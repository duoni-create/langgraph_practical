from __future__ import annotations

import warnings

from typing_extensions import TypedDict
from langchain_core._api.deprecation import LangChainPendingDeprecationWarning

warnings.filterwarnings("ignore", category=LangChainPendingDeprecationWarning)

from langgraph.graph import END, START, StateGraph


class HelloState(TypedDict):
    """Hello World 示例里在节点间流转的最小状态。"""

    user_text: str
    answer: str


def say_hello(state: HelloState) -> dict[str, str]:
    """读取用户输入，并返回一句最简单的问候结果。"""
    return {"answer": f"你好，你刚才说的是：{state['user_text']}"}


# 这几行展示了 LangGraph 最基本的三步：建图、加节点、连边。
graph = StateGraph(HelloState)
graph.add_node("say_hello", say_hello)
graph.add_edge(START, "say_hello")
graph.add_edge("say_hello", END)
app = graph.compile()


def main() -> None:
    """运行 Hello World 图，并打印最终输出。"""
    print(app.invoke({"user_text": "LangGraph"})["answer"])


if __name__ == "__main__":
    main()
