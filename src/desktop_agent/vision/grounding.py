# src/desktop_agent/vision/grounding.py
import requests
from typing import Dict, Any
from .capture import capture_screen

class VisionGrounder:
    """
    负责：截图 → 调用 UI-TARS 等模型 → 返回结构化视觉理解
    输出示例：
    {
      "elements": [
        {"id": 1, "bbox": [100, 200, 300, 250], "text": "File", "type": "button"},
        {"id": 2, "bbox": [400, 400, 800, 600], "text": "", "type": "text_field"}
      ],
      "resolution": [1920, 1080]
    }
    """
    
    def __init__(
        self,
        url: str,
        model: str = "ui-tars-1.5-7b",
        api_key: str | None = None,
        width: int = 1920,
        height: int = 1080,
    ):
        self.url = url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.width = width
        self.height = height
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    def perceive(self, instruction: str | None = None) -> Dict[str, Any]:
        """
        完整流程：截图 → 发送 → 解析
        """
        screenshot_bytes, _ = capture_screen(self.width, self.height)
        
        files = {"image": ("screen.png", screenshot_bytes, "image/png")}
        data = {
            "model": self.model,
            "width": str(self.width),
            "height": str(self.height),
            "instruction": instruction or "Describe all UI elements with bounding boxes and text."
        }
        
        resp = requests.post(
            f"{self.url}/ground",
            files=files,
            data=data,
            headers=self.headers,
            timeout=30
        )
        resp.raise_for_status()
        return resp.json()