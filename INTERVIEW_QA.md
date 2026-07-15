# Interview Q&A

Model answers in interview voice — 2–4 sentences each, the way to actually say them. Grouped by phase.

---

## Phase 0 — Setup, Providers, Tracing

**Q: How does Azure OpenAI differ from the plain OpenAI API?**
Same models, different front door. With Azure you call a *deployment* — your own named instance of a model — on a *per-resource, regional endpoint*, and you pass an explicit dated `api-version`. Auth is an `api-key` header or, better for enterprises, Microsoft Entra ID with role-based access. The regional endpoint is the whole point: your data stays in your tenant and region, which is why regulated industries like commercial real estate choose it.

**Q: What does "provider-agnostic" mean in your system, and how did you build it?**
The app never imports a vendor class. There's one factory module with `get_chat_model()` and `get_embeddings()`, and two `.env` switches choose the provider. Everything else codes against LangChain's shared `BaseChatModel` interface — `.invoke`, `.bind_tools`, `.with_structured_output` — so swapping between Azure, Bedrock, Gemini, or Anthropic is a config change, not a refactor. I actually proved it by running the same code across four providers.

**Q: Why factory functions instead of building the model at module import?**
Lazy construction. A module-level model would try to build a client — and read API keys — the moment anything imports the config, which breaks tests and any code that only needs part of the system. A factory defers construction until you call it, so importing config is free and needs no credentials.

**Q: Why are the chat provider and the embeddings provider chosen separately?**
Because they don't always come from the same vendor. Anthropic, for example, has no embeddings API, so if I use Claude for chat I still need embeddings elsewhere. Two independent switches let each capability pick the best available source.

**Q: How do you get LangSmith tracing, and how much code is it?**
Zero code. Tracing turns on from environment variables — `LANGSMITH_TRACING=true` plus the API key — which `load_dotenv()` loads at startup, and then LangChain records every model and chain call to the project automatically. I verified it by querying the project's runs through the LangSmith client, not just eyeballing the dashboard.

**Q: What's an editable install and why use one?**
`pip install -e .` installs a pointer to your source instead of a copy, so the package imports from anywhere in the repo and code edits take effect immediately with no reinstall. It's what lets my `scripts/` and `mcp_server/` folders import the shared `lease_crew` package without any `sys.path` hacks.

**Q: How do you keep secrets out of the repo?**
Real keys live in a gitignored `.env`; I commit only a `.env.example` template with empty values. And `.gitignore` only protects *untracked* files — if a secret ever got committed, you'd have to `git rm --cached` it *and rotate the key*, because it's already in history.

**Q: A model you hardcoded got deprecated. How do you handle model selection robustly?**
Don't hardcode blindly — provider catalogs change. I query the provider's models endpoint to see what my key can actually use, and I read the error codes: 404 means gone or gated, 429 is a rate/quota limit, 503 is transient overload. For stability I prefer a mature model or a `-latest` alias, and I keep the model name in an env var so changing it is config, not a redeploy.
