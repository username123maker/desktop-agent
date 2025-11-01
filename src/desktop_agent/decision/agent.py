# src/desktop_agent/decision/agent.py
import json
from openai import OpenAI
from ..vision.grounding import VisionGrounder

class DecisionAgent:
    def __init__(self, provider="openai", model="gpt-4o", api_key=None, base_url=None):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def decide(
        self,
        instruction: str,
        grounder: VisionGrounder
    ) -> list[dict]:
        """
        输入：用户指令 + 视觉感知
        输出：动作序列
        """
        vision_data = grounder.perceive(instruction)
        
        messages = [
            {"role": "system", "content": self._system_prompt()},
            {"role": "user", "content": [
                {"type": "text", "text": f"Task: {instruction}"},
                {"type": "text", "text": f"UI Elements:\n{json.dumps(vision_data, indent=2)}"}
            ]}
        ]

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.0
        )
        
        result = json.loads(resp.choices[0].message.content)
        return result.get("actions", [])
    
    def _system_prompt(self):
        return """
        You are a desktop automation agent. Given a user task and UI elements with bounding boxes,
        output a JSON array of actions to complete the task.
        
        Available actions:
        - click(element_id)
        - type(text, element_id)
        - press(key)
        - code(language, code)
        
        Use element_id from the UI elements list. Be precise.
        """