import { useState } from 'react'

import { HealthStatus } from '../features/health'
import {
  LanguageSwitch,
  RecordButton,
  type SpeechLanguage,
  TranscriptView,
  useSpeechRecognition,
} from '../features/recording'
import { ReportCard, ReportList, useReports } from '../features/reports'

const toReportLanguage = (language: SpeechLanguage) => (language === 'de-DE' ? 'de' : 'en')

const SAVE_LABEL = { idle: 'Save', saving: 'Saving…', saved: 'Saved ✓' } as const

function App() {
  const [language, setLanguage] = useState<SpeechLanguage>('en-US')
  const speech = useSpeechRecognition(language)
  const reports = useReports()

  const canGenerate = speech.transcript.trim() !== '' && !speech.listening && !reports.generating

  return (
    <div className="app">
      <header className="header">
        <h1>Voice to Report</h1>
        <p className="tagline">Speak a site note. Get a clean, structured report.</p>
        <HealthStatus />
      </header>

      <main className="panel">
        <LanguageSwitch value={language} disabled={speech.listening} onChange={setLanguage} />

        {speech.supported ? (
          <RecordButton listening={speech.listening} onClick={speech.listening ? speech.stop : speech.start} />
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

        <button
          type="button"
          className="primary"
          disabled={!canGenerate}
          onClick={() => reports.generate(speech.transcript, toReportLanguage(language))}
        >
          {reports.generating ? 'Generating report…' : 'Generate report'}
        </button>

        {reports.generateError && (
          <p className="notice" role="alert">
            {reports.generateError}
          </p>
        )}
      </main>

      {reports.report && (
        <section className="section" aria-live="polite">
          <ReportCard
            report={reports.report}
            actions={
              <>
                {reports.saveError && (
                  <p className="notice notice--inline" role="alert">
                    {reports.saveError}
                  </p>
                )}
                <button
                  type="button"
                  className="secondary"
                  disabled={reports.saveState !== 'idle'}
                  onClick={() => reports.save(speech.transcript)}
                >
                  {SAVE_LABEL[reports.saveState]}
                </button>
              </>
            }
          />
        </section>
      )}

      <ReportList items={reports.saved} error={reports.listError} />
    </div>
  )
}

export default App
