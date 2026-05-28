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
        "summary": "一句话总结：LangGraph 的重点是把 Agent 流程拆成可控节点，并用 State 串起上下文。",
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
        "summary": "一句话总结：State 是整张图共享的工作区，负责让前后节点看到同一份上下文。",
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
        "summary": "一句话总结：Node 负责做事，Edge 负责决定下一步去哪。",
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
        "summary": "一句话总结：Checkpoint 负责存档，Thread 负责标记这是哪一段对话。",
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
        "summary": "一句话总结：LangChain 偏组件工具箱，LangGraph 偏多步骤流程编排。",
        "pitfalls": "两者不是替代关系，常见用法是 LangChain 提供组件，LangGraph 负责编排。",
    },
    "tool_calling": {
        "title": "Tool Calling",
        "keywords": ["tool", "tools", "工具", "工具调用", "调用工具", "调用", "函数调用", "function calling"],
        "concept": (
            "Tool Calling 是让模型在需要时调用外部能力，例如查数据库、算价格、"
            "调用搜索接口，而不是只靠模型自己编答案。"
        ),
        "analogy": (
            "它像学生考试时可以举手请实验室测一次数据。模型负责判断什么时候需要工具，"
            "工具负责给出真实结果。"
        ),
        "compare": (
            "普通模型回答主要靠已有知识；带工具调用的 Agent 可以把问题交给确定性的函数"
            "或外部系统处理。"
        ),
        "practice": "写一个 `lookup_course(topic)` 工具，让助教按主题查询课程资料。",
        "project": "课程助教 Agent 可以把资料检索、作业查询、课程进度查询都封装成工具。",
        "summary": "一句话总结：Tool Calling 是让 Agent 从“会说”升级到“会办事”。",
        "pitfalls": "不要把所有逻辑都交给模型决定；工具入参、返回值和错误处理要设计清楚。",
    },
    "interrupt": {
        "title": "Interrupt / Human-in-the-loop",
        "keywords": ["interrupt", "中断", "打断", "人工介入", "人机协作", "审批", "确认"],
        "concept": (
            "Interrupt 是在图运行到关键步骤时暂停，把决定权交给人，等人确认或补充信息后再继续。"
        ),
        "analogy": (
            "它像银行转账前的二次确认。系统已经准备好执行，但真正动钱之前会停一下，"
            "让用户确认金额和收款人。"
        ),
        "compare": (
            "普通自动流程会一路跑到底；有人机协作的流程会在高风险或信息不足的位置暂停。"
        ),
        "practice": "设计一个审批节点：当回答会修改学生成绩时，先暂停等待老师确认。",
        "project": "课程助教 Agent 可以在发布作业、修改成绩、发送通知前加入人工确认。",
        "summary": "一句话总结：Interrupt 让 LangGraph 流程既能自动执行，也能在关键点请人把关。",
        "pitfalls": "中断恢复后节点可能重新进入，放在中断前的副作用要谨慎处理。",
    },
    "store": {
        "title": "Store / Long-term Memory",
        "keywords": ["store", "长期记忆", "长时记忆", "长期", "长时", "跨线程", "用户画像", "偏好"],
        "concept": (
            "Store 用来保存跨线程、跨会话都需要记住的信息，例如学生偏好、学习进度、"
            "常见薄弱点。"
        ),
        "analogy": (
            "它像学校的学生档案。一次对话里的草稿会结束，但学生的基础信息和学习记录"
            "应该长期保存。"
        ),
        "compare": (
            "Checkpoint 更像某一条对话的运行存档；Store 更像全局资料库，可以被不同线程复用。"
        ),
        "practice": "把学生喜欢的讲解风格写入 Store，下次新 thread 也能读出来。",
        "project": "课程助教 Agent 可以用 Store 保存学生画像，再按画像调整讲解难度。",
        "summary": "一句话总结：Store 负责长期业务记忆，Checkpoint 负责当前线程的运行状态。",
        "pitfalls": "不要把所有聊天记录都塞进 Store；长期记忆应该保存稳定、可复用的事实。",
    },
}

DEFAULT_TOPIC = "langgraph"


def detect_intent(question: str) -> str:
    """根据问题内容粗粒度判断意图，决定后续走哪条分支。"""
    lowered = question.lower()
    if any(word in lowered for word in ["总结", "小结", "归纳", "概括", "回顾", "复盘", "summary"]):
        return "summary"
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
    elif intent == "summary":
        blocks.extend(
            [
                f"课堂小结：{payload['summary']}",
                f"复盘线索：先说它解决什么问题，再说它在项目里放在哪一层。",
            ]
        )
    else:
        blocks.append(f"补充理解：{payload['compare']}")

    return blocks


def join_context(blocks: Sequence[str]) -> str:
    """把多个素材块合并成适合注入提示词的文本。"""
    return "\n".join(f"- {block}" for block in blocks)
