import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { formatDate } from '../../lib/formatDate'
import { ReportCard } from './ReportCard'
import type { Report } from './types'

const REPORT: Report = {
  location: '2nd floor, room 3',
  issue: 'Crack in the wall next to the window',
  category: 'Damage',
  priority: 'High',
  due_date: '2026-11-20',
  assigned_trade: 'Plasterer',
  summary: 'Crack in wall next to window in room 3, fix by Friday.',
  language: 'en',
  missing_fields: [],
}

describe('ReportCard', () => {
  it.each([
    ['High', 'badge--high'],
    ['Medium', 'badge--medium'],
    ['Low', 'badge--low'],
  ] as const)('shows %s priority with text and the right colour', (priority, className) => {
    render(<ReportCard report={{ ...REPORT, priority }} />)
    expect(screen.getByText(`${priority} priority`)).toHaveClass('badge', className)
  })

  it('shows the fields and a Swiss date', () => {
    render(<ReportCard report={REPORT} />)
    expect(screen.getByText('📍 2nd floor, room 3')).toBeInTheDocument()
    expect(screen.getByText('Fri 20.11.2026')).toBeInTheDocument()
    expect(screen.getByText('Plasterer')).toBeInTheDocument()
  })

  it('lists what the worker did not say', () => {
    render(<ReportCard report={{ ...REPORT, priority: null, assigned_trade: null, missing_fields: ['priority', 'assigned_trade'] }} />)
    expect(screen.getByText('No priority')).toHaveClass('badge--none')
    expect(screen.getByText(/Missing: priority, trade/)).toBeInTheDocument()
  })

  it('formats dates as weekday dd.mm.yyyy', () => {
    expect(formatDate('2026-01-05')).toBe('Mon 05.01.2026')
  })
})
