# Voice to Report

A small demo app: a construction worker **speaks** a short site note, and the app turns it into a **structured report**.
Full plan: `docs/spec.md`. Read it before each step.

## Tech stack
- **Frontend:** React + TypeScript (Vite)
- **Backend:** Python + FastAPI
- **Speech-to-text:** browser Web Speech API (free) by default; optional local Whisper (`faster-whisper`, free)
- **NLP:** spaCy (entities like dates, numbers, locations) + an LLM for structuring
- **LLM:** provider is configurable. Default: **Claude API** (`claude-haiku-5-5`; auth via `ant auth login` or `ANTHROPIC_API_KEY`). Optional: Ollama (free, local) or OpenAI via `LLM_PROVIDER` env variable.
- **Node:** 20 (see `.nvmrc`, run `nvm use`)
- **Database:** SQLite (simple, no setup)
- **Tests:** pytest (backend), Vitest (frontend)
- **CI:** GitHub Actions

## Project structure (always follow this)
```
voice-to-report/
├── CLAUDE.md
├── README.md
├── docs/spec.md
├── frontend/src/
│   ├── components/   → RecordButton, TranscriptView, ReportCard, ReportList
│   ├── hooks/        → useSpeechRecognition
│   ├── services/     → api.ts
│   └── types/        → report.ts
└── backend/
    ├── app/
    │   ├── main.py          → FastAPI app + routes
    │   ├── models.py        → Pydantic models (Report, ReportItem)
    │   ├── nlp.py           → spaCy pre-processing (dates, numbers, places)
    │   ├── llm/             → base.py (interface), ollama.py, claude.py, openai.py
    │   ├── report_service.py→ transcript → structured report
    │   └── db.py            → SQLite storage
    └── tests/
```

## Rules
- Build one step at a time (build plan in `docs/spec.md`). Stop after each step so I can test and commit.
- After each step, explain in simple words what you built and how I can test it.
- Every feature needs at least one test. LLM calls must be mocked in tests.
- Never commit API keys. Use `.env` (in `.gitignore`) and provide `.env.example`.
- Keep it small, clean and finished. Don't add features that aren't in the spec.
- The LLM must return **valid JSON** matching the Pydantic model. Validate it and retry once if invalid.
