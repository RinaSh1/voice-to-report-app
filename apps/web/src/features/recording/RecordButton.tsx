type Props = {
  listening: boolean
  disabled?: boolean
  onClick: () => void
}

/** The big microphone button: tap to start, tap again to stop (easy with work gloves). */
export function RecordButton({ listening, disabled = false, onClick }: Props) {
  return (
    <button
      type="button"
      className={`record ${listening ? 'record--on' : ''}`}
      aria-pressed={listening}
      disabled={disabled}
      onClick={onClick}
    >
      <svg className="record__icon" viewBox="0 0 24 24" aria-hidden="true">
        {listening ? (
          <rect x="7" y="7" width="10" height="10" rx="2" />
        ) : (
          <>
            <rect x="9" y="3" width="6" height="11" rx="3" />
            <path d="M6 11a6 6 0 0 0 12 0M12 17v4M9 21h6" fill="none" strokeWidth="2" strokeLinecap="round" />
          </>
        )}
      </svg>
      <span className="record__label">{listening ? 'Recording… tap to stop' : 'Tap to speak'}</span>
    </button>
  )
}
