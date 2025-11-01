# src/desktop_agent/config.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
import os
from dotenv import load_dotenv

# 自动加载 .env
load_dotenv()

@dataclass
class Config:
    # 主模型
    provider: Literal["openai", "anthropic", "gemini", "vllm"] = os.getenv("PROVIDER", "openai")
    model: str = os.getenv("MAIN_MODEL", "gpt-4o")

    # Grounding 模型
    grounding_url: str = os.getenv("GROUNDING_URL", "http://localhost:8080")
    grounding_model: str = os.getenv("GROUNDING_MODEL", "ui-tars-1.5-7b")
    grounding_api_key: str | None = os.getenv("GROUNDING_API_KEY")
    grounding_width: int = int(os.getenv("GROUNDING_WIDTH", "1920"))
    grounding_height: int = int(os.getenv("GROUNDING_HEIGHT", "1080"))

    # 安全控制
    enable_local_code: bool = os.getenv("ENABLE_LOCAL_CODE", "false").lower() == "true"

    @classmethod
    def from_env(cls) -> "Config":
        return cls()

# 全局配置实例
config = Config.from_env()