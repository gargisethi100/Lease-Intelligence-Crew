# Lease Intelligence Crew

A **multi-agent** system for commercial real-estate lease analysis, built with **LangGraph**. A supervisor routes an analyst's question to specialist agents — **RAG** over lease documents, live market research, and a **human-in-the-loop** analyst that runs code only after approval — with persistent memory and structured **lease abstraction**. The same capabilities are also exposed over an **MCP (Model Context Protocol)** server. Provider-agnostic across **Azure OpenAI**, AWS Bedrock, Google Gemini, and Anthropic.

## What it does

- **Portfolio Q&A (RAG):** ask questions about a folder of commercial lease PDFs and get grounded, cited answers — or an honest "I don't know" when the answer isn't in the documents.
- **Lease abstraction:** extract key terms (parties, rent, term, escalation, break clause, deposit) from a lease into **validated JSON** via structured output.
- **Market research:** pull current market/vacancy/rent context from the web (Tavily).
- **Analyst with approval:** writes small Python for rent math and **pauses for human approval** before running it.
- **Memory:** conversations persist across restarts, keyed by `thread_id` (SQLite checkpointer).
- **MCP server:** `search_leases`, `extract_lease_terms`, `project_rent` exposed to any MCP host (e.g. Claude Desktop).
- **Tracing:** every run is traced in LangSmith.

## Architecture

```
   User
     |
     v
   CLI  ----------------  SQLite checkpointer  (persistent memory by thread_id)
     |
     v
   SUPERVISOR  (LangGraph)  --- routes each question to one specialist ---
     |
     +--  Lease Expert       -> search_leases   (grounded RAG, cites sources)
     +--  Market Researcher  -> Tavily web search
     +--  Analyst            -> writes Python -> interrupt() for approval -> runs it
     |
     |  every specialist calls into...
     v
   core/   retrieval . abstraction . projection . ingest   (framework-neutral logic)
     |
     +-->  Chroma vector store   (Titan embeddings over the lease PDFs)
     |
     +-->  MCP server (FastMCP)  exposes the SAME core over JSON-RPC:
              search_leases, extract_lease_terms, project_rent
```

**Key design decision — a framework-neutral `core`.** Business logic lives once in `core/` and is exposed two ways: as LangChain tools for the agents, and as MCP tools for the server. No duplication, no coupling to a framework.

**Provider-agnostic.** `config.py` picks the chat model and embeddings independently from two `.env` switches, so switching between Azure OpenAI (the production target), AWS Bedrock, Gemini, or Anthropic is a config change — everything else codes against LangChain's shared model interface.

## Tech stack

Python 3.13 · LangGraph · LangChain · Azure OpenAI / AWS Bedrock / Gemini / Anthropic · Chroma · Tavily · Pydantic (structured output) · MCP (FastMCP) · SQLite checkpointer · LangSmith.

## Setup

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m pip install -e .
cp .env.example .env        # then fill in provider + LangSmith (+ Tavily) keys
```

Set `PROVIDER` and `EMBEDDINGS` in `.env` (e.g. `azure`, `bedrock`, `gemini`) and the matching keys. See `.env.example`.

## Usage

```bash
# 1. Add lease PDFs to data/leases/ (or generate synthetic samples)
.venv/Scripts/python scripts/make_sample_leases.py

# 2. Ingest them into the vector store (load -> chunk -> embed -> persist)
.venv/Scripts/python -m lease_crew.ingest

# 3. Chat with the crew (memory persists under this thread_id)
.venv/Scripts/python -m lease_crew.cli my-session

# 4. MCP: run the server, or drive it with the demo client
.venv/Scripts/python mcp_server/server.py          # stdio server
.venv/Scripts/python mcp_server/client_demo.py     # client: discover + call tools
mcp dev mcp_server/server.py                        # inspect in the MCP Inspector
```

## Project layout

```
lease_crew/
  config.py       provider-agnostic model + embeddings factory
  state.py        shared graph state (messages + routing)
  ingest.py       load -> chunk -> embed -> persist (Chroma)
  retrieval.py    search_leases (RAG core)
  abstraction.py  extract_lease_terms (structured output)
  projection.py   project_rent (pure math)
  tools.py        LangChain @tool adapters over core
  agents.py       the three specialist workers
  graph.py        supervisor graph + human-in-the-loop analyst
  cli.py          chat loop with persistent memory
mcp_server/
  server.py       FastMCP server (same core, over MCP)
  client_demo.py  minimal MCP client
```
