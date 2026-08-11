import { useState } from 'react'

interface Props {
  sql: string | null
  provider: string | null
  attempts: number
}

export function DetailsSection({ sql, provider, attempts }: Props) {
  const [open, setOpen] = useState(false)

  return (
    <div className="rounded-xl border border-slate-200 bg-white">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between gap-2 px-4 py-3 text-left text-sm font-medium text-slate-600 hover:text-slate-900"
        aria-expanded={open}
      >
        <span>How was this calculated?</span>
        <svg
          className={`h-4 w-4 shrink-0 transition-transform ${open ? 'rotate-180' : ''}`}
          viewBox="0 0 20 20"
          fill="none"
          stroke="currentColor"
        >
          <path d="M5 7.5 10 12.5 15 7.5" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>

      {open && (
        <div className="border-t border-slate-200 px-4 py-4">
          <dl className="mb-3 flex flex-wrap gap-x-6 gap-y-1 text-xs text-slate-500">
            {provider && (
              <div>
                <dt className="inline font-medium text-slate-600">Model: </dt>
                <dd className="inline">{provider}</dd>
              </div>
            )}
            <div>
              <dt className="inline font-medium text-slate-600">Attempts: </dt>
              <dd className="inline">{attempts}</dd>
            </div>
          </dl>
          <pre className="overflow-x-auto rounded-lg bg-slate-900 p-3 text-xs leading-relaxed text-slate-100">
            <code>{sql ?? 'No SQL was generated.'}</code>
          </pre>
        </div>
      )}
    </div>
  )
}
