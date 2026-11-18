import type { ReactNode } from 'react'

import { formatDate } from '../../lib/formatDate'
import { PriorityBadge } from './PriorityBadge'
import type { Report } from './types'

const FIELD_LABELS: Record<string, string> = {
  location: 'location',
  priority: 'priority',
  due_date: 'due date',
  assigned_trade: 'trade',
}

type Props = {
  report: Report
  actions?: ReactNode
}

/** Shows one structured report. Fields the worker didn't say are listed as "Missing". */
export function ReportCard({ report, actions }: Props) {
  return (
    <article className="card" aria-label="Report">
      <div className="card__top">
        <span className="card__location">📍 {report.location ?? 'No location'}</span>
        <PriorityBadge priority={report.priority} />
      </div>

      <h2 className="card__issue">{report.issue}</h2>
      <p className="card__summary">{report.summary}</p>

      <dl className="card__facts">
        <div>
          <dt>Due</dt>
          <dd>{report.due_date ? formatDate(report.due_date) : '—'}</dd>
        </div>
        <div>
          <dt>Trade</dt>
          <dd>{report.assigned_trade ?? '—'}</dd>
        </div>
        <div>
          <dt>Category</dt>
          <dd>{report.category}</dd>
        </div>
      </dl>

      {report.missing_fields.length > 0 && (
        <p className="card__missing">
          Missing: {report.missing_fields.map((field) => FIELD_LABELS[field] ?? field).join(', ')}. Please check before sending.
        </p>
      )}

      {actions && <div className="card__actions">{actions}</div>}
    </article>
  )
}
