import { render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { HealthStatus } from './HealthStatus'

afterEach(() => vi.unstubAllGlobals())

describe('HealthStatus', () => {
  it('shows the active LLM provider when the API answers', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ status: 'ok', llm_provider: 'claude' })),
    ))
    render(<HealthStatus />)
    expect(await screen.findByText('claude')).toBeInTheDocument()
  })

  it('shows a clear message when the API is down', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')))
    render(<HealthStatus />)
    expect(await screen.findByRole('alert')).toHaveTextContent('API not reachable')
  })
})
