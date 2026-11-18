import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { fakeApi } from '../test/fakeFetch'
import { installFakeSpeech, removeSpeech } from '../test/fakeSpeech'
import App from './App'

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
  fakeApi()
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
    const fetchMock = fakeApi({
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

  it("shows the API's error message", async () => {
    fakeApi({
      '/api/reports/generate': () => Response.json({ detail: 'Could not reach Claude.' }, { status: 502 }),
    })
    render(<App />)
    await userEvent.type(screen.getByLabelText('Transcript'), 'Crack in room 3')
    await userEvent.click(screen.getByRole('button', { name: 'Generate report' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Could not reach Claude.')
  })
})

describe('App save and list', () => {
  beforeEach(installFakeSpeech)

  const SAVED = { id: 7, created_at: '2026-11-18T09:30:00Z', transcript: 'old note', report: { ...REPORT, issue: 'Old crack' } }

  it('shows an empty state when nothing is saved', async () => {
    render(<App />)
    expect(await screen.findByText(/No reports yet/)).toBeInTheDocument()
  })

  it('lists saved reports from the API', async () => {
    fakeApi({ '/api/reports': () => Response.json([SAVED]) })
    render(<App />)
    expect(await screen.findByText('Old crack')).toBeInTheDocument()
  })

  it('saves the generated report and puts it at the top of the list', async () => {
    const fetchMock = fakeApi({
      '/api/reports/generate': () => Response.json(REPORT),
      '/api/reports': (init) =>
        init?.method === 'POST'
          ? Response.json({ ...SAVED, id: 8, report: REPORT }, { status: 201 })
          : Response.json([SAVED]),
    })
    render(<App />)
    await userEvent.type(screen.getByLabelText('Transcript'), 'Socket in room 12 broken')
    await userEvent.click(screen.getByRole('button', { name: 'Generate report' }))
    await userEvent.click(await screen.findByRole('button', { name: 'Save' }))

    expect(await screen.findByRole('button', { name: 'Saved ✓' })).toBeDisabled()
    const post = fetchMock.mock.calls.find(([url, init]) => url === '/api/reports' && init?.method === 'POST')!
    expect(JSON.parse(post[1]!.body as string).transcript).toBe('Socket in room 12 broken')
    const rows = screen.getAllByRole('listitem')
    expect(rows[0]).toHaveTextContent('Broken socket')
    expect(rows[1]).toHaveTextContent('Old crack')
  })
})
