import pyautogui
import base64
from io import BytesIO

is_on = False

def screen_shooter_is_on():
    return is_on

def screen_shooter_start():
    global is_on
    is_on = True

def screen_shooter_stop():
    global is_on
    is_on = False
    
def screen_shooter_toggle():
    global is_on
    is_on = not is_on
    
def take_screenshot() -> bytes:
    screenshot = pyautogui.screenshot()

    buffer = BytesIO()
    screenshot.save(buffer, format="PNG")

    return buffer.getvalue()