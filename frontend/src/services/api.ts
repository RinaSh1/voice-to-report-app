// All calls from the frontend to the FastAPI backend live here.

export type Health = {
  status: string
  llm_provider: string
}

export async function getHealth(): Promise<Health> {
  const response = await fetch('/api/health')
  if (!response.ok) {
    throw new Error(`Backend error ${response.status}`)
  }
  return response.json()
}
