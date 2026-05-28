from __future__ import annotations

import argparse
import os
import warnings

from langchain_core.messages import HumanMessage
from langgraph.types import Command

from langgraph_practical.model07 import (
    DEFAULT_DEEPSEEK_BASE_URL,
    DEFAULT_DEEPSEEK_MODEL,
    ModelSettings,
    load_env_file,
)

# 🌟🌟🌟🌟🌟🌟🌟🌟🌟  这个文件是 “主程序”，可以理解就是 main 程序，然后在这里会去跑 graph，如果中断了，怎么恢复也是在这里去写代码。

def _build_parser() -> argparse.ArgumentParser:
    """定义命令行参数，区分单轮问答和双轮演示两种运行模式。"""
    parser = argparse.ArgumentParser(description="Run the LangGraph classroom tutor demo")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Ask one question")
    run_parser.add_argument("--question", required=True, help="Student question")
    run_parser.add_argument("--thread-id", default="class-demo", help="Conversation id")
    run_parser.add_argument("--model", default=None, help="Model name")
    run_parser.add_argument("--base-url", default=None, help="API base url")
    run_parser.add_argument("--api-key", default=None, help="DeepSeek API key")
    run_parser.add_argument("--mock", action="store_true", help="Use offline mock model")
    run_parser.add_argument(
        "--review-decision",
        choices=["prompt", "approve", "reject"],
        default="prompt",
        help="Human review decision before answer generation",
    )
    run_parser.add_argument("--review-reason", default="", help="Reason used with review decision")

    demo_parser = subparsers.add_parser("demo", help="Run a two-turn classroom demo")
    demo_parser.add_argument("--thread-id", default="class-demo", help="Conversation id")
    demo_parser.add_argument("--model", default=None, help="Model name")
    demo_parser.add_argument("--base-url", default=None, help="API base url")
    demo_parser.add_argument("--api-key", default=None, help="DeepSeek API key")
    demo_parser.add_argument("--mock", action="store_true", help="Use offline mock model")
    demo_parser.add_argument(
        "--review-decision",
        choices=["prompt", "approve", "reject"],
        default="prompt",
        help="Human review decision before answer generation",
    )
    demo_parser.add_argument("--review-reason", default="", help="Reason used with review decision")
    return parser


def _print_result(result: dict) -> None:
    """把图执行结果格式化打印到终端，便于课堂观察。"""
    print(f"intent: {result.get('intent')}")
    print(f"topic: {result.get('topic')}")
    if result.get("review_status"):
        print(f"review: {result.get('review_status')}")
    if result.get("review_reason"):
        print(f"review_reason: {result.get('review_reason')}")
    print("trace:")
    for step in result.get("steps", [])[-5:]:
        print(f"  - {step}")
    print("\nanswer:\n")
    print(result.get("answer", ""))


def _interrupt_payload(result: dict) -> object | None:
    """从图执行结果中取出 interrupt payload；没有中断时返回 None。"""
    interrupts = result.get("__interrupt__")
    if not interrupts:
        return None
    return interrupts[0].value


def _print_review_payload(payload: object) -> None:
    """把人工审核节点暴露出来的信息打印给命令行用户。"""
    if not isinstance(payload, dict):
        print(f"\n[human review]\n{payload}")
        return

    print("\n[human review]")
    print(payload.get("question", "是否批准继续执行？"))
    print(f"student_question: {payload.get('student_question', '')}")
    print(f"intent: {payload.get('intent', '')}")
    print(f"topic: {payload.get('topic_title') or payload.get('topic', '')}")
    blocks = payload.get("context_blocks") or []
    if blocks:
        print("context:")
        for block in blocks:
            print(f"  - {block}")


def _decision_payload(decision: str, reason: str = "") -> dict[str, object]:
    """把命令行里的审核决定转成 Command(resume=...) 使用的数据。"""
    return {
        "approved": decision == "approve",
        "reason": reason.strip(),
    }


