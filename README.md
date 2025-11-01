# Desktop Agent



## 安装

```bash
pip install desktop-agent
```

> 开发模式（可修改源码）：
```bash
git clone https://github.com/yourname/desktop-agent.git
cd desktop-agent
pip install -e .
```

### 依赖
- `pyautogui`：鼠标键盘控制
- `Pillow`：图像处理
- `requests`：调用 grounding 模型
- `openai`：主决策模型（可替换）

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

```python
# examples/demo.py
from desktop_agent import capture_screenshot, DecisionAgent, GroundingModel, Executor

# 1. 截图
screenshot_bytes, _ = capture_screenshot(width=1920, height=1080)

# 2. 决策模型
agent = DecisionAgent(provider="openai", model="gpt-4o")

# 3. Grounding 模型
grounding = GroundingModel(
    url="http://localhost:8080",
    model="ui-tars-1.5-7b",
    width=1920, height=1080
)

# 4. 执行器
executor = Executor(enable_local_env=True)

# 5. 执行任务
instruction = "打开记事本，输入 'Hello Desktop Agent' 并保存为 demo.txt"
actions = agent.decide(instruction, screenshot_bytes, grounding)
executor.execute(actions)
```

```bash
python examples/demo.py
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

---

## 支持的动作类型

| 类型 | 示例 |
|------|------|
| `click` | `{"type": "click", "x": 320, "y": 560}` |
| `type` | `{"type": "type", "text": "Hello"}` |
| `press` | `{"type": "press", "key": "enter"}` |
| `code` | `{"type": "code", "language": "python", "code": "print(42)"}` |

> `code` 动作需启用 `enable_local_env=True`

---

## 安全提示

- **本地代码执行** 会以当前用户权限运行任意代码
- 仅在 **可信任务** 和 **隔离环境** 中启用
- 建议使用 **Docker 沙箱** 或 **虚拟机** 运行

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

