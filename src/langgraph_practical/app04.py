from __future__ import annotations

from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from langgraph_practical.knowledge06 import (
    build_context_blocks,
    detect_intent,
    detect_topic,
    join_context,
    topic_title,
)
from langgraph_practical.model07 import ModelSettings, TutorModel, create_tutor_model
from langgraph_practical.state05 import TutorState

# 🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟  这个文件，主要用来构建 graph 图对象  🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟

def _latest_question(state: TutorState) -> str:
    """从状态里的消息列表中取出最近一轮学生提问。"""
    for message in reversed(state["messages"]):    # 🌟🌟🌟 reversed 意思是：把 state["messages"] 这个消息列表倒着遍历。
        if isinstance(message, HumanMessage):    # 🌟🌟🌟 isinstance  意思是：判断 message 这个对象是不是 HumanMessage 类型。
            return str(message.content)
    raise ValueError("State does not contain a human message.")


def _history_without_latest_question(state: TutorState) -> list:
    """提取当前问题之前的历史消息，供模型感知上下文。"""
    messages = state["messages"]
    for index in range(len(messages) - 1, -1, -1):
        if isinstance(messages[index], HumanMessage):
            return messages[:index]
    return []


def create_app(settings: ModelSettings):
    """按照模型配置创建整张课程助教图的可运行实例。"""
    tutor_model = create_tutor_model(settings)  # 🌟🌟🌟  先生成一个 model
    return build_tutor_graph(tutor_model)       # 🌟🌟🌟  再生成一个 graph


# 🌟🌟🌟 创建一个 graph 图对象
def build_tutor_graph(tutor_model: TutorModel):
    """组装课程助教 Agent 的节点、边和持久化能力。"""
    workflow = StateGraph(TutorState)

    # 🌟🌟🌟 下面这些就是一个个 node 节点
    def analyze_question(state: TutorState) -> dict:
        """分析学生问题，识别意图和主题，作为整张图的路由入口。"""
        question = _latest_question(state)
        intent = detect_intent(question)
        topic = detect_topic(question)
        return {
            "intent": intent,
            "topic": topic,
            "steps": [
                f"收到问题：{question}",
                f"识别意图：{intent}",
                f"识别主题：{topic_title(topic)}",
            ],
        }

    def retrieve_concept_context(state: TutorState) -> dict:
        """为概念讲解问题补充基础概念和比喻素材。"""
        topic = state["topic"]
        return {
            "context_blocks": build_context_blocks("concept", topic),
            "steps": [f"进入概念讲解分支：{topic_title(topic)}"],
        }

    def retrieve_compare_context(state: TutorState) -> dict:
        """为对比类问题补充差异点和比较素材。"""
        topic = state["topic"]
        return {
            "context_blocks": build_context_blocks("compare", topic),
            "steps": [f"进入对比分支：{topic_title(topic)}"],
        }

    def retrieve_practice_context(state: TutorState) -> dict:
        """为练习题补充可直接给学生使用的练习建议。"""
        topic = state["topic"]
        return {
            "context_blocks": build_context_blocks("practice", topic),
            "steps": [f"进入练习分支：{topic_title(topic)}"],
        }

    def retrieve_project_context(state: TutorState) -> dict:
        """为项目实战类问题补充案例和实现建议。"""
        topic = state["topic"]
        return {
            "context_blocks": build_context_blocks("project", topic),
            "steps": [f"进入项目实战分支：{topic_title(topic)}"],
        }

    def retrieve_summary_context(state: TutorState) -> dict:
        """为课堂小结类问题补充提纲式复盘素材。"""
        topic = state["topic"]
        return {
            "context_blocks": build_context_blocks("summary", topic),
            "steps": [f"进入课堂小结分支：{topic_title(topic)}"],
        }

    def answer_question(state: TutorState) -> dict:
        """调用模型把问题、上下文和历史消息整理成最终答案。"""
        question = _latest_question(state)
        history = _history_without_latest_question(state)
        context_text = join_context(state.get("context_blocks", []))

        # 🌟🌟🌟🌟🌟🌟🌟🌟🌟  这个节点需要有一个 LLM ，所以其他 .py 文件需要有相应的逻辑去处理，生成一个 LLM，那这里就可以拿来用。  说白了，每个节点，都是在组装工具而已，很简单的，就是将这些工具组装成一个“功能”。
        answer = tutor_model.generate(
            history=history,
            question=question,
            intent=state["intent"],
            topic=state["topic"],
            context_text=context_text,
        )
        llm_calls = state.get("llm_calls", 0) + 1
        return {
            "messages": [AIMessage(content=answer)],
            "answer": answer,
            "llm_calls": llm_calls,
            "steps": [f"调用模型生成答案，第 {llm_calls} 次"],
        }

    def route_by_intent(
        state: TutorState,
    ) -> Literal[
        "retrieve_concept_context",
        "retrieve_compare_context",
        "retrieve_practice_context",
        "retrieve_project_context",
        "retrieve_summary_context",
    ]:
        """根据意图把流程分发到不同的资料检索分支。"""
        mapping = {
            "concept": "retrieve_concept_context",
            "compare": "retrieve_compare_context",
            "practice": "retrieve_practice_context",
            "project": "retrieve_project_context",
            "summary": "retrieve_summary_context",
        }
        return mapping.get(state["intent"], "retrieve_concept_context")

    # 先注册所有节点，再定义节点之间的连接关系。
    workflow.add_node("analyze_question", analyze_question)
    workflow.add_node("retrieve_concept_context", retrieve_concept_context)
    workflow.add_node("retrieve_compare_context", retrieve_compare_context)
    workflow.add_node("retrieve_practice_context", retrieve_practice_context)
    workflow.add_node("retrieve_project_context", retrieve_project_context)
    workflow.add_node("retrieve_summary_context", retrieve_summary_context)
    workflow.add_node("answer_question", answer_question)

    # 图的主流程：入口先分析问题，中间按意图路由，最后统一生成答案。
    workflow.add_edge(START, "analyze_question")
    workflow.add_conditional_edges("analyze_question", route_by_intent)   # 🌟🌟🌟  条件边， route_by_intent 是一个函数处理，决定接下来走哪一个节点
    workflow.add_edge("retrieve_concept_context", "answer_question")
    workflow.add_edge("retrieve_compare_context", "answer_question")
    workflow.add_edge("retrieve_practice_context", "answer_question")
    workflow.add_edge("retrieve_project_context", "answer_question")
    workflow.add_edge("retrieve_summary_context", "answer_question")
    workflow.add_edge("answer_question", END)

    # 编译时挂上内存检查点，这样同一 thread_id 下可以保留多轮对话状态。
    return workflow.compile(checkpointer=InMemorySaver())
