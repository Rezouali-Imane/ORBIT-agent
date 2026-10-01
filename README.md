# ORBIT

ORBIT is a document-aware research agent built around a manager and a small team of specialist agents. It answers questions from private documents and the web, checks its own draft, cites the evidence it used, and asks for human approval before it writes a project note or changes the document library.

The project was built after the LangChain Academy Foundations course as part of Thirduni.

## Why ORBIT exists

Most chat interfaces optimize for a fast answer. ORBIT is designed for answers that can be inspected and acted on:

- It chooses tools based on the question instead of following a fixed sequence.
- It separates document retrieval, web research, checking, and writing into specialist responsibilities.
- It treats retrieved text as untrusted information, never as instructions.
- It shows the sources behind an answer when they are available.
- It pauses for approval before saving notes or changing the document library.

## How a request flows

```text
User question
     |
     v
Manager agent
  |       |        |          |           |
  v       v        v          v           v
Librarian Researcher Checker  Roadmap   Notes
  |       |        |          |           |
  v       v        v          v           v
RAG     Web      Draft      Mermaid    Approval
search  search   review     roadmap    gate
```

The manager can call only the specialists needed for a request. A question about an uploaded PDF may use the Librarian and Checker, while a current-events question may use the Researcher and Checker.

## Specialist team

| Specialist | Responsibility |
| --- | --- |
| **Manager** | Interprets the request, selects tools, combines results, and produces the final response. |
| **Librarian** | Searches the local document index and answers from available documents with source references. |
| **Researcher** | Uses web search for current information and returns linked findings. |
| **Checker** | Reviews the draft against its sources and flags unsupported claims or roadmap structure problems. |
| **Roadmap studio** | Converts an approved plan into structured roadmap data and Mermaid output. |
| **Notes** | Saves project notes only after a human approves, edits, or rejects the proposed action. |

## Human approval

The manager uses LangChain's human-in-the-loop middleware for side effects. A note request produces an approval card in the web UI with editable title and content fields. The reviewer can:

1. Approve the original tool call.
2. Edit the proposed tool arguments and approve the edited call.
3. Reject the request without writing the note.

The same pattern protects document additions and removals. The UI supports the current LangGraph interrupt format (`action_requests` and `review_configs`) and maps reviews to `approve`, `edit`, or `reject` decisions.

## Repository layout

```text
ORBIT-agent/
|-- orbit-agent/                  Python agent and LangGraph server
|   |-- agent/                    manager and specialist agents
|   |-- api/                      upload endpoint and upload page
|   |-- data/docs/                local source documents
|   |-- data/notes.json           approved project notes
|   |-- tools/                    retrieval, notes, roadmap, and web tools
|   |-- tests/                    backend tests
|   |-- main.py                   standalone agent entry point
|   |-- langgraph.json            LangGraph graph registration
|   `-- pyproject.toml            Python dependencies and test settings
|-- agent-chat-ui/                Next.js web client
|   `-- apps/web/                 Orbit landing page and chat workspace
|-- README.md
`-- LICENSE
```

## Requirements

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/)
- Node.js and npm
- A Groq API key for the configured chat model
- A Tavily API key for web research
- A LangSmith API key if tracing is enabled

The backend can run without a LangSmith key when using a local development server, but model and search features require their provider keys.

## Backend setup

From the repository root:

```bash
cd orbit-agent
uv sync
copy .env.example .env       # Windows PowerShell: Copy-Item .env.example .env
```

Fill in `.env`:

```dotenv
GROQ_API_KEY=your-groq-key
GROQ_MODEL=qwen/qwen3.8-27b
TAVILY_API_KEY=your-tavily-key
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=orbit
```

Optional provider and storage variables are documented in `orbit-agent/.env.example`.

### Add documents

Place PDF, Markdown, or plain-text files in `orbit-agent/data/docs/`, then ingest them:

```bash
cd orbit-agent
uv run python tools/ingest.py
```

The document search tools use the resulting local index. Keep private source files and generated local data out of commits.

### Run the backend

For the LangGraph development API:

```bash
cd orbit-agent
uv run langgraph dev --no-reload --no-browser
```

The default local endpoints are:

- API: `http://127.0.0.1:2024`
- API docs: `http://127.0.0.1:2024/docs`
- Graph ID: `orbit_agent`

For the standalone terminal entry point:

```bash
cd orbit-agent
uv run python main.py
```

## Web UI setup

The web client is a Next.js application in `agent-chat-ui/apps/web`.

```bash
cd agent-chat-ui
npm install
```

Create `agent-chat-ui/apps/web/.env.local`:

```dotenv
NEXT_PUBLIC_API_URL=http://127.0.0.1:2024
NEXT_PUBLIC_ASSISTANT_ID=orbit_agent
```

Start the UI:

```bash
cd agent-chat-ui/apps/web
npm run dev
```

Open the URL printed by Next.js, usually `http://localhost:3000`. If that port is busy, Next.js selects another available port.

The workspace provides a responsive conversation view, source-aware assistant messages, Mermaid roadmap previews, tool activity, and approval controls for human-in-the-loop actions.

## Testing and validation

Backend tests:

```bash
cd orbit-agent
uv run pytest -q
uv run python -m compileall -q .
```

Frontend production build:

```bash
cd agent-chat-ui/apps/web
npm run build:internal
```

The frontend build may report existing ESLint warnings from the upstream chat UI; warnings do not prevent a successful production build.

## Safety and privacy

- Retrieved web pages and documents are treated as data, not executable instructions.
- Notes and document mutations are gated by human approval.
- API keys belong in local `.env` files and are not committed.
- The local development server uses in-memory runtime persistence.
- Document contents, notes, and model prompts may be sent to the external providers configured in your environment.

## Current status

Implemented:

- Manager and specialist agent routing
- Local document retrieval and document management
- Web research with Tavily
- Source-aware answers and self-checking
- Human approval for notes and document mutations
- Structured roadmap generation with Mermaid output
- LangSmith tracing support
- LangGraph development server integration
- Next.js chat workspace

Planned:

- Hosted public demo
- More automated evaluation and answer scoring
- Richer activity history and agent-state visualization
- Voice input

## License

MIT. See [LICENSE](LICENSE).

Built by [Imane Rezouali](https://github.com/Rezouali-Imane) as part of Thirduni.
