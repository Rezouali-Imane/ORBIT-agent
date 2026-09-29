# ORBIT Agent

A LangChain agent that manages a librarian (RAG), web researcher, and checker with human approval before saving.

## What it does

This agent helps you research topics by searching your own documents and the web. It can also create structured roadmaps for projects. The system requires human approval before saving any information or making changes to your document library.

## Main folders

- **agent/** - Core specialist agents (librarian, researcher, checker)
- **api/** - Document upload interface
- **data/docs/** - Your documents that get ingested into the RAG system
- **tools/** - Tools for searching documents, web research, and managing the document library
- **tests/** - Unit tests for various components

## Setup

1. Install dependencies: `uv sync`
2. Copy `.env.example` to `.env` and fill in your API keys
3. Put your own documents in `data/docs/`
4. Run document ingestion: `python tools/ingest.py`
5. Start the agent: `python main.py`

## Important notes

- Documents in `data/docs/` are not included in this repository - you must add your own
- The agent will ask for approval before saving any information or modifying your document library

## Status

- ✅ Core RAG functionality works (searching user documents)
- ✅ Web research functionality works (using Tavily API)
- ✅ Human-in-the-loop approval system works
- ✅ Document management (add/remove) works
- ⚠️ Roadmap creation and validation needs more testing

## License

This project is licensed under the MIT License - see the LICENSE file for details.