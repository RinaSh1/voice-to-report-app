type Props = {
  transcript: string
  interim: string
  listening: boolean
  onChange: (text: string) => void
}

/** Shows the transcript. The user can correct it before generating a report. */
export function TranscriptView({ transcript, interim, listening, onChange }: Props) {
  return (
    <div className="transcript">
      <div className="transcript__head">
        <label htmlFor="transcript">Transcript</label>
        {transcript && !listening && (
          <button type="button" className="link" onClick={() => onChange('')}>
            Clear
          </button>
        )}
      </div>
      <textarea
        id="transcript"
        value={transcript}
        onChange={(event) => onChange(event.target.value)}
        readOnly={listening}
        rows={4}
        placeholder="Your words appear here. You can also type or correct them."
      />
      {interim && (
        <p className="transcript__interim" aria-live="polite">
          {interim}…
        </p>
      )}
    </div>
  )
}
