from __future__ import annotations

import operator

from langchain_core.messages import AnyMessage
from typing_extensions import Annotated, TypedDict


class TutorState(TypedDict, total=False):
    """LangGraph 在各节点之间传递的共享状态。"""

    # 对话消息列表，会随着多轮提问持续累加。
    messages: Annotated[list[AnyMessage], operator.add]
    # 当前问题识别出的意图，例如 concept / compare / practice / project / summary。
    intent: str
    # 当前问题匹配到的主题，例如 langgraph / state / checkpoint。
    topic: str
    # 检索或拼装得到的上下文素材块，供答案生成节点使用。
    context_blocks: list[str]
    # 最终返回给学生的口语化答案。
    answer: str
    # 人工审核结果：pending / approved / rejected。
    review_status: str
    # 人工审核时填写的原因或备注。
    review_reason: str
    # 当前线程里累计调用模型的次数，便于课堂观察执行过程。
    llm_calls: int
    # 图执行轨迹，会把每一步的重要动作追加进去。
    steps: Annotated[list[str], operator.add]


