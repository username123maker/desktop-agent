from desktop_agent.vision.grounding import VisionGrounder
from desktop_agent.decision.agent import DecisionAgent
from desktop_agent.execution.executor import Executor

# 1. 视觉感知
grounder = VisionGrounder(
    url="http://localhost:8080",
    model="ui-tars-1.5-7b",
    width=1920, height=1080
)

# 2. 决策
agent = DecisionAgent(model="gpt-4o")

# 3. 执行
executor = Executor(enable_code=True)

# 主流程
instruction = "打开记事本，输入 'Hello World' 并保存"
actions = agent.decide(instruction, grounder)

# 构建 element_map（从 grounder.perceive() 拿）
vision = grounder.perceive()
element_map = {e["id"]: e["bbox"] for e in vision["elements"]}

executor.execute(actions, element_map)