"""
Desktop Agent - 桌面自动化代理

主要组件：
- DesktopAgent: 高层统一接口（推荐使用）
- VisionGrounder: 视觉感知（截图和 UI 元素识别）
- DecisionAgent: 决策代理（LLM 生成动作序列）
- Executor: 执行器（执行动作序列）
- Config: 配置管理
"""

from .agent import DesktopAgent
from .vision.grounding import VisionGrounder
from .vision.capture import capture_screenshot
from .decision.agent import DecisionAgent
from .execution.executor import Executor
from .config import Config, config

__version__ = "0.1.0"
__all__ = [
    "DesktopAgent",
    "VisionGrounder",
    "capture_screenshot",
    "DecisionAgent",
    "Executor",
    "Config",
    "config",
]

