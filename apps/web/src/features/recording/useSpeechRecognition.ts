import { useCallback, useEffect, useRef, useState } from 'react'

// The Web Speech API is not in TypeScript's built-in types, so we describe the small part we use.
type SpeechResult = { isFinal: boolean; 0: { transcript: string } }
type SpeechResultEvent = { resultIndex: number; results: ArrayLike<SpeechResult> }
type SpeechErrorEvent = { error: string }

export type SpeechRecognitionLike = {
  lang: string
  continuous: boolean
  interimResults: boolean
  onresult: ((event: SpeechResultEvent) => void) | null
  onerror: ((event: SpeechErrorEvent) => void) | null
  onend: (() => void) | null
  start: () => void
  stop: () => void
}

type SpeechRecognitionConstructor = new () => SpeechRecognitionLike

declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionConstructor
    webkitSpeechRecognition?: SpeechRecognitionConstructor
  }
}

export type SpeechLanguage = 'en-US' | 'de-DE'

/** Turn the browser's error codes into messages a worker understands. */
export function errorMessage(code: string): string {
  switch (code) {
    case 'not-allowed':
    case 'service-not-allowed':
      return 'Microphone access is blocked. Allow the microphone in the browser address bar, then try again.'
    case 'no-speech':
      return 'No speech heard. Tap the button and speak a little louder.'
    case 'audio-capture':
      return 'No microphone found. Check that one is connected.'
    case 'network':
      return 'Speech recognition needs an internet connection (Chrome sends the audio to Google).'
    default:
      return `Speech recognition stopped (${code}). Please try again.`
  }
}

function getConstructor(): SpeechRecognitionConstructor | undefined {
  return window.SpeechRecognition ?? window.webkitSpeechRecognition
}

/** Join two pieces of text with exactly one space. */
function join(a: string, b: string): string {
  return [a.trim(), b.trim()].filter(Boolean).join(' ')
}

/**
 * Live speech-to-text in the browser.
 * - `transcript`: the finished text (the user may also edit it).
 * - `interim`: words still being recognised, shown greyed out while speaking.
 */
export function useSpeechRecognition(lang: SpeechLanguage) {
  const supported = getConstructor() !== undefined
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null)
  const [listening, setListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [interim, setInterim] = useState('')
  const [error, setError] = useState<string | null>(null)

  const start = useCallback(() => {
    const Recognition = getConstructor()
    if (!Recognition) return

    const recognition = new Recognition()
    recognition.lang = lang
    recognition.continuous = true // keep listening through short pauses
    recognition.interimResults = true // show words while the user is still speaking

    recognition.onresult = (event) => {
      let finished = ''
      let pending = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        if (result.isFinal) finished = join(finished, result[0].transcript)
        else pending = join(pending, result[0].transcript)
      }
      if (finished) setTranscript((previous) => join(previous, finished))
      setInterim(pending)
    }
    recognition.onerror = (event) => {
      // "aborted" only means we stopped it ourselves.
      if (event.error !== 'aborted') setError(errorMessage(event.error))
    }
    recognition.onend = () => {
      setListening(false)
      setInterim('')
    }

    recognitionRef.current = recognition
    setError(null)
    setListening(true)
    recognition.start()
  }, [lang])

  const stop = useCallback(() => {
    recognitionRef.current?.stop()
  }, [])

  // Stop the microphone if the component disappears.
  useEffect(() => () => recognitionRef.current?.stop(), [])

  return { supported, listening, transcript, setTranscript, interim, error, start, stop }
}
