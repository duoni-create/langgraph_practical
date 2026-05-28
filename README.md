# langgraph_practical

一个适合课堂演示的 LangGraph 小项目：`课程助教 Agent`。

它演示了 4 个最重要的入门概念：

- `State`：状态在节点之间流动
- `Node`：每个节点只做一件事
- `Edge`：根据意图走不同分支
- `Persistence`：通过 `thread_id` 记住同一条对话

当前课程助教 Agent 支持 5 种问题意图：`concept`、`compare`、`practice`、`project`、`summary`。

## 目录结构

```text
langgraph_practical/
├── pyproject.toml
├── README.md
└── src/langgraph_practical/
    ├── __init__.py
    ├── __main__.py
    ├── app.py
    ├── cli.py
    ├── knowledge.py
    ├── model.py
    └── state.py
```

## 安装

```bash
cd langgraph_practical
python3 -m venv .venv
.venv/bin/pip install -U pip
.venv/bin/pip install -e .
```

## 运行方式

### 1. 离线演示

```bash
PYTHONPATH=src .venv/bin/python -m langgraph_practical demo --mock
```

### 2. 真实调用 DeepSeek

```bash
cat > .env <<'EOF'
DEEPSEEK_API_KEY=你的 key
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_BASE_URL=https://api.deepseek.com
EOF

PYTHONPATH=src .venv/bin/python -m langgraph_practical run \
  --question "请用生活化的比喻解释什么是 LangGraph" \
  --thread-id class-01
```

### 3. 指定模型与地址

```bash
PYTHONPATH=src .venv/bin/python -m langgraph_practical run \
  --question "LangGraph 和 LangChain 有什么区别？" \
  --model deepseek-v4-flash \
  --base-url https://api.deepseek.com
```

## 设计说明

- 默认模型是 `deepseek-v4-flash`
- 默认会优先从 `.env` 读取 `DEEPSEEK_MODEL` 和 `DEEPSEEK_BASE_URL`
- 使用 `thread_id` 保持同一会话记忆
- 提供 `--mock` 模式，课堂没网也能完整演示图执行流程
- 没有把密钥写进代码，运行时通过 `.env`、环境变量或参数传入
