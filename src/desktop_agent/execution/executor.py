# src/desktop_agent/execution/executor.py
import pyautogui
import subprocess
from typing import List, Dict

class Executor:
    def __init__(self, enable_code=False):
        self.enable_code = enable_code

    def execute(self, actions: List[Dict], element_map: Dict[int, tuple]):
        for act in actions:
            typ = act["type"]
            if typ == "click":
                x, y = self._center(element_map[act["element_id"]])
                pyautogui.click(x, y)
            elif typ == "type":
                x, y = self._center(element_map[act["element_id"]])
                pyautogui.click(x, y)
                pyautogui.write(act["text"])
            elif typ == "press":
                pyautogui.press(act["key"])
            elif typ == "code" and self.enable_code:
                self._run_code(act["language"], act["code"])

    def _center(self, bbox):
        x1, y1, x2, y2 = bbox
        return (x1 + x2) // 2, (y1 + y2) // 2

    def _run_code(self, lang, code):
        if lang == "python":
            subprocess.run(["python", "-c", code], timeout=10)