// All calls from the frontend to the FastAPI backend live here.

import type { Language, Report } from '../types/report'

export type Health = {
  status: string
  llm_provider: string
}

/** Read the backend's error message ("detail") so the user sees something useful. */
async function readError(response: Response): Promise<Error> {
  try {
    const body = await response.json()
    if (typeof body.detail === 'string') return new Error(body.detail)
  } catch {
    // not JSON, fall through
  }
  return new Error(`Backend error ${response.status}`)
}

export async function getHealth(): Promise<Health> {
  const response = await fetch('/api/health')
  if (!response.ok) throw await readError(response)
  return response.json()
}

export async function generateReport(transcript: string, language: Language): Promise<Report> {
  const response = await fetch('/api/reports/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ transcript, language }),
  })
  if (!response.ok) throw await readError(response)
  return response.json()
}
