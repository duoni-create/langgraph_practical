from __future__ import annotations

import argparse
import os
import warnings

from langchain_core.messages import HumanMessage

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

    demo_parser = subparsers.add_parser("demo", help="Run a two-turn classroom demo")
    demo_parser.add_argument("--thread-id", default="class-demo", help="Conversation id")
    demo_parser.add_argument("--model", default=None, help="Model name")
    demo_parser.add_argument("--base-url", default=None, help="API base url")
    demo_parser.add_argument("--api-key", default=None, help="DeepSeek API key")
    demo_parser.add_argument("--mock", action="store_true", help="Use offline mock model")
    return parser


def _print_result(result: dict) -> None:
    """把图执行结果格式化打印到终端，便于课堂观察。"""
    print(f"intent: {result.get('intent')}")
    print(f"topic: {result.get('topic')}")
    print("trace:")
    for step in result.get("steps", [])[-5:]:
        print(f"  - {step}")
    print("\nanswer:\n")
    print(result.get("answer", ""))


def _invoke_question(app, *, question: str, thread_id: str) -> dict:
    """向图发送一个学生问题，并绑定 thread_id 以保留会话状态。"""
    config = {"configurable": {"thread_id": thread_id}}
    return app.invoke({"messages": [HumanMessage(content=question)]}, config)


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
        result = _invoke_question(app, question=args.question, thread_id=args.thread_id)     # 🌟🌟🌟 开始跑这个 graph
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
        result = _invoke_question(app, question=question, thread_id=args.thread_id)
        _print_result(result)


if __name__ == "__main__":
    main()
