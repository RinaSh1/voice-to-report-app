import type { ReportItem } from '../types/report'
import { PriorityBadge } from './ReportCard'

type Props = {
  items: ReportItem[]
  error: string | null
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleString('de-CH', { dateStyle: 'short', timeStyle: 'short' })
}

/** Saved reports, newest first. */
export function ReportList({ items, error }: Props) {
  return (
    <section className="section" aria-labelledby="saved-heading">
      <h2 id="saved-heading" className="section__title">
        Saved reports {items.length > 0 && <span className="count">{items.length}</span>}
      </h2>

      {error && (
        <p className="notice" role="alert">
          {error}
        </p>
      )}

      {!error && items.length === 0 && <p className="empty">No reports yet. Record a note and save its report.</p>}

      <ul className="list">
        {items.map(({ id, created_at, report }) => (
          <li key={id} className="row">
            <div className="row__main">
              <p className="row__issue">{report.issue}</p>
              <p className="row__meta">
                {report.location ?? 'No location'} · {formatTime(created_at)}
                {report.missing_fields.length > 0 && <> · {report.missing_fields.length} missing</>}
              </p>
            </div>
            <PriorityBadge priority={report.priority} />
          </li>
        ))}
      </ul>
    </section>
  )
}
