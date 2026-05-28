# 课程助教 Agent 项目初始化说明

## 1. 项目定位

本项目是一个适合课堂演示的 LangGraph 入门项目，核心示例是「课程助教 Agent」。

它用一条清晰的图执行流程演示：

- `State`：节点之间共享和累积的数据
- `Node`：每个节点只负责一个明确动作
- `Edge`：根据意图把问题分发到不同分支
- `Persistence`：通过 `thread_id` 保留同一段对话的上下文

项目默认支持 DeepSeek 的 OpenAI 兼容接口，同时提供 `--mock` 离线模式，方便课堂没网时演示完整流程。

## 2. 目录结构

```text
langgraph_practical/
├── pyproject.toml
├── README.md
├── .env
└── src/
    ├── langgraph_practical/
    │   ├── __init__.py
    │   ├── __main__.py
    │   ├── app.py
    │   ├── cli.py
    │   ├── knowledge.py
    │   ├── model.py
    │   └── state.py
    └── readme/
        ├── 项目流程说明.md
        └── agent.md
```

## 3. 初始化环境

### Windows PowerShell

```powershell
uv sync
```

如果不用 `uv`，也可以手动创建虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -e .
```

### 环境变量

真实调用 DeepSeek 时，需要在项目根目录准备 `.env`：

```text
DEEPSEEK_API_KEY=你的 key
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

课堂演示或本地调试时可以优先使用 `--mock`，不需要 API Key。

## 4. 运行命令

### 离线双轮演示

```powershell
.\.venv\Scripts\python.exe -m langgraph_practical demo --mock
```

这个命令会固定执行两轮问题，用来观察同一个 `thread_id` 下的上下文记忆。

### 单轮提问

```powershell
.\.venv\Scripts\python.exe -m langgraph_practical run --mock --question "请用生活化的比喻解释什么是 LangGraph"
```

### 真实模型调用

```powershell
.\.venv\Scripts\python.exe -m langgraph_practical run --question "LangGraph 和 LangChain 有什么区别？" --thread-id class-01
```

## 5. 核心源码说明

| 文件 | 作用 |
|------|------|
| `src/langgraph_practical/cli.py` | 命令行入口，解析 `run` / `demo` 参数 |
| `src/langgraph_practical/app.py` | 构建 LangGraph 图，注册节点、边和 checkpointer |
| `src/langgraph_practical/state.py` | 定义 `TutorState`，说明图里会流动哪些状态 |
| `src/langgraph_practical/knowledge.py` | 本地知识库、意图识别、主题识别和上下文拼装 |
| `src/langgraph_practical/model.py` | 模型抽象层，包含 DeepSeek 实现和 mock 实现 |

## 6. 图执行流程

```text
START
  |
  v
analyze_question
  |
  v
route_by_intent
  |
  +--> retrieve_concept_context
  +--> retrieve_compare_context
  +--> retrieve_practice_context
  +--> retrieve_project_context
  +--> retrieve_summary_context
  |
  v
answer_question
  |
  v
END
```

执行时，`analyze_question` 会先从 `messages` 里取出最新的人类问题，然后识别：

- `intent`：问题意图，例如 `concept`、`compare`、`practice`、`project`、`summary`
- `topic`：问题主题，例如 `langgraph`、`state`、`checkpoint`

之后条件边根据 `intent` 进入不同资料补充节点，最后统一交给 `answer_question` 生成答案。

## 7. 状态约定

`TutorState` 是这个项目最重要的共享对象：

```python
class TutorState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], operator.add]
    intent: str
    topic: str
    context_blocks: list[str]
    answer: str
    llm_calls: int
    steps: Annotated[list[str], operator.add]
```

关键规则：

- `messages` 会追加保存对话消息，支撑多轮上下文。
- `steps` 会追加保存执行轨迹，方便课堂观察图的运行过程。
- `intent` 和 `topic` 是路由依据，不要在后续节点随意改写。
- `context_blocks` 是给模型使用的素材块，不建议提前拼成复杂 prompt。
- `llm_calls` 用于观察调用次数，不承担业务逻辑。

## 8. 后续开发约定

新增能力时优先按下面方式扩展：

1. 新增主题知识：改 `knowledge.py` 里的 `TOPIC_LIBRARY`。
2. 新增意图类型：补充 `detect_intent()`，再在 `app.py` 里增加对应检索节点和路由。
3. 修改回答风格：优先改 `model.py` 里的 system prompt 或 mock 输出。
4. 修改命令参数：集中改 `cli.py`，不要把命令行解析逻辑放进图节点。
5. 修改状态字段：先改 `state.py`，再逐个检查读写该字段的节点。

节点设计尽量保持单一职责：分析、检索、生成分开写，便于调试和课堂讲解。

## 9. 验证清单

改动后至少运行：

```powershell
.\.venv\Scripts\python.exe -m langgraph_practical demo --mock
```

重点确认：

- 第一轮和第二轮都能正常输出。
- `trace` 中能看到正确的意图、主题和分支。
- 第二轮仍然使用同一个 `thread_id`。
- `--mock` 模式不依赖网络和 API Key。

如果改动了真实模型调用，再额外确认 `.env` 中的 DeepSeek 配置是否可用。

## 10. 常见问题

### 为什么必须传 `thread_id`？

`thread_id` 是 LangGraph checkpoint 的会话编号。同一个 `thread_id` 会继承之前保存的状态，不同 `thread_id` 会被视为不同对话。

### 为什么有 `--mock`？

`--mock` 用来保证课堂演示稳定。它绕过真实网络请求，但仍然会完整执行 LangGraph 的节点和边。

### API Key 应该写在哪里？

优先写在项目根目录 `.env` 里，或者通过环境变量传入。不要把 API Key 写进源码或文档示例中的真实值。

### 想让 Agent 支持更多课程内容，应该改哪里？

优先改 `knowledge.py` 的 `TOPIC_LIBRARY`。这是当前项目的本地知识来源，也是最适合扩展课堂主题的位置。
