import os, sys

import numpy as np
print("Loading Whisper...")

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

print("Whisper ready.")


WHISPER_MODEL = "medium"

whisper = WhisperModel(
    WHISPER_MODEL,
    device="cuda",
    compute_type="int8_float16"
)

def stt(audio):
    audio_array = np.frombuffer(
        audio,
        dtype=np.float32
    )
    
    segments, info = whisper.transcribe(
        audio_array,
        language="en"
    )
    
    return segments