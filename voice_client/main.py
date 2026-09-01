import threading
import time
from concurrent.futures import ThreadPoolExecutor

import soundfile as sf

from pynput import keyboard

from stt_client import stt
from tts_client import speak, stop_speaking, tts_queue, tts_worker
from voice_recorder import start_recording, stop_recording, is_recording, get_audio_data
from agent_client import send_to_agent_and_put_to_tts_queue, get_ollama_response
from screen_shooter import take_screenshot, screen_shooter_is_on, screen_shooter_stop, screen_shooter_start, screen_shooter_toggle


def transcribe_and_send():
    start = time.perf_counter()
    audio_data = get_audio_data()
    if not audio_data:
        return

    # Combine recorded chunks
    audio = b"".join(chunk.tobytes() for chunk in audio_data)

    print("🧠 Transcribing...", end='')
    segments = stt(audio)


    text = " ".join(segment.text for segment in segments).strip()

    if not text:
        print("No speech detected.")
        return

    elapsed = time.perf_counter() - start
    print(f"({elapsed:.1f}s)")
    print(f"📝 You: {text}")

    send_to_agent_and_put_to_tts_queue(text, tts_queue)

def interrupt_speaking():
    stop_speaking.set()
    
    ollama_response = get_ollama_response()

    if ollama_response is not None:
        ollama_response.close()
        ollama_response = None
        
    while not tts_queue.empty():
        try:
            tts_queue.get_nowait()
            tts_queue.task_done()
        except:
            break
        
print("Hold F2 to speak.")
        
tts_thread = threading.Thread(
    target=tts_worker,
    daemon=True
)
tts_thread.start()

# =========================
# Events
# =========================

def on_press(key):

    if key == keyboard.Key.f2:
        interrupt_speaking()
        start_recording()


def on_release(key):
    if key == keyboard.Key.f2:
        if is_recording():
            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(stop_recording)
            future.add_done_callback(lambda future: transcribe_and_send())
            
    elif key == keyboard.Key.f3:
        screen_shooter_toggle()
        if screen_shooter_is_on():
            speak('Screen capture: on!')
        else:
            speak('Screen capture: off!')
            

    elif key == keyboard.Key.esc:
        
        stop_speaking.set()
        print("\nShutting down...")
        return False


with keyboard.Listener(
    on_press=on_press,
    on_release=on_release
) as listener:

    listener.join()