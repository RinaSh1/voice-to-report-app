import { getJson, postJson } from '../../lib/http'
import type { Language, Report, ReportItem } from './types'

export const generateReport = (transcript: string, language: Language) =>
  postJson<Report>('/api/reports/generate', { transcript, language })

export const saveReport = (transcript: string, report: Report) =>
  postJson<ReportItem>('/api/reports', { transcript, report })

export const listReports = () => getJson<ReportItem[]>('/api/reports')