def _prompt_review_decision() -> dict[str, object]:
    """在命令行里收集批准或驳回；无交互输入时默认批准，方便课堂脚本继续跑。"""
    while True:
        try:
            user_input = input("请输入审核决定 (y=批准 / n=驳回): ").strip().lower()
        except EOFError:
            print("y")
            return _decision_payload("approve")

        if user_input in {"y", "yes", "是", "批准", "通过", "approve"}:
            return _decision_payload("approve")
        if user_input in {"n", "no", "否", "驳回", "拒绝", "reject"}:
            try:
                reason = input("请输入驳回原因: ").strip()
            except EOFError:
                reason = "人工审核驳回"
                print(reason)
            return _decision_payload("reject", reason)
        print("无效输入，请输入 y/yes/是/批准 或 n/no/否/驳回")


def _resume_after_review(
    app,
    *,
    result: dict,
    config: dict,
    review_decision: str,
    review_reason: str,
) -> dict:
    """如果图在人工审核节点暂停，就收集决定并恢复执行。"""
    while True:
        payload = _interrupt_payload(result)
        if payload is None:
            return result    # 🌟🌟🌟 如果没有发生中断，那么这个函数 return 直接打断

        _print_review_payload(payload)
        if review_decision == "prompt":
            decision = _prompt_review_decision()
        else:
            decision = _decision_payload(review_decision, review_reason)
            print(f"使用预设审核决定：{review_decision}")
            if review_reason:
                print(f"审核原因：{review_reason}")
        result = app.invoke(Command(resume=decision), config)   # 🌟🌟🌟🌟🌟🌟🌟🌟🌟 这里的 Command 是为了“中断后恢复”


def _invoke_question(
    app,
    *,
    question: str,
    thread_id: str,
    review_decision: str,
    review_reason: str,
) -> dict:
    """向图发送一个学生问题，并绑定 thread_id 以保留会话状态。"""
    config = {"configurable": {"thread_id": thread_id}}
    result = app.invoke({"messages": [HumanMessage(content=question)]}, config)    # 🌟🌟🌟🌟🌟🌟🌟🌟🌟  这里调用，有可能某一个节点，发生了打断，其实就是“人工介入”
    return _resume_after_review(
        app,
        result=result,
        config=config,
        review_decision=review_decision,
        review_reason=review_reason,
    )




def main() -> None:
    """CLI 主入口：解析参数、创建应用，并执行 run 或 demo 模式。"""
    parser = _build_parser()
    args = parser.parse_args()
    load_env_file()

    warnings.filterwarnings(
        "ignore",
        message="The default value of `allowed_objects` will change in a future version.*",
    )

    from langgraph_practical.app04 import create_app

    settings = ModelSettings(
        model=args.model or os.getenv("DEEPSEEK_MODEL") or DEFAULT_DEEPSEEK_MODEL,
        base_url=args.base_url
        or os.getenv("DEEPSEEK_BASE_URL")
        or DEFAULT_DEEPSEEK_BASE_URL,
        api_key=args.api_key or os.getenv("DEEPSEEK_API_KEY"),
        mock=args.mock,
    )
    app = create_app(settings)    # 🌟🌟🌟 构建好一切，包括 model、graph

    # ☀️ model 模式，真实调用 大模型 API
    if args.command == "run":
        result = _invoke_question(         # 🌟🌟🌟 开始跑这个 graph
            app,
            question=args.question,
            thread_id=args.thread_id,
            review_decision=args.review_decision,
            review_reason=args.review_reason,
        )
        _print_result(result)
        return


    # ☀️ demo 模式，固定演示两轮提问，方便课堂展示 thread 记忆效果。
    questions = [
        "请用生活化的比喻解释什么是 LangGraph。",
        "那 State 和 Checkpoint 分别像什么？请顺便给我一个练习。",
    ]
    for index, question in enumerate(questions, start=1):
        print(f"\n=== Round {index} ===")
        print(f"question: {question}\n")
        result = _invoke_question(
            app,
            question=question,
            thread_id=args.thread_id,
            review_decision=args.review_decision,
            review_reason=args.review_reason,
        )
        _print_result(result)


if __name__ == "__main__":
    main()
