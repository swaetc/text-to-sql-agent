import { useState } from 'react'
import type { FormEvent } from 'react'
import { EXAMPLE_QUESTIONS } from '../lib/examples'

interface Props {
  onAsk: (question: string) => void
  loading: boolean
}

export function QuestionForm({ onAsk, loading }: Props) {
  const [question, setQuestion] = useState('')

  function submit(e: FormEvent) {
    e.preventDefault()
    const trimmed = question.trim()
    if (!trimmed || loading) return
    onAsk(trimmed)
  }

  function pickExample(example: string) {
    setQuestion(example)
    if (!loading) onAsk(example)
  }

  return (
    <div className="w-full">
      <div className="mb-3 flex flex-wrap gap-2">
        {EXAMPLE_QUESTIONS.map((example) => (
          <button
            key={example}
            type="button"
            onClick={() => pickExample(example)}
            disabled={loading}
            className="rounded-full border border-slate-300 bg-white px-3.5 py-1.5 text-sm text-slate-600 transition hover:border-blue-400 hover:text-blue-700 disabled:cursor-not-allowed disabled:opacity-50 sm:text-[13px]"
          >
            {example}
          </button>
        ))}
      </div>

      <form onSubmit={submit} className="flex flex-col gap-3 sm:flex-row">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about your data…"
          disabled={loading}
          className="flex-1 rounded-xl border border-slate-300 bg-white px-4 py-3 text-base text-slate-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="rounded-xl bg-blue-600 px-6 py-3 text-base font-medium text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? 'Thinking…' : 'Ask'}
        </button>
      </form>
    </div>
  )
}
