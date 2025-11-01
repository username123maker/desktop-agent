# src/desktop_agent/decision/agent.py
import json
import os
from typing import Optional, Literal, Tuple, List
from openai import OpenAI
from ..types import VisionData, Action
from ..config import Config

# 可选依赖的条件导入
try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

class DecisionAgent:
    """决策代理：使用 LLM 将用户指令和视觉感知转换为动作序列"""
    
    def __init__(
        self,
        provider: Literal["openai", "anthropic", "gemini", "vllm"] = "openai",
        model: str = "gpt-4o",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        config: Optional[Config] = None
    ):
        """
        Args:
            provider: LLM 提供商
            model: 模型名称
            api_key: API 密钥（如未提供则从环境变量读取）
            base_url: API 基础 URL（用于 vLLM 等）
            config: 配置对象（可选）
        """
        self.provider = provider
        self.model = model
        self.config = config
        
        # 获取 API 密钥
        if api_key is None:
            if provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
            elif provider == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY")
            elif provider == "gemini":
                api_key = os.getenv("GEMINI_API_KEY")
        
        # 初始化客户端
        if provider == "openai" or provider == "vllm":
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        elif provider == "anthropic":
            if Anthropic is None:
                raise ImportError("请安装 anthropic 库: pip install anthropic")
            self.client = Anthropic(api_key=api_key)
        elif provider == "gemini":
            if genai is None:
                raise ImportError("请安装 google-generativeai 库: pip install google-generativeai")
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(model)
        else:
            raise ValueError(f"不支持的 provider: {provider}")

    def decide(
        self,
        instruction: str,
        vision_data: VisionData
    ) -> List[Action]:
        """
        输入：用户指令 + 视觉数据
        输出：动作序列
        
        Args:
            instruction: 用户指令
            vision_data: 视觉感知数据
        
        Returns:
            动作序列列表
        
        Raises:
            Exception: API 调用失败时抛出
        """
        try:
            # 构建 prompt
            prompt = self._build_prompt(instruction, vision_data)
            
            # 调用 LLM
            if self.provider == "openai" or self.provider == "vllm":
                response = self._call_openai(prompt)
            elif self.provider == "anthropic":
                response = self._call_anthropic(prompt)
            elif self.provider == "gemini":
                response = self._call_gemini(prompt)
            else:
                raise ValueError(f"不支持的 provider: {self.provider}")
            
            # 解析响应
            if isinstance(response, str):
                result = json.loads(response)
            else:
                result = response
            
            actions = result.get("actions", [])
            return actions
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM 返回的 JSON 格式错误: {e}") from e
        except Exception as e:
            raise RuntimeError(f"决策失败: {e}") from e
    
    def _build_prompt(self, instruction: str, vision_data: VisionData) -> Tuple[str, str]:
        """构建完整的 prompt"""
        system_prompt = self._system_prompt()
        user_prompt = f"""Task: {instruction}

UI Elements:
{json.dumps(vision_data, indent=2, ensure_ascii=False)}

请根据以上 UI 元素和任务要求，输出一个 JSON 对象，包含一个 "actions" 数组。
每个动作应该是以下格式之一：
- {{"type": "click", "element_id": 1}}
- {{"type": "type", "element_id": 2, "text": "要输入的文本"}}
- {{"type": "press", "key": "enter"}}
- {{"type": "code", "language": "python", "code": "代码内容"}}
"""
        return system_prompt, user_prompt
    
    def _call_openai(self, prompt: Tuple[str, str]) -> str:
        """调用 OpenAI API"""
        system_prompt, user_prompt = prompt
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        return resp.choices[0].message.content
    
    def _call_anthropic(self, prompt: Tuple[str, str]) -> str:
        """调用 Anthropic API"""
        system_prompt, user_prompt = prompt
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return resp.content[0].text
    
    def _call_gemini(self, prompt: Tuple[str, str]) -> str:
        """调用 Gemini API"""
        system_prompt, user_prompt = prompt
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        resp = self.client.generate_content(
            full_prompt,
            generation_config={
                "temperature": 0.0,
                "response_mime_type": "application/json"
            }
        )
        return resp.text
    
    def _system_prompt(self) -> str:
        """系统提示词"""
        return """You are a desktop automation agent. Given a user task and UI elements with bounding boxes,
output a JSON object with an "actions" array to complete the task.

Available actions:
- click(element_id): Click on an element
- type(element_id, text): Type text into an element
- press(key): Press a keyboard key (e.g., "enter", "tab", "escape")
- code(language, code): Execute code (use with caution)

Use element_id from the UI elements list. Be precise and follow the task step by step."""