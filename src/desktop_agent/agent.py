"""
高层 DesktopAgent 类：统一管理整个桌面自动化流程
"""
import logging
from typing import Optional
from .vision.grounding import VisionGrounder
from .decision.agent import DecisionAgent
from .execution.executor import Executor
from .config import Config, config
from .types import VisionData, Action, ElementMap

logger = logging.getLogger(__name__)


class DesktopAgent:
    """
    桌面自动化代理
    
    封装完整的桌面自动化流程：
    1. 视觉感知（截图 + UI 元素识别）
    2. 决策（LLM 生成动作序列）
    3. 执行（执行动作序列）
    """
    
    def __init__(
        self,
        grounder: Optional[VisionGrounder] = None,
        decision_agent: Optional[DecisionAgent] = None,
        executor: Optional[Executor] = None,
        config_instance: Optional[Config] = None,
    ):
        """
        Args:
            grounder: 视觉感知器（如未提供则使用 config 创建）
            decision_agent: 决策代理（如未提供则使用 config 创建）
            executor: 执行器（如未提供则使用 config 创建）
            config_instance: 配置对象（默认使用全局 config）
        """
        self.config = config_instance or config
        
        # 初始化组件
        self.grounder = grounder or VisionGrounder(config=self.config)
        self.decision_agent = decision_agent or DecisionAgent(
            provider=self.config.provider,
            model=self.config.model,
            config=self.config
        )
        self.executor = executor or Executor(
            enable_local_code=self.config.enable_local_code,
            config=self.config
        )
    
    def run(self, instruction: str) -> tuple[list[Action], VisionData]:
        """
        执行完整的桌面自动化流程
        
        Args:
            instruction: 用户指令
        
        Returns:
            (动作序列, 视觉数据)
        
        Raises:
            RuntimeError: 执行失败时抛出
        """
        logger.info(f"开始执行任务: {instruction}")
        
        try:
            # 1. 视觉感知
            logger.debug("步骤 1: 视觉感知")
            vision_data = self.grounder.perceive(instruction)
            logger.info(f"识别到 {len(vision_data['elements'])} 个 UI 元素")
            
            # 2. 决策
            logger.debug("步骤 2: 决策生成")
            actions = self.decision_agent.decide(instruction, vision_data)
            logger.info(f"生成 {len(actions)} 个动作")
            
            # 3. 执行
            logger.debug("步骤 3: 执行动作")
            element_map = VisionGrounder.build_element_map(vision_data)
            self.executor.execute(actions, element_map)
            
            logger.info(f"✅ 任务完成！执行了 {len(actions)} 个动作")
            return actions, vision_data
            
        except Exception as e:
            logger.error(f"任务执行失败: {e}")
            raise RuntimeError(f"桌面自动化任务失败: {e}") from e
    
    def perceive(self, instruction: Optional[str] = None) -> VisionData:
        """
        仅执行视觉感知（不执行决策和执行）
        
        Args:
            instruction: 可选的用户指令
        
        Returns:
            视觉数据
        """
        return self.grounder.perceive(instruction)
    
    def decide(
        self,
        instruction: str,
        vision_data: Optional[VisionData] = None
    ) -> list[Action]:
        """
        执行决策（需要先有视觉数据）
        
        Args:
            instruction: 用户指令
            vision_data: 视觉数据（如未提供则自动感知）
        
        Returns:
            动作序列
        """
        if vision_data is None:
            vision_data = self.grounder.perceive(instruction)
        return self.decision_agent.decide(instruction, vision_data)
    
    def execute(
        self,
        actions: list[Action],
        vision_data: Optional[VisionData] = None,
        element_map: Optional[ElementMap] = None
    ) -> None:
        """
        仅执行动作序列
        
        Args:
            actions: 动作序列
            vision_data: 视觉数据（用于构建 element_map）
            element_map: 元素映射（优先级高于 vision_data）
        """
        if element_map is None:
            if vision_data is None:
                raise ValueError("需要提供 vision_data 或 element_map")
            element_map = VisionGrounder.build_element_map(vision_data)
        
        self.executor.execute(actions, element_map)

