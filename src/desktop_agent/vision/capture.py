# src/desktop_agent/vision/capture.py
import io
from PIL import Image
import pyautogui
from typing import Tuple

def capture_screen(
    target_width: int = 1920,
    target_height: int = 1080,
) -> Tuple[bytes, Tuple[int, int]]:
    """
    捕获主屏幕并缩放到目标分辨率（供 Grounding 模型使用）
    """
    screen = pyautogui.screenshot()
    if screen.size != (target_width, target_height):
        screen = screen.resize((target_width, target_height), Image.LANCZOS)
    
    buffer = io.BytesIO()
    screen.save(buffer, format="PNG")
    return buffer.getvalue(), (target_width, target_height)