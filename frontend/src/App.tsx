import { useState } from 'react'

import { HealthStatus } from './components/HealthStatus'
import { RecordButton } from './components/RecordButton'
import { TranscriptView } from './components/TranscriptView'
import { useSpeechRecognition, type Language } from './hooks/useSpeechRecognition'

const LANGUAGES: { code: Language; label: string }[] = [
  { code: 'en-US', label: 'English' },
  { code: 'de-DE', label: 'Deutsch' },
]

function App() {
  const [lang, setLang] = useState<Language>('en-US')
  const speech = useSpeechRecognition(lang)

  return (
    <div className="app">
      <header className="header">
        <h1>Voice to Report</h1>
        <p className="tagline">Speak a site note. Get a clean, structured report.</p>
        <HealthStatus />
      </header>

      <main className="panel">
        <div className="langs" role="group" aria-label="Spoken language">
          {LANGUAGES.map(({ code, label }) => (
            <button
              key={code}
              type="button"
              className="lang"
              aria-pressed={lang === code}
              disabled={speech.listening}
              onClick={() => setLang(code)}
            >
              {label}
            </button>
          ))}
        </div>

        {speech.supported ? (
          <RecordButton
            listening={speech.listening}
            onClick={speech.listening ? speech.stop : speech.start}
          />
        ) : (
          <p className="notice" role="alert">
            This browser can't do speech recognition. Please use Google Chrome, or type the note below.
          </p>
        )}

        {speech.error && (
          <p className="notice" role="alert">
            {speech.error}
          </p>
        )}

        <TranscriptView
          transcript={speech.transcript}
          interim={speech.interim}
          listening={speech.listening}
          onChange={speech.setTranscript}
        />
      </main>
    </div>
  )
}

export default App
