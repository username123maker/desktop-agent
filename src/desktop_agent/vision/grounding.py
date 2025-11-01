# src/desktop_agent/vision/grounding.py
import requests
from typing import Dict, Any, Optional
from .capture import capture_screenshot
from ..types import VisionData, ElementMap, UIElement
from ..config import Config

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
        url: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        config: Optional[Config] = None,
    ):
        """
        Args:
            url: Grounding 模型 URL
            model: Grounding 模型名称
            api_key: API 密钥
            width: 截图宽度
            height: 截图高度
            config: 配置对象（优先级高于单独参数）
        """
        if config:
            self.url = url or config.grounding_url
            self.model = model or config.grounding_model
            self.api_key = api_key or config.grounding_api_key
            self.width = width if width is not None else config.grounding_width
            self.height = height if height is not None else config.grounding_height
        else:
            self.url = (url or "http://localhost:8080").rstrip("/")
            self.model = model or "ui-tars-1.5-7b"
            self.api_key = api_key
            self.width = width or 1920
            self.height = height or 1080
        
        self.headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    def perceive(self, instruction: Optional[str] = None) -> VisionData:
        """
        完整流程：截图 → 发送 → 解析
        
        Args:
            instruction: 可选的用户指令，用于指导模型关注特定区域
        
        Returns:
            视觉数据（包含 elements 和 resolution）
        
        Raises:
            requests.RequestException: API 请求失败时抛出
        """
        try:
            screenshot_bytes, _ = capture_screenshot(self.width, self.height)
            
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
        except requests.RequestException as e:
            raise RuntimeError(f"Grounding API 请求失败: {e}") from e
    
    @staticmethod
    def build_element_map(vision_data: VisionData) -> ElementMap:
        """
        从视觉数据构建元素映射
        
        Args:
            vision_data: 视觉感知数据
        
        Returns:
            element_id -> bbox 的映射字典
        """
        return {element["id"]: tuple(element["bbox"]) for element in vision_data["elements"]}