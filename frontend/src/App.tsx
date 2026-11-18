import { useEffect, useState } from 'react'

import { HealthStatus } from './components/HealthStatus'
import { RecordButton } from './components/RecordButton'
import { ReportCard } from './components/ReportCard'
import { ReportList } from './components/ReportList'
import { TranscriptView } from './components/TranscriptView'
import { useSpeechRecognition, type Language } from './hooks/useSpeechRecognition'
import { generateReport, listReports, saveReport } from './services/api'
import type { Report, ReportItem } from './types/report'

const LANGUAGES: { code: Language; label: string }[] = [
  { code: 'en-US', label: 'English' },
  { code: 'de-DE', label: 'Deutsch' },
]

function App() {
  const [lang, setLang] = useState<Language>('en-US')
  const speech = useSpeechRecognition(lang)
  const [report, setReport] = useState<Report | null>(null)
  const [generating, setGenerating] = useState(false)
  const [generateError, setGenerateError] = useState<string | null>(null)
  const [saved, setSaved] = useState<ReportItem[]>([])
  const [listError, setListError] = useState<string | null>(null)
  const [saveState, setSaveState] = useState<'idle' | 'saving' | 'saved'>('idle')
  const [saveError, setSaveError] = useState<string | null>(null)

  useEffect(() => {
    listReports()
      .then(setSaved)
      .catch(() => setListError('Could not load saved reports.'))
  }, [])

  const canGenerate = speech.transcript.trim() !== '' && !speech.listening && !generating

  async function handleGenerate() {
    setGenerating(true)
    setGenerateError(null)
    setSaveState('idle')
    setSaveError(null)
    try {
      setReport(await generateReport(speech.transcript, lang === 'de-DE' ? 'de' : 'en'))
    } catch (error) {
      setGenerateError(error instanceof Error ? error.message : 'Something went wrong.')
    } finally {
      setGenerating(false)
    }
  }

  async function handleSave() {
    if (!report) return
    setSaveState('saving')
    setSaveError(null)
    try {
      const item = await saveReport(speech.transcript, report)
      setSaved((items) => [item, ...items])
      setSaveState('saved')
    } catch (error) {
      setSaveError(error instanceof Error ? error.message : 'Could not save.')
      setSaveState('idle')
    }
  }

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

        <button type="button" className="primary" disabled={!canGenerate} onClick={handleGenerate}>
          {generating ? 'Generating report…' : 'Generate report'}
        </button>

        {generateError && (
          <p className="notice" role="alert">
            {generateError}
          </p>
        )}
      </main>

      {report && (
        <section className="section" aria-live="polite">
          <ReportCard
            report={report}
            actions={
              <>
                {saveError && (
                  <p className="notice notice--inline" role="alert">
                    {saveError}
                  </p>
                )}
                <button type="button" className="secondary" disabled={saveState !== 'idle'} onClick={handleSave}>
                  {saveState === 'saving' ? 'Saving…' : saveState === 'saved' ? 'Saved ✓' : 'Save'}
                </button>
              </>
            }
          />
        </section>
      )}

      <ReportList items={saved} error={listError} />
    </div>
  )
}

export default App
