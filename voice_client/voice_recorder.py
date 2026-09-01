import sounddevice as sd

SAMPLE_RATE = 16000
CHANNELS = 1

stream = None
recording = False
audio_data = []

def audio_callback(indata, frames, time, status):
    if status:
        print(status)

    audio_data.append(indata.copy())
    
def get_audio_data():
    return audio_data

def is_recording():
    return recording

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
