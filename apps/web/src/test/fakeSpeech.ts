import { vi } from 'vitest'

import type { SpeechRecognitionLike } from '../features/recording/useSpeechRecognition'

/** A fake browser speech recogniser, so tests can "speak" without a microphone. */
export class FakeRecognition implements SpeechRecognitionLike {
  static last: FakeRecognition | null = null

  lang = ''
  continuous = false
  interimResults = false
  onresult: SpeechRecognitionLike['onresult'] = null
  onerror: SpeechRecognitionLike['onerror'] = null
  onend: SpeechRecognitionLike['onend'] = null
  start = vi.fn()
  stop = vi.fn(() => this.onend?.())

  constructor() {
    FakeRecognition.last = this
  }

  /** Pretend the user said `text`. `isFinal: false` means it is still being recognised. */
  say(text: string, isFinal: boolean) {
    this.onresult?.({ resultIndex: 0, results: [{ isFinal, 0: { transcript: text } }] })
  }
}

export function installFakeSpeech() {
  FakeRecognition.last = null
  window.webkitSpeechRecognition = FakeRecognition
}

export function removeSpeech() {
  delete window.SpeechRecognition
  delete window.webkitSpeechRecognition
}
