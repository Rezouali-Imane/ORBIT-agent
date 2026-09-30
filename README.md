# ORBIT

**A team of AI specialists that answers from your own documents and the web, cites its sources, double-checks itself, and asks your permission before it saves anything.**

> Built after the LangChain Academy *Foundations* course, as part of Thirduni.

---

## What it does

Ask ORBIT a question and a **manager** agent decides who should work on it. It is not a fixed script: for each question the manager chooses which specialists to call.

| Specialist       | Job                                                                                                                                                                   |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Librarian**    | Searches your own documents (RAG) and answers only from them, with the document name and page. Says "I don't have this in my documents" when it can't find an answer. |
| **Researcher**   | Searches the web for current information and returns findings with links.                                                                                             |
| **Checker**      | Reads the draft answer and flags any claim that has no source, before you see it.                                                                                     |
| **Roadmap tool** | Turns a plan into a structured roadmap and draws it.                                                                                                                  |
| **Notes**        | Saves project notes, but only after you approve.                                                                                                                      |

### Four things that make it an agent, not a chatbot

1. It chooses its own tools for each question.
2. It works as a team of specialists.
3. It pauses and asks you before saving or changing anything.
4. It checks its own answer and shows its sources.


##
## Safety

* **Web pages and documents are information, never instructions.** The agent is told to ignore any instruction found inside retrieved content.
* **Human approval:** Saving a note pauses for approve / edit / reject.
* **Your keys stay in `.env`** and are never committed.
* **What runs where:** The agent code and document store run on my computer; model calls and web search are handled by the configured external services.

---

## How it is built

```text
you ──> Manager agent ──┬──> Librarian ──> document store (RAG)
                        ├──> Researcher ──> web search
                        ├──> Checker
                        ├──> Roadmap tool
                        └──> Notes (with approval)
```

* **LangChain** `create_agent`, with human-in-the-loop middleware
* **LangGraph** dev server for running and inspecting the agent
* **Groq** for the language model
* **Vector store** for document search
* **LangSmith** for traces

### Project structure

```text
agent/      manager and specialists (librarian, researcher, checker)
api/        document upload interface
tools/      notes, roadmap, web research, and document tools
tests/      unit tests
data/docs/  put your own documents here (not included in the repo)
main.py     run the agent
langgraph.json  configuration for the LangGraph server
```

---

## Run it yourself

**You need:** Python 3.13, [uv](https://docs.astral.sh/uv/), and API keys for the services above.

```bash
git clone [YOUR-REPO-URL]
cd [YOUR-REPO-FOLDER]
uv sync
```

1. Copy `.env.example` to `.env` and fill in your keys.

2. Put your own documents (PDF, Markdown, or text) in `data/docs/`.

3. Run document ingestion:

   ```bash
   python tools/ingest.py
   ```

4. Start the agent:

   ```bash
   python main.py
   ```

5. Or run it with the LangGraph development server:

   ```bash
   uv run langgraph dev
   ```

---

## What works and what is next

**Works now:**

* Manager and specialist agents
* RAG over user documents
* Web research
* Sourced answers
* Self-checking
* Human approval before saving
* Document management
* Roadmap generation
* LangSmith traces
* Conversation memory

**Next:**

* Animated agent state / interface
* Voice input
* Hosted demo
* More evaluation tests and scoring

---

## License

MIT. See LICENSE.

---

Built by [Imane Rezouali](https://github.com/Rezouali-Imane) as part of Thirduni.

# 
