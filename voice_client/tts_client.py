import threading
from queue import Queue

import requests
import pyaudio

KOKORO_URL = "http://127.0.0.1:8880"
KOKORO_VOICE = "af_heart"

stop_speaking = threading.Event()
tts_queue = Queue()

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
        
