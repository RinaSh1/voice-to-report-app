// Same shape as the Report model in backend/app/models.py.

export type Priority = 'High' | 'Medium' | 'Low'
export type Category = 'Damage' | 'Safety' | 'Material' | 'Task' | 'Other'
export type Language = 'en' | 'de'

export type Report = {
  location: string | null
  issue: string
  category: Category
  priority: Priority | null
  due_date: string | null // YYYY-MM-DD
  assigned_trade: string | null
  summary: string
  language: Language
  missing_fields: string[]
}

export type ReportItem = {
  id: number
  created_at: string // ISO date-time
  transcript: string
  report: Report
}
