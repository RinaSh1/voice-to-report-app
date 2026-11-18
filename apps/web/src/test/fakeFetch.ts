import { vi } from 'vitest'

type Handler = (init?: RequestInit) => Response | Promise<Response>

const DEFAULTS: Record<string, Handler> = {
  '/api/health': () => Response.json({ status: 'ok', llm_provider: 'claude' }),
  '/api/reports': () => Response.json([]), // no saved reports yet
}

/** Fake the API: map a URL to an answer. Health and an empty report list work by default. */
export function fakeApi(routes: Record<string, Handler> = {}) {
  const fetchMock = vi.fn(async (url: string, init?: RequestInit) => {
    const handler = routes[url] ?? DEFAULTS[url]
    if (!handler) throw new Error(`No fake for ${url}`)
    return handler(init)
  })
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}
