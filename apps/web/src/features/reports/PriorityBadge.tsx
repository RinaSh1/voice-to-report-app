import type { Priority } from './types'

/** Priority shown as text and colour, so it never relies on colour alone. */
export function PriorityBadge({ priority }: { priority: Priority | null }) {
  const level = priority?.toLowerCase() ?? 'none'
  return (
    <span className={`badge badge--${level}`}>
      <span className="dot" aria-hidden="true" />
      {priority ? `${priority} priority` : 'No priority'}
    </span>
  )
}
