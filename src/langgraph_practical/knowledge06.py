from __future__ import annotations

from collections.abc import Sequence


# 本地主题知识库：把课堂要讲的主题、比喻、练习和项目建议预先整理好。
TOPIC_LIBRARY: dict[str, dict[str, object]] = {
    "langgraph": {
        "title": "LangGraph",
        "keywords": ["langgraph", "agent", "工作流", "图", "智能体"],
        "concept": (
            "LangGraph 是一个专门负责“把步骤串起来并管理状态”的框架。"
            "它不替你决定所有提示词，而是把流程控制权交还给开发者。"
        ),
        "analogy": (
            "把它想成机场中转系统：旅客是任务，登机牌是状态，登机口是节点，"
            "转机路线是边。旅客去哪一站，不只看地图，还看当前登机牌上的信息。"
        ),
        "compare": (
            "如果说普通 LLM 调用像一次问答，LangGraph 更像一条可追踪、可暂停、"
            "可恢复的流水线。"
        ),
        "practice": "给一个用户问题，设计 3 个节点：分类、检索、生成答案。",
        "project": "做一个课程助教 Agent：先判断问题类型，再补充资料，最后生成老师式回答。",
        "pitfalls": "不要把 LangGraph 理解成只有画图；它真正的价值是状态管理与流程编排。",
    },
    "state": {
        "title": "State",
        "keywords": ["state", "状态", "共享数据", "上下文", "messages"],
        "concept": (
            "State 是图里所有节点共用的一份工作区。节点读取它，也把结果写回去。"
        ),
        "analogy": (
            "它像医生手里的病历夹：挂号台、化验室、诊室都往同一份夹子里补充信息，"
            "这样后面的环节不需要从头再问一遍。"
        ),
        "compare": (
            "变量像一张便签，只在局部步骤里用；State 像统一档案，会贯穿整条流程。"
        ),
        "practice": "给 State 增加 `question`、`intent`、`answer` 三个字段，观察每一步怎么变化。",
        "project": "让课程助教 Agent 把用户问题、检索资料和最终答案都写入 State。",
        "pitfalls": "State 里尽量放原始数据，不要提前拼成一大段提示词。",
    },
    "node_edge": {
        "title": "Node / Edge",
        "keywords": ["node", "edge", "节点", "边", "路由", "分支"],
        "concept": "Node 是执行动作的函数，Edge 是从一个节点走到下一个节点的规则。",
        "analogy": (
            "节点像工厂里的工位，边像传送带。一个工位只负责一件事，"
            "这样出了问题更容易定位。"
        ),
        "compare": "普通函数链是写死的直线，图结构可以根据当前状态选择不同路线。",
        "practice": "写一个条件边：如果用户问的是练习题，就走到 `practice` 节点。",
        "project": "课程助教 Agent 用条件边决定走“概念讲解”还是“项目实战”分支。",
        "pitfalls": "不要让一个节点既分类、又检索、又生成，职责越杂，越难讲清楚。",
    },
    "checkpoint": {
        "title": "Checkpoint / Thread",
        "keywords": ["checkpoint", "thread", "持久化", "恢复", "记忆"],
        "concept": (
            "Checkpoint 是每一步执行后的存档点，Thread 是同一条任务或同一段对话的编号。"
        ),
        "analogy": (
            "它像打游戏的存档位。人打到第 7 关断电了，下次不用从第 1 关重来，"
            "只要读档即可。"
        ),
        "compare": "普通脚本中断后通常重跑；有 Checkpoint 的图可以从中途继续。",
        "practice": "给同一个 `thread_id` 连续提两个问题，观察第二次如何继承上下文。",
        "project": "课程助教 Agent 使用 `thread_id=class-01` 保留同一学生的追问记录。",
        "pitfalls": "没有 `thread_id`，就谈不上真正的会话记忆与恢复。",
    },
    "langgraph_vs_langchain": {
        "title": "LangGraph vs LangChain",
        "keywords": ["langchain", "区别", "对比", "比较", "vs"],
        "concept": (
            "LangChain 更像工具箱，负责模型、提示词、工具集成；"
            "LangGraph 更像调度中心，负责把步骤组织成一张可运行的图。"
        ),
        "analogy": (
            "盖房子时，LangChain 像砖块、门窗和水电材料；"
            "LangGraph 像施工总进度表和工地调度员。"
        ),
        "compare": (
            "入门做单轮调用、RAG、基础 Agent，用 LangChain 很顺手；"
            "要做多步骤、可恢复、有人机协同的流程，更适合上 LangGraph。"
        ),
        "practice": "把一个“问答 + 检索”的小应用拆成工具层和编排层各自负责什么。",
        "project": "在课程助教 Agent 里，用 LangGraph 管路线，用模型层做答案生成。",
        "pitfalls": "两者不是替代关系，常见用法是 LangChain 提供组件，LangGraph 负责编排。",
    },
}

DEFAULT_TOPIC = "langgraph"


def detect_intent(question: str) -> str:
    """根据问题内容粗粒度判断意图，决定后续走哪条分支。"""
    lowered = question.lower()
    if any(word in lowered for word in ["区别", "对比", "比较", "vs", "和"]):
        if "langgraph" in lowered and "langchain" in lowered:
            return "compare"
    if any(word in lowered for word in ["练习", "题", "作业", "quiz", "练一练"]):
        return "practice"
    if any(word in lowered for word in ["项目", "实战", "demo", "案例", "搭建"]):
        return "project"
    if any(word in lowered for word in ["区别", "对比", "比较", "vs"]):
        return "compare"
    return "concept"


def detect_topic(question: str) -> str:
    """从问题里匹配最相关的主题，找不到时回退到默认主题。"""
    lowered = question.lower()
    if "langgraph" in lowered and "langchain" in lowered:
        return "langgraph_vs_langchain"

    best_topic = DEFAULT_TOPIC
    best_score = 0
    for topic, payload in TOPIC_LIBRARY.items():
        score = sum(1 for keyword in payload["keywords"] if str(keyword).lower() in lowered)
        if score > best_score:
            best_topic = topic
            best_score = score
    return best_topic


def topic_title(topic: str) -> str:
    """把主题键转换成更适合展示给学生看的标题。"""
    return str(TOPIC_LIBRARY.get(topic, TOPIC_LIBRARY[DEFAULT_TOPIC])["title"])


def build_context_blocks(intent: str, topic: str) -> list[str]:
    """按意图和主题拼装上下文素材，供答案生成节点使用。"""
    payload = TOPIC_LIBRARY.get(topic, TOPIC_LIBRARY[DEFAULT_TOPIC])
    blocks = [
        f"主题：{payload['title']}",
        f"核心概念：{payload['concept']}",
        f"生活比喻：{payload['analogy']}",
        f"重点提醒：{payload['pitfalls']}",
    ]

    if intent == "compare":
        blocks.append(f"重点对比：{payload['compare']}")
    elif intent == "practice":
        blocks.append(f"练习建议：{payload['practice']}")
    elif intent == "project":
        blocks.append(f"项目建议：{payload['project']}")
    else:
        blocks.append(f"补充理解：{payload['compare']}")

    return blocks


def join_context(blocks: Sequence[str]) -> str:
    """把多个素材块合并成适合注入提示词的文本。"""
    return "\n".join(f"- {block}" for block in blocks)
