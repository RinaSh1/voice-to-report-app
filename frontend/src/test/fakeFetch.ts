import { vi } from 'vitest'

type Handler = (init?: RequestInit) => Response | Promise<Response>

/** Fake the backend: map a URL to an answer. The health check always answers "ok". */
export function fakeBackend(routes: Record<string, Handler> = {}) {
  const fetchMock = vi.fn(async (url: string, init?: RequestInit) => {
    if (url === '/api/health') return Response.json({ status: 'ok', llm_provider: 'claude' })
    const handler = routes[url]
    if (!handler) throw new Error(`No fake for ${url}`)
    return handler(init)
  })
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}
