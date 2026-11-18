import type { SpeechLanguage } from './useSpeechRecognition'

const LANGUAGES: { code: SpeechLanguage; label: string }[] = [
  { code: 'en-US', label: 'English' },
  { code: 'de-DE', label: 'Deutsch' },
]

type Props = {
  value: SpeechLanguage
  disabled: boolean
  onChange: (language: SpeechLanguage) => void
}

export function LanguageSwitch({ value, disabled, onChange }: Props) {
  return (
    <div className="langs" role="group" aria-label="Spoken language">
      {LANGUAGES.map(({ code, label }) => (
        <button
          key={code}
          type="button"
          className="lang"
          aria-pressed={value === code}
          disabled={disabled}
          onClick={() => onChange(code)}
        >
          {label}
        </button>
      ))}
    </div>
  )
}
