from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash"
DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com"


@dataclass(frozen=True)
class ModelSettings:
    """模型层配置：统一管理模型名、地址、温度和鉴权信息。"""

    model: str = DEFAULT_DEEPSEEK_MODEL
    base_url: str = DEFAULT_DEEPSEEK_BASE_URL
    temperature: float = 0.2
    api_key: str | None = None
    mock: bool = False


# 🌟🌟🌟🌟🌟🌟🌟🌟🌟  Protocol 可以理解成：给模型对象定一个“接口标准”。  只要一个对象有 generate(...) -> str 这个方法，并且参数长得一样，它就可以被当成 TutorModel 使用。
# 🌟🌟🌟🌟🌟🌟🌟🌟🌟  虽然下面两个类都没有继承 TutorModel： DeepSeekTutorModel、MockTutorModel ，但它们都有 generate 方法，所以都符合 TutorModel 这个协议。 ☀️ 说白了，就是不管用哪一个模型，名字都叫 tutor_model。
class TutorModel(Protocol):
    def generate(
        self,
        *,
        history: list[BaseMessage],
        question: str,
        intent: str,
        topic: str,
        context_text: str,
    ) -> str:
        """根据历史消息、意图和上下文生成给学生的答案。"""
        ...


class DeepSeekTutorModel:
    """真实模型实现：通过 OpenAI 兼容接口调用 DeepSeek。"""

    def __init__(self, settings: ModelSettings) -> None:
        """初始化 DeepSeek 客户端，并从参数或 .env 中读取 API Key。"""
        load_env_file()
        api_key = settings.api_key or os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "Missing DeepSeek API key. Set DEEPSEEK_API_KEY or pass --api-key."
            )
        self._client = ChatOpenAI(
            model=settings.model,
            api_key=api_key,
            base_url=settings.base_url,
            temperature=settings.temperature,
        )

    def generate(
        self,
        *,
        history: list[BaseMessage],
        question: str,
        intent: str,
        topic: str,
        context_text: str,
    ) -> str:
        """把图里整理好的上下文转成提示词，并请求 DeepSeek 生成答案。"""
        messages: list[BaseMessage] = [
            SystemMessage(
                content=(
                    "你是一位课堂上很会讲复杂技术的助教。"
                    "请把答案讲得口语化、结构清楚、带比喻、带一个具体场景。"
                    "避免堆术语，优先帮助初学者理解。"
                )
            )
        ]
        messages.extend(history[-4:])
        messages.append(
            HumanMessage(
                content=(
                    f"当前问题：{question}\n"
                    f"讲解意图：{intent}\n"
                    f"主题：{topic}\n"
                    f"可用素材：\n{context_text}\n\n"
                    "请输出：\n"
                    "1. 先用一句话回答\n"
                    "2. 再用生活化比喻解释\n"
                    "3. 再给一个小例子\n"
                    "4. 如果适合，再给一个课后练习"
                )
            )
        )
        response = self._client.invoke(messages)
        return str(response.content)


class MockTutorModel:
    """离线演示模型：不联网，直接返回固定结构的课堂示例答案。"""

    def generate(
        self,
        *,
        history: list[BaseMessage],
        question: str,
        intent: str,
        topic: str,
        context_text: str,
    ) -> str:
        """根据当前问题和上下文拼出一份可预测的 mock 结果。"""
        history_note = "这是同一 thread 下的追问。" if history else "这是第一轮提问。"
        sections = [
            f"一句话回答：你问的是 {topic}，当前分支属于 {intent} 型讲解。",
            "生活化比喻：把 LangGraph 想成一个有调度员的车站，问题像乘客，"
            "状态像行李牌，节点像站台，路线由当前信息决定。",
            f"具体例子：收到问题“{question}”后，图会先判断意图，再补资料，最后给出答案。",
            f"课堂提示：{history_note}",
            "可用素材摘录：",
            context_text,
        ]
        return "\n\n".join(sections)


def create_tutor_model(settings: ModelSettings) -> TutorModel:
    """根据配置决定使用真实模型还是离线 mock 模型。"""
    if settings.mock:
        return MockTutorModel()
    return DeepSeekTutorModel(settings)


def load_env_file() -> None:
    """从当前工作目录读取 .env，补充运行时需要的环境变量。"""
    env_path = Path.cwd() / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value
