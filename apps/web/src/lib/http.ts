/** Minimal JSON client for the API. Errors carry the API's "detail" message when there is one. */

export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function toError(response: Response): Promise<ApiError> {
  try {
    const body = await response.json()
    if (typeof body.detail === 'string') return new ApiError(body.detail, response.status)
  } catch {
    // body is not JSON
  }
  return new ApiError(`Request failed (${response.status})`, response.status)
}

export async function getJson<T>(url: string): Promise<T> {
  const response = await fetch(url)
  if (!response.ok) throw await toError(response)
  return response.json() as Promise<T>
}

export async function postJson<T>(url: string, body: unknown): Promise<T> {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!response.ok) throw await toError(response)
  return response.json() as Promise<T>
}
