# Learning Notes

Plain-English summaries of the concepts behind each phase. Written to be re-read the night before an interview.

---

## Phase 0 — Setup, Providers, Tracing

### Virtual environments (and our 3.12 → 3.13 lesson)
A **virtual environment** (`venv`) is an isolated, per-project copy of Python + its own installed packages, so this project's dependencies never collide with another project's. We create it with `python -m venv .venv`.

Our Python **3.12 install was broken** — its standard library folder was missing. The tell: `ModuleNotFoundError: No module named 'encodings'` plus Python reporting its "home" as the current folder. That signature = *Python can't find its own standard library*. We switched to the working 3.13; the whole 2026 library stack supports it.

### Secrets hygiene (`.gitignore`)
- Real keys live in `.env`, which is **gitignored and never committed**. We commit only `.env.example`, a template with empty values.
- Git reads `.gitignore` top-to-bottom and **the last matching pattern wins**. A `!pattern` line *re-includes* something a previous line excluded — that's why `!.env.example` (placed *after* `.env.*`) keeps the template tracked. Order matters.
- **Landmine:** `.gitignore` only affects **untracked** files. If you already committed a secret, adding it to `.gitignore` does nothing — you must `git rm --cached <file>` **and rotate the key** (it's in history forever).

### Provider-agnostic design (`config.py`)
- We hide the vendor behind **factory functions** (`get_chat_model`, `get_embeddings`), not module-level objects. Functions build the model **lazily** — only when called — so importing config never needs credentials or a network call (great for tests and for tools that only need part of the system).
- **Lazy local imports** (import inside the branch that uses them) keep optional providers optional: the HuggingFace path only imports `torch` if you actually choose HuggingFace.
- **Two independent switches:** `PROVIDER` (chat) and `EMBEDDINGS` — separate on purpose, because our fallback chat provider (Anthropic) has **no embeddings API**.
- **Fail-fast vs default:** `os.environ["X"]` for values that *must* be set (loud `KeyError`), `os.getenv("X", default)` for values that can sensibly default.
- **Why swapping vendors is one line:** every LangChain chat model subclasses the same `BaseChatModel`, so they all expose the same methods (`.invoke`, `.bind_tools`, `.with_structured_output`). The app codes against that shared interface, not the vendor.

### Azure OpenAI vs plain OpenAI (interview favorite)
| | Plain OpenAI | Azure OpenAI |
|---|---|---|
| Model selection | `model="gpt-4o"` | a **deployment** (your named instance of a model) |
| Endpoint | one global URL | **per-resource, regional** URL → data residency / compliance |
| API version | none | explicit dated `api-version` (version pinning) |
| Auth | `Authorization: Bearer <key>` | `api-key` header **or** Microsoft **Entra ID** + RBAC (no static key) |

One-liner: *"Same models, different front door — named deployments on a regional endpoint with a pinned api-version, optionally auth'd with Entra ID. That's what makes it enterprise-grade."*

### Packaging: the editable install
`pip install -e .` installs a **pointer** to your source (via `site-packages`), not a copy. Result: code edits are live (no reinstall), and every folder in the repo can `import lease_crew.*` without `sys.path` hacks. Verified with Python's `-P` flag, which strips the current directory from the path — the import still worked, proving the install (not cwd) provides it.

### First LLM call + message types
- Chat models take a **list of typed messages**, not a raw string: `SystemMessage` (standing instructions/persona) and `HumanMessage` (the user turn) — mirroring the `system`/`user`/`assistant` roles of the chat API.
- `model.invoke(messages)` returns an **`AIMessage` object** (not a string); `.content` is the text, and it also carries metadata like token usage.
- `.invoke()` is the **universal method**: a model, a prompt, a chain, and later our whole **graph** all expose it. That uniformity is what lets LangGraph compose them.

### LangSmith tracing
Tracing is **environment-driven, zero code**: because `load_dotenv()` puts `LANGSMITH_TRACING=true` in the environment, LangChain automatically records every model call to your LangSmith project. "Tracing on every run" is a config setting, not something you instrument by hand.
