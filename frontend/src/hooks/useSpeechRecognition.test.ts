import { act, renderHook } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'

import { FakeRecognition, installFakeSpeech, removeSpeech } from '../test/fakeSpeech'
import { useSpeechRecognition } from './useSpeechRecognition'

describe('useSpeechRecognition', () => {
  beforeEach(installFakeSpeech)
  afterEach(removeSpeech)

  it('starts listening in the chosen language', () => {
    const { result } = renderHook(() => useSpeechRecognition('de-DE'))
    act(() => result.current.start())

    expect(result.current.listening).toBe(true)
    expect(FakeRecognition.last?.lang).toBe('de-DE')
    expect(FakeRecognition.last?.start).toHaveBeenCalled()
  })

  it('shows words live, then adds them to the transcript when final', () => {
    const { result } = renderHook(() => useSpeechRecognition('en-US'))
    act(() => result.current.start())

    act(() => FakeRecognition.last?.say('the socket in', false))
    expect(result.current.interim).toBe('the socket in')
    expect(result.current.transcript).toBe('')

    act(() => FakeRecognition.last?.say('The socket in room 12 is broken.', true))
    expect(result.current.transcript).toBe('The socket in room 12 is broken.')
  })

  it('adds a new recording after the text that is already there', () => {
    const { result } = renderHook(() => useSpeechRecognition('en-US'))
    act(() => result.current.setTranscript('First note.'))
    act(() => result.current.start())
    act(() => FakeRecognition.last?.say('Second note.', true))

    expect(result.current.transcript).toBe('First note. Second note.')
  })

  it('stops listening when stopped', () => {
    const { result } = renderHook(() => useSpeechRecognition('en-US'))
    act(() => result.current.start())
    act(() => result.current.stop())

    expect(result.current.listening).toBe(false)
  })

  it('explains a blocked microphone in plain words', () => {
    const { result } = renderHook(() => useSpeechRecognition('en-US'))
    act(() => result.current.start())
    act(() => FakeRecognition.last?.onerror?.({ error: 'not-allowed' }))

    expect(result.current.error).toMatch(/Microphone access is blocked/)
  })

  it('reports when the browser has no speech recognition', () => {
    removeSpeech()
    const { result } = renderHook(() => useSpeechRecognition('en-US'))

    expect(result.current.supported).toBe(false)
  })
})
