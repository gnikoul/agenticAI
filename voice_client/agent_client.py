import time
import json

import requests

from screen_shooter import screen_shooter_is_on, take_screenshot

BACKEND_URL = "http://127.0.0.1:5000"
ollama_response = None

def get_ollama_response():
    return ollama_response
def send_to_agent_and_put_to_tts_queue(text, tts_queue):
    print("🤖 Waiting for agent...", end='')
    start = time.perf_counter()
    first_queue = True
    
    screenshot = None
    if screen_shooter_is_on():
        screenshot = take_screenshot()

    global ollama_response
    ollama_response = requests.post(
        f"{BACKEND_URL}/agent/send_message",
        data={"message": text},
        files={
            "image": ("screenshot.webp", screenshot, "image/webp")
        },
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