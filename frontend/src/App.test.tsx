import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import App from './App'
import { fakeBackend } from './test/fakeFetch'
import { installFakeSpeech, removeSpeech } from './test/fakeSpeech'

const REPORT = {
  location: 'Room 12',
  issue: 'Broken socket',
  category: 'Damage',
  priority: null,
  due_date: null,
  assigned_trade: null,
  summary: 'Socket in room 12 is broken.',
  language: 'en',
  missing_fields: ['priority', 'due_date', 'assigned_trade'],
}

beforeEach(() => {
  fakeBackend()
})

afterEach(() => {
  vi.unstubAllGlobals()
  removeSpeech()
})

describe('App recording', () => {
  it('switches the button to "stop" while recording and locks the language', async () => {
    installFakeSpeech()
    render(<App />)

    await userEvent.click(screen.getByRole('button', { name: 'Tap to speak' }))

    expect(screen.getByRole('button', { name: /Recording… tap to stop/ })).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByRole('button', { name: 'Deutsch' })).toBeDisabled()
  })

  it('asks for Chrome when speech recognition is missing, but typing still works', async () => {
    removeSpeech()
    render(<App />)

    expect(screen.getByRole('alert')).toHaveTextContent('Please use Google Chrome')
    await userEvent.type(screen.getByLabelText('Transcript'), 'Crack in the kitchen wall')
    expect(screen.getByLabelText('Transcript')).toHaveValue('Crack in the kitchen wall')
  })
})

describe('App generate report', () => {
  beforeEach(installFakeSpeech)

  it('disables "Generate report" while the transcript is empty', () => {
    render(<App />)
    expect(screen.getByRole('button', { name: 'Generate report' })).toBeDisabled()
  })

  it('sends the transcript and language, then shows the report card', async () => {
    let resolve!: (response: Response) => void
    const fetchMock = fakeBackend({
      '/api/reports/generate': () => new Promise<Response>((r) => (resolve = r)),
    })
    render(<App />)
    await userEvent.click(screen.getByRole('button', { name: 'Deutsch' }))
    await userEvent.type(screen.getByLabelText('Transcript'), 'Steckdose in Raum 12 kaputt')
    await userEvent.click(screen.getByRole('button', { name: 'Generate report' }))

    // Loading state while waiting for the AI
    expect(screen.getByRole('button', { name: 'Generating report…' })).toBeDisabled()
    const body = JSON.parse(fetchMock.mock.calls.at(-1)![1]!.body as string)
    expect(body).toEqual({ transcript: 'Steckdose in Raum 12 kaputt', language: 'de' })

    resolve(Response.json(REPORT))
    expect(await screen.findByRole('article', { name: 'Report' })).toHaveTextContent('Broken socket')
    expect(screen.getByText(/Missing: priority, due date, trade/)).toBeInTheDocument()
  })

  it("shows the backend's error message", async () => {
    fakeBackend({
      '/api/reports/generate': () => Response.json({ detail: 'Could not reach Claude.' }, { status: 502 }),
    })
    render(<App />)
    await userEvent.type(screen.getByLabelText('Transcript'), 'Crack in room 3')
    await userEvent.click(screen.getByRole('button', { name: 'Generate report' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Could not reach Claude.')
  })
})
