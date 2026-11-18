/** "2026-11-20" -> "Fri 20.11.2026" (Swiss date format). */
export function formatDate(iso: string): string {
  const [year, month, day] = iso.split('-').map(Number)
  const date = new Date(year, month - 1, day)
  const weekday = date.toLocaleDateString('en-GB', { weekday: 'short' })
  return `${weekday} ${String(day).padStart(2, '0')}.${String(month).padStart(2, '0')}.${year}`
}
