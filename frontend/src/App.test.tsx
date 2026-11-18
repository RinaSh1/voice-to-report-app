import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import App from './App'
import { installFakeSpeech, removeSpeech } from './test/fakeSpeech'

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(
    new Response(JSON.stringify({ status: 'ok', llm_provider: 'claude' })),
  ))
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
