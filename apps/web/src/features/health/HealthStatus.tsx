import { useEffect, useState } from 'react'

import { getHealth, type Health } from './api'

type State =
  | { kind: 'loading' }
  | { kind: 'ok'; health: Health }
  | { kind: 'error' }

/** Small status line: is the API running, and which LLM does it use? */
export function HealthStatus() {
  const [state, setState] = useState<State>({ kind: 'loading' })

  useEffect(() => {
    getHealth()
      .then((health) => setState({ kind: 'ok', health }))
      .catch(() => setState({ kind: 'error' }))
  }, [])

  if (state.kind === 'loading') {
    return <p className="status">Checking API…</p>
  }
  if (state.kind === 'error') {
    return (
      <p className="status status--error" role="alert">
        <span className="dot" aria-hidden="true" /> API not reachable. Start it with{' '}
        <code>uvicorn app.main:app --reload</code>
      </p>
    )
  }
  return (
    <p className="status status--ok">
      <span className="dot" aria-hidden="true" /> API connected · LLM:{' '}
      <strong>{state.health.llm_provider}</strong>
    </p>
  )
}
