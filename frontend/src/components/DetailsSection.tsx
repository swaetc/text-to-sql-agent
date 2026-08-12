import { ChevronDown } from 'lucide-react'
import { useState } from 'react'

interface Props {
  sql: string | null
  provider: string | null
  attempts: number
}

export function DetailsSection({ sql, provider, attempts }: Props) {
  const [open, setOpen] = useState(false)

  return (
    <div className="border-t border-hairline pt-4">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1.5 font-sans text-sm text-muted underline decoration-hairline decoration-1 underline-offset-4 transition-colors hover:text-accent hover:decoration-accent"
        aria-expanded={open}
      >
        How was this calculated?
        <ChevronDown
          className={`h-3.5 w-3.5 shrink-0 transition-transform ${open ? 'rotate-180' : ''}`}
          strokeWidth={2}
        />
      </button>

      {open && (
        <div className="mt-4">
          <dl className="mb-3 flex flex-wrap gap-x-6 gap-y-1 font-sans text-xs text-muted">
            {provider && (
              <div>
                <dt className="inline font-medium text-ink">Model: </dt>
                <dd className="inline font-mono">{provider}</dd>
              </div>
            )}
            <div>
              <dt className="inline font-medium text-ink">Attempts: </dt>
              <dd className="inline font-mono">{attempts}</dd>
            </div>
          </dl>
          <pre className="overflow-x-auto rounded-[4px] bg-ink p-3.5 font-mono text-xs leading-relaxed text-paper">
            <code>{sql ?? 'No SQL was generated.'}</code>
          </pre>
        </div>
      )}
    </div>
  )
}
