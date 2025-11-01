# src/desktop_agent/decision/grounding.py
from __future__ import annotations
from typing import Dict, Any
import requests


class GroundingModel:
    """封装 UI-TARS / 任意自定义 grounding 端点"""

    def __init__(
        self,
        url: str,
        model: str,
        api_key: str | None = None,
        width: int = 1920,
        height: int = 1080,
    ):
        self.url = url.rstrip("/")
        self.model = model
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self.width = width
        self.height = height

    def predict(self, screenshot_bytes: bytes) -> Dict[str, Any]:
        """返回 grounding JSON（坐标、元素、置信度等）"""
        files = {"image": ("screenshot.png", screenshot_bytes, "image/png")}
        data = {
            "model": self.model,
            "width": str(self.width),
            "height": str(self.height),
        }
        resp = requests.post(f"{self.url}/predict", files=files, data=data, headers=self.headers)
        resp.raise_for_status()
        return resp.json()