# src/desktop_agent/execution/executor.py
import pyautogui
import subprocess
import logging
from typing import Optional
from ..config import Config
from ..types import Action, ElementMap

logger = logging.getLogger(__name__)

class Executor:
    """执行器：将动作序列转换为实际的桌面操作"""
    
    def __init__(self, enable_local_code: bool = False, config: Optional[Config] = None):
        """
        Args:
            enable_local_code: 是否启用本地代码执行（安全风险）
            config: 配置对象（可选）
        """
        self.enable_local_code = enable_local_code or (config and config.enable_local_code if config else False)
        if self.enable_local_code:
            logger.warning("⚠️  已启用本地代码执行，存在安全风险！")

    def execute(self, actions: list[Action], element_map: ElementMap) -> None:
        """
        执行动作序列
        
        Args:
            actions: 动作列表
            element_map: 元素 ID 到边界框的映射
        
        Raises:
            KeyError: 动作引用了不存在的 element_id
            ValueError: 动作格式错误
            RuntimeError: 执行失败
        """
        if not actions:
            logger.info("没有需要执行的动作")
            return
        
        logger.info(f"开始执行 {len(actions)} 个动作")
        
        for i, act in enumerate(actions):
            try:
                typ = act.get("type")
                if not typ:
                    raise ValueError(f"动作 {i+1} 缺少 'type' 字段")
                
                logger.debug(f"执行动作 {i+1}/{len(actions)}: {typ}")
                
                if typ == "click":
                    self._execute_click(act, element_map)
                elif typ == "type":
                    self._execute_type(act, element_map)
                elif typ == "press":
                    self._execute_press(act)
                elif typ == "code":
                    self._execute_code(act)
                else:
                    raise ValueError(f"不支持的动作类型: {typ}")
            except Exception as e:
                logger.error(f"执行动作 {i+1} 失败: {e}")
                raise RuntimeError(f"执行动作 {i+1} 失败: {e}") from e

    def _execute_click(self, action: Action, element_map: ElementMap) -> None:
        """执行点击动作"""
        element_id = action.get("element_id")
        if element_id is None:
            raise ValueError("click 动作缺少 'element_id'")
        if element_id not in element_map:
            raise KeyError(f"element_id {element_id} 不存在于 element_map")
        
        x, y = self._center(element_map[element_id])
        pyautogui.click(x, y)
        logger.debug(f"点击位置: ({x}, {y})")

    def _execute_type(self, action: Action, element_map: ElementMap) -> None:
        """执行输入文本动作"""
        element_id = action.get("element_id")
        text = action.get("text", "")
        
        if element_id is None:
            raise ValueError("type 动作缺少 'element_id'")
        if element_id not in element_map:
            raise KeyError(f"element_id {element_id} 不存在于 element_map")
        
        x, y = self._center(element_map[element_id])
        pyautogui.click(x, y)
        pyautogui.write(text)
        logger.debug(f"在元素 {element_id} 输入文本: {text[:50]}...")

    def _execute_press(self, action: Action) -> None:
        """执行按键动作"""
        key = action.get("key")
        if not key:
            raise ValueError("press 动作缺少 'key'")
        
        pyautogui.press(key)
        logger.debug(f"按键: {key}")

    def _execute_code(self, action: Action) -> None:
        """执行代码动作"""
        if not self.enable_local_code:
            raise RuntimeError("代码执行未启用（安全考虑），需要设置 enable_local_code=True")
        
        lang = action.get("language")
        code = action.get("code")
        
        if not lang or not code:
            raise ValueError("code 动作缺少 'language' 或 'code'")
        
        logger.warning(f"⚠️  执行 {lang} 代码: {code[:100]}...")
        self._run_code(lang, code)

    def _center(self, bbox: tuple) -> Tuple[int, int]:
        """
        计算边界框的中心点
        
        Args:
            bbox: (x1, y1, x2, y2) 格式的边界框
        
        Returns:
            (x, y) 中心点坐标
        """
        if len(bbox) != 4:
            raise ValueError(f"边界框格式错误，应为 (x1, y1, x2, y2)，得到: {bbox}")
        
        x1, y1, x2, y2 = bbox
        return (x1 + x2) // 2, (y1 + y2) // 2

    def _run_code(self, lang: str, code: str) -> None:
        """
        运行代码
        
        Args:
            lang: 编程语言
            code: 代码内容
        
        Raises:
            ValueError: 不支持的编程语言
            subprocess.TimeoutExpired: 代码执行超时
            subprocess.CalledProcessError: 代码执行失败
        """
        if lang == "python":
            try:
                result = subprocess.run(
                    ["python", "-c", code],
                    timeout=10,
                    capture_output=True,
                    text=True,
                    check=True
                )
                if result.stdout:
                    logger.info(f"代码输出: {result.stdout}")
            except subprocess.TimeoutExpired:
                raise RuntimeError("代码执行超时（10秒）")
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"代码执行失败: {e.stderr}")
        else:
            raise ValueError(f"不支持的编程语言: {lang}")