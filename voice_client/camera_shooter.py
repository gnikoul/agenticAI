import cv2

is_on = False

def camera_is_on():
    return is_on

def camera_start():
    global is_on
    is_on = True

def camera_stop():
    global is_on
    is_on = False

def camera_toggle():
    global is_on
    is_on = not is_on

def take_camera_photo() -> bytes:
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        raise RuntimeError("Could not open camera")

    success, frame = camera.read()
    camera.release()

    if not success:
        raise RuntimeError("Could not capture frame")

    success, buffer = cv2.imencode(".png", frame)

    if not success:
        raise RuntimeError("Could not encode camera image")

    return buffer.tobytes()