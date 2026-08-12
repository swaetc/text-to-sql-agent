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
      <div className="mb-4 flex flex-wrap gap-2">
        {EXAMPLE_QUESTIONS.map((example) => (
          <button
            key={example}
            type="button"
            onClick={() => pickExample(example)}
            disabled={loading}
            className="rounded-[4px] border border-hairline bg-transparent px-3.5 py-1.5 font-sans text-[13px] text-muted transition-colors hover:border-accent hover:text-ink disabled:cursor-not-allowed disabled:opacity-50"
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
          className="flex-1 rounded-[4px] border border-hairline bg-white px-4 py-3 font-sans text-base text-ink outline-none transition-colors placeholder:text-muted/70 focus:border-accent disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="rounded-[4px] bg-accent px-6 py-3 font-sans text-base font-medium text-white transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? 'Thinking…' : 'Ask'}
        </button>
      </form>
    </div>
  )
}
