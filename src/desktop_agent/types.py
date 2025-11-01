"""
类型定义模块：统一数据类型定义
"""
from typing import Dict, Literal, Tuple

# 动作类型
ActionType = Literal["click", "type", "press", "code"]

# UI 元素定义：{"id": int, "bbox": [int, int, int, int], "text": str, "type": str}
UIElement = Dict[str, object]

# 视觉数据定义：{"elements": List[UIElement], "resolution": [int, int]}
VisionData = Dict[str, object]

# 动作定义：包含 type 字段，以及 element_id, text, key, language, code 等字段
Action = Dict[str, object]

# 元素映射：element_id -> bbox (x1, y1, x2, y2)
ElementMap = Dict[int, Tuple[int, int, int, int]]
