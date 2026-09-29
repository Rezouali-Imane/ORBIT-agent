# ORBIT

ORBIT is organized as one repository with two applications:

- `orbit-agent/`: Python LangGraph manager, RAG library, approval tools, and upload API.
- `agent-chat-ui/`: official Agent Chat UI frontend.

## Run the backend

```powershell
cd orbit-agent
uv run langgraph dev
```

The LangGraph API runs at `http://127.0.0.1:2024`.

## Run the upload API

```powershell
cd orbit-agent
uv run uvicorn api.upload:app --reload --port 8000
```

Open `http://127.0.0.1:8000/upload`.

## Run the chat UI

```powershell
cd agent-chat-ui
npm install --legacy-peer-deps
npm exec turbo dev -- --filter=web
```

Open `http://localhost:3000`.
