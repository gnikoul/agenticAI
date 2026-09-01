import threading
import os, sys
import requests
import json
from queue import Queue
import time

import sounddevice as sd
import soundfile as sf
import pyaudio

from pynput import keyboard
if sys.platform == "win32":
    nvidia_path = os.path.join(
        sys.prefix,
        "Lib",
        "site-packages",
        "nvidia"
    )

    cublas_bin = os.path.join(nvidia_path, "cublas", "bin")
    cudnn_bin = os.path.join(nvidia_path, "cudnn", "bin")

    os.add_dll_directory(cublas_bin)
    os.add_dll_directory(cudnn_bin)

    os.environ["PATH"] = (
        cublas_bin
        + os.pathsep
        + cudnn_bin
        + os.pathsep
        + os.environ["PATH"]
    )
from faster_whisper import WhisperModel


BACKEND_URL = "http://127.0.0.1:5000"
KOKORO_URL = "http://127.0.0.1:8880"

SAMPLE_RATE = 16000
CHANNELS = 1

WHISPER_MODEL = "medium"
KOKORO_VOICE = "af_heart"

tts_queue = Queue()


print("Loading Whisper...")

whisper = WhisperModel(
    WHISPER_MODEL,
    device="cuda",
    compute_type="int8_float16"
)

print("Whisper ready.")
print("Hold F2 to speak.")


recording = False
audio_data = []
ollama_response = None


def audio_callback(indata, frames, time, status):
    if status:
        print(status)

    audio_data.append(indata.copy())


stream = None


def start_recording():
    global recording
    global audio_data
    global stream

    if recording:
        return

    audio_data = []
    recording = True

    print("🎤 Listening...")

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
        callback=audio_callback
    )

    stream.start()


def stop_recording():
    global recording
    global stream

    if not recording:
        return

    recording = False

    print("🛑 Recording stopped.")

    stream.stop()
    stream.close()

    stream = None

    transcribe_and_send()


def transcribe_and_send():
    start = time.perf_counter()
    if not audio_data:
        return

    # Combine recorded chunks
    audio = b"".join(chunk.tobytes() for chunk in audio_data)

    # Convert bytes back to numpy array
    import numpy as np

    audio_array = np.frombuffer(
        audio,
        dtype=np.float32
    )

    print("🧠 Transcribing...", end='')

    segments, info = whisper.transcribe(
        audio_array,
        language="en"
    )

    text = " ".join(segment.text for segment in segments).strip()

    if not text:
        print("No speech detected.")
        return

    elapsed = time.perf_counter() - start
    print(f"({elapsed:.1f}s)")
    print(f"📝 You: {text}")

    send_to_agent(text)


def send_to_agent(text):
    print("🤖 Waiting for agent...", end='')
    first_queue = True

    global ollama_response
    ollama_response = requests.post(
        f"{BACKEND_URL}/agent/send_message",
        data={"message": text},
        stream=True
    )

    response = ollama_response
    response.raise_for_status()

    decoder = json.JSONDecoder()
    buffer = ""
    sentence_buffer = ""

    try:
        for chunk in response.iter_content():
            buffer += chunk.decode("utf-8")

            while buffer:
                try:
                    data, index = decoder.raw_decode(buffer)
                except json.JSONDecodeError:
                    break

                buffer = buffer[index:]

                if data["state"] != "content":
                    continue

                sentence_buffer += data["message"]

                if sentence_buffer.rstrip().endswith((".", "!", "?", "\n", ":")):
                    sentence = sentence_buffer.strip()
                    if first_queue:
                        first_queue = False
                        elapsed = time.perf_counter() - start
                        print(f"({elapsed:.1f}s)")
                    print(f"🔊 Queueing: {sentence}")
                    tts_queue.put(sentence)

                    # IMPORTANT
                    sentence_buffer = ""

    except (requests.exceptions.RequestException, AttributeError):
        print("🤖 Ollama request interrupted.")

    finally:
        response.close()
        ollama_response = None

    # Handle text that didn't end with punctuation
    if sentence_buffer.strip():
        sentence = sentence_buffer.strip()

        print(f"🔊 Queueing: {sentence}")
        tts_queue.put(sentence)

stop_speaking = threading.Event()
def speak(text):
    print("🔊 Speaking...")


    response = requests.post(
        f"{KOKORO_URL}/v1/audio/speech",
        json={
            "model": "kokoro",
            "input": text,
            "voice": KOKORO_VOICE,
            "response_format": "pcm",
            "speed": 1.0
        },
        stream=True
    )

    response.raise_for_status()

    player = pyaudio.PyAudio()

    stream = player.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=24000,
        output=True
    )

    try:
        for chunk in response.iter_content(chunk_size=4096):
            if stop_speaking.is_set():
                break

            if chunk:
                stream.write(chunk)

    finally:
        stream.stop_stream()
        stream.close()
        player.terminate()

        response.close()

    print("🔊 Stopped.")

    
def tts_worker():
    while True:
        text = tts_queue.get()

        if text is None:
            break

        stop_speaking.clear()
        speak(text)

        tts_queue.task_done()


tts_thread = threading.Thread(
    target=tts_worker,
    daemon=True
)

tts_thread.start()

def interrupt_speaking():
    stop_speaking.set()

    global ollama_response
    
    if ollama_response is not None:
        ollama_response.close()
        ollama_response = None
        
    while not tts_queue.empty():
        try:
            tts_queue.get_nowait()
            tts_queue.task_done()
        except:
            break
        
# =========================
# F2 keyboard handling
# =========================

def on_press(key):

    if key == keyboard.Key.f2:
        interrupt_speaking()
        start_recording()


def on_release(key):

    if key == keyboard.Key.f2:
        if recording:
            threading.Thread(
                target=stop_recording,
                daemon=True
            ).start()

    elif key == keyboard.Key.esc:
        stop_speaking.set()
        print("\nShutting down...")
        return False


with keyboard.Listener(
    on_press=on_press,
    on_release=on_release
) as listener:

    listener.join()