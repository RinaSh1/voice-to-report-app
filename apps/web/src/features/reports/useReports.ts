import { useCallback, useEffect, useState } from 'react'

import { generateReport, listReports, saveReport } from './api'
import type { Language, Report, ReportItem } from './types'

type SaveState = 'idle' | 'saving' | 'saved'

const message = (error: unknown, fallback: string) => (error instanceof Error ? error.message : fallback)

/** Generate, save and list reports. Keeps all report state out of the UI components. */
export function useReports() {
  const [report, setReport] = useState<Report | null>(null)
  const [generating, setGenerating] = useState(false)
  const [generateError, setGenerateError] = useState<string | null>(null)

  const [saveState, setSaveState] = useState<SaveState>('idle')
  const [saveError, setSaveError] = useState<string | null>(null)

  const [saved, setSaved] = useState<ReportItem[]>([])
  const [listError, setListError] = useState<string | null>(null)

  useEffect(() => {
    listReports()
      .then(setSaved)
      .catch(() => setListError('Could not load saved reports.'))
  }, [])

  const generate = useCallback(async (transcript: string, language: Language) => {
    setGenerating(true)
    setGenerateError(null)
    setSaveState('idle')
    setSaveError(null)
    try {
      setReport(await generateReport(transcript, language))
    } catch (error) {
      setGenerateError(message(error, 'Something went wrong.'))
    } finally {
      setGenerating(false)
    }
  }, [])

  const save = useCallback(
    async (transcript: string) => {
      if (!report) return
      setSaveState('saving')
      setSaveError(null)
      try {
        const item = await saveReport(transcript, report)
        setSaved((items) => [item, ...items])
        setSaveState('saved')
      } catch (error) {
        setSaveError(message(error, 'Could not save.'))
        setSaveState('idle')
      }
    },
    [report],
  )

  return { report, generating, generateError, generate, saveState, saveError, save, saved, listError }
}
