"""
简单示例：展示如何使用 Desktop Agent 完成自动化任务（低层 API）
"""
from desktop_agent import VisionGrounder, DecisionAgent, Executor

# 1. 视觉感知
grounder = VisionGrounder(
    url="http://localhost:8080",
    model="ui-tars-1.5-7b",
    width=1920,
    height=1080
)

# 2. 决策
decision_agent = DecisionAgent(provider="openai", model="gpt-4o")

# 3. 执行
executor = Executor(enable_local_code=True)

# 主流程
instruction = "打开记事本，输入 'Hello World' 并保存"

# 步骤 1: 视觉感知
vision_data = grounder.perceive(instruction)

# 步骤 2: 决策（现在只需要传入 vision_data，不需要 grounder）
actions = decision_agent.decide(instruction, vision_data)

# 步骤 3: 构建 element_map 并执行
element_map = VisionGrounder.build_element_map(vision_data)
executor.execute(actions, element_map)

print(f"✅ 完成！执行了 {len(actions)} 个动作")