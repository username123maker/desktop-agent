# Desktop Agent



## 安装

> 开发模式（可修改源码）：
```bash
git clone https://github.com/yourname/desktop-agent.git
cd desktop-agent
pip install -e .
```

### 依赖

**必需依赖：**
- `pyautogui`：鼠标键盘控制
- `Pillow`：图像处理
- `requests`：调用 grounding 模型
- `openai`：主决策模型
- `python-dotenv`：环境变量管理

**可选依赖：**
- `anthropic`：Anthropic Claude 支持（`pip install -e .[anthropic]`）
- `google-generativeai`：Google Gemini 支持（`pip install -e .[gemini]`）
- 安装所有可选依赖：`pip install -e .[all]`

---

## 快速开始

### 1. 配置 API 密钥

```bash
export OPENAI_API_KEY="sk-..."
# 可选：Anthropic / Gemini / HF
export ANTHROPIC_API_KEY="..."
export HF_TOKEN="..."
```

### 2. 启动本地 Grounding 模型（推荐 UI-TARS-1.5-7B）

使用 vLLM 部署：
```bash
vllm serve ui-tars-1.5-7b --port 8080 --dtype float16
```

### 3. 运行示例

#### 方式一：使用高层 DesktopAgent API（推荐）

```python
# examples/simple_demo_v2.py
from desktop_agent import DesktopAgent

# 创建桌面代理（自动使用配置）
agent = DesktopAgent()

# 一行代码完成所有流程
instruction = "打开记事本，输入 'Hello Desktop Agent' 并保存为 demo.txt"
actions, vision_data = agent.run(instruction)
```

#### 方式二：使用低层组件 API（更灵活）

```python
# examples/simple_demo.py
from desktop_agent import VisionGrounder, DecisionAgent, Executor

# 1. 视觉感知
grounder = VisionGrounder(
    url="http://localhost:8080",
    model="ui-tars-1.5-7b",
    width=1920,
    height=1080
)

# 2. 决策模型
decision_agent = DecisionAgent(provider="openai", model="gpt-4o")

# 3. 执行器
executor = Executor(enable_local_code=True)

# 4. 执行任务
instruction = "打开记事本，输入 'Hello Desktop Agent' 并保存为 demo.txt"

# 步骤 1: 视觉感知
vision_data = grounder.perceive(instruction)

# 步骤 2: 决策
actions = decision_agent.decide(instruction, vision_data)

# 步骤 3: 构建 element_map 并执行
from desktop_agent import VisionGrounder
element_map = VisionGrounder.build_element_map(vision_data)
executor.execute(actions, element_map)
```

```bash
# 使用高层 API
python examples/simple_demo_v2.py

# 或使用低层 API
python examples/simple_demo.py
```

---

## 模块详解

## 模块架构

```text
┌─────────────────┐
│   用户指令       │
└───────┬─────────┘
        ↓
┌───────┴────────┐
│  VisionGrounder │ → 截图 + UI-TARS → 元素坐标
└───────┬────────┘
        ↓
┌───────┴────────┐
│  DecisionAgent │ → LLM 推理 → 动作序列
└───────┬────────┘
        ↓
┌───────┴────────┐
│    Executor    │ → pyautogui + 代码执行
└────────────────┘
```

---

## 支持的动作类型

| 类型 | 示例 |
|------|------|
| `click` | `{"type": "click", "element_id": 1}` |
| `type` | `{"type": "type", "element_id": 2, "text": "Hello"}` |
| `press` | `{"type": "press", "key": "enter"}` |
| `code` | `{"type": "code", "language": "python", "code": "print(42)"}` |

> `code` 动作需启用 `enable_local_code=True`（存在安全风险）

---

## 配置

可以通过环境变量或 `Config` 类进行配置：

```python
from desktop_agent import Config, config

# 使用全局配置
print(config.provider)  # "openai"
print(config.model)     # "gpt-4o"

# 或创建自定义配置
custom_config = Config.from_env()
```

环境变量：
- `PROVIDER`: LLM 提供商 (openai/anthropic/gemini/vllm)
- `MAIN_MODEL`: 主模型名称
- `GROUNDING_URL`: Grounding 模型 URL
- `GROUNDING_MODEL`: Grounding 模型名称
- `ENABLE_LOCAL_CODE`: 是否启用本地代码执行 (true/false)

## 安全提示

- **本地代码执行** 会以当前用户权限运行任意代码
- 仅在 **可信任务** 和 **隔离环境** 中启用
- 建议使用 **Docker 沙箱** 或 **虚拟机** 运行
- 默认禁用代码执行，需显式设置 `enable_local_code=True`

---

## 开发

```bash
# 安装开发依赖
pip install -e .[dev]

# 运行测试
pytest tests/

# 格式化
ruff format .
black .
```

