# ORBIT-agent

LangChain manager agent that coordinates specialist sub-agents to research, check, and produce an approved roadmap.

## Document library

The manager can search, add, list, and remove `.pdf`, `.md`, and `.txt` documents. Adding and removing documents pauses for human approval. The lightweight upload page can be started with:

```powershell
uv run uvicorn api.upload:app --reload --port 8000
```

Open `http://127.0.0.1:8000/upload` to upload a document. Files are limited to 20 MB and duplicate content is skipped.