# Voice to Report

A small demo app: a construction worker **speaks** a short site note, and the app turns it into a **structured report**.
Full plan: `docs/spec.md`. Read it before each step.

## Tech stack
- **Web app (`apps/web`):** React + TypeScript (Vite), Vitest
- **API (`apps/api`):** Python + FastAPI, Pydantic, pydantic-settings, pytest, ruff
- **Speech-to-text:** browser Web Speech API
- **NLP:** spaCy (dates, numbers, places) + dateparser + an LLM for structuring
- **LLM:** configurable with `LLM_PROVIDER`. Default: **Claude API** (`claude-haiku-5-5`; auth via `ant auth login` or `ANTHROPIC_API_KEY`). Optional: Ollama (local).
- **Node:** 20 (see `.nvmrc`, run `nvm use`)
- **Database:** SQLite
- **CI:** GitHub Actions · **Hosting:** Render (`render.yaml`)

## Project structure (always follow this)
```
apps/
├── api/
│   ├── app/
│   │   ├── main.py        → app factory + error handlers
│   │   ├── core/          → config (settings), errors, rate limit
│   │   ├── api/           → routers (health, reports) + dependencies
│   │   ├── schemas/       → Pydantic models
│   │   ├── services/      → nlp.py, report_service.py
│   │   ├── llm/           → base (interface), factory, claude, ollama
│   │   └── db/            → report repository (SQLite)
│   ├── eval/              → sample notes + accuracy script
│   └── tests/             → unit/, api/
└── web/src/
    ├── app/               → App (composition only)
    ├── features/          → recording/, reports/, health/
    ├── lib/               → http client, formatting
    └── test/              → setup and fakes
```

## Rules
- Every feature needs at least one test. LLM calls must be mocked in tests.
- Never commit API keys. Use `.env` (in `.gitignore`) and provide `.env.example`.
- Keep it small, clean and finished. Don't add features that aren't in the spec.
- The LLM must return **valid JSON** matching the Pydantic model. Validate it and retry once if invalid.
- Commit messages: short, imperative, professional.
