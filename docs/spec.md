# Voice to Report: Design Spec

## 1. Goal
A worker speaks a short note on site. The app turns it into a clean, structured report that can be saved and reviewed.

**Example input (spoken):**
> "Room 3 on the second floor, there's a crack in the wall next to the window. Needs to be fixed by Friday, high priority. Tell the plasterer."

**Example output:**
```json
{
  "location": "2nd floor, room 3",
  "issue": "Crack in the wall next to the window",
  "category": "Damage",
  "priority": "High",
  "due_date": "2026-11-13",
  "assigned_trade": "Plasterer",
  "summary": "Crack in wall next to window in room 3 (2nd floor), fix by Friday.",
  "language": "en"
}
```

Purpose: show **TypeScript + Python + NLP + LLMs** working together, with clean architecture, testing and CI.
Scope rule: **small and finished beats big and half-done.**

## 2. Features (v1)
1. **Record:** big microphone button; live transcript appears while speaking (Web Speech API).
2. **Edit transcript:** the user can correct the text before generating the report.
3. **Generate report:** backend turns the transcript into the structured JSON above.
4. **Report card:** shows the fields clearly, with a coloured priority badge (High = red, Medium = orange, Low = green).
5. **Save and list:** reports are stored in SQLite and shown in a list (newest first).
6. **Languages:** works with English and German input (the output fields stay in English).

### Out of scope (v1)
Login, photos, PDF export, multiple users, mobile app.

## 3. NLP pipeline (backend)
1. **Clean** the transcript (trim, normalise spaces).
2. **spaCy pre-processing** (`nlp.py`): extract dates, numbers and locations as hints (classic NLP before the LLM).
3. **Relative dates:** convert words like "Friday" or "tomorrow" into real dates (e.g. with `dateparser`), based on today's date.
4. **LLM structuring** (`report_service.py`): send the transcript + hints + a JSON schema to the LLM and ask for JSON only.
5. **Validate** with Pydantic. If invalid, retry once with the error message, otherwise return a clear error.

## 4. LLM providers (`llm/`)
- `base.py`: interface `LLMProvider.generate_json(prompt, schema) -> dict`
- `claude.py`: **default** (`claude-haiku-5-5`, less than 1 cent per report; no disk space needed)
- `ollama.py` / `openai.py`: optional, chosen with `LLM_PROVIDER` in `.env` (Ollama = free and local, but needs ~2 GB disk)
This shows clean design (interface + interchangeable implementations).

> Decision 2026-11-18: Claude is the default instead of Ollama (only ~4 GB free disk, better accuracy).

## 5. API
| Method | Route | Purpose |
|---|---|---|
| POST | `/api/reports/generate` | Body `{ transcript }` → structured report (not saved) |
| POST | `/api/reports` | Save a report |
| GET | `/api/reports` | List saved reports |
| GET | `/api/health` | Health check (shows which LLM provider is active) |

## 6. Frontend
One screen:
```
┌─────────────────────────────────────────────┐
│  Voice to Report                             │
│            [ 🎤  Tap to speak  ]             │
│  Transcript: "Room 3 on the second floor…"   │
│  [ Edit ]                [ Generate report ] │
├─────────────────────────────────────────────┤
│  REPORT CARD                                 │
│  📍 2nd floor, room 3     🔴 High priority   │
│  Crack in the wall next to the window        │
│  Due: Fri 13.11.2026   Trade: Plasterer      │
│                                  [ Save ]    │
├─────────────────────────────────────────────┤
│  SAVED REPORTS (list)                        │
└─────────────────────────────────────────────┘
```
Style: clean, big buttons and text (usable with work gloves on a phone), mobile-first, works on desktop too.
Show clear messages when the microphone isn't allowed or the browser doesn't support speech recognition (Chrome works best).

Design decisions (2026-11-18):
- **Tap to start / tap to stop** instead of hold: easier with work gloves; the button shows a clear "Recording…" state.
- **Loading state** while the report is generated (button disabled + spinner text), and an **error message** if the LLM fails.
- **Empty state** for the saved list ("No reports yet").
- **Never guess:** fields the worker didn't say stay `null`, and the report card shows a **"Missing: …"** line (from the first prototype).
- Priority badge always shows **text + colour** (not colour alone), so it works for colour-blind users.

## 7. Testing
- **Backend (pytest):** date conversion, spaCy hints, JSON validation + retry, API routes (LLM mocked).
- **Frontend (Vitest):** ReportCard shows the right priority colour; the generate button is disabled while the transcript is empty.
- **Example set:** 10 sample transcripts in `backend/tests/samples.json` with expected fields, to measure how accurate the pipeline is (a simple evaluation, a real AI engineering practice).

## 8. Build plan (one step at a time, test + commit after each)
1. Project skeleton: frontend (Vite React TS) + backend (FastAPI) + health check
2. Frontend: record button + live transcript (Web Speech API)
3. Backend: Pydantic models + spaCy hints + date conversion + tests
4. Backend: LLM interface + Ollama provider + `/generate` endpoint + tests (mocked)
5. Frontend: connect generate → show ReportCard
6. Save/list reports with SQLite
7. Evaluation script with the 10 sample transcripts (print accuracy per field)
8. GitHub Actions CI (pytest + Vitest + build)
9. README with a demo GIF/video, architecture diagram, and "what I learned"
10. Optional: deploy (frontend on Vercel; backend only if free hosting works)

## 9. Definition of done
- I can speak a note in the browser and get a correct, structured report in a few seconds.
- It runs with Claude by default (Ollama optional for free local runs).
- Tests pass in CI.
- The README has a demo video and explains the NLP pipeline clearly.
