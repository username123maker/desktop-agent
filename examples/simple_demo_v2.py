"""
简单示例 v2：使用高层 DesktopAgent 接口（推荐）
"""
from desktop_agent import DesktopAgent

# 创建桌面代理（使用默认配置）
agent = DesktopAgent()

# 执行任务（一行代码完成所有流程）
instruction = "打开记事本，输入 'Hello World' 并保存"
actions, vision_data = agent.run(instruction)

print(f"✅ 完成！执行了 {len(actions)} 个动作")
print(f"识别到 {len(vision_data['elements'])} 个 UI 元素")

