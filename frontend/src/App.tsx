import { useState } from 'react'
import { AnswerCard } from './components/AnswerCard'
import { DataTable } from './components/DataTable'
import { DetailsSection } from './components/DetailsSection'
import { ErrorState } from './components/ErrorState'
import { LoadingState } from './components/LoadingState'
import { QuestionForm } from './components/QuestionForm'
import { ResultChart } from './components/ResultChart'
import { askQuestion, FriendlyError } from './lib/api'
import { detectChartShape } from './lib/chartShape'
import type { AskResponse } from './types'

export default function App() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AskResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handleAsk(question: string) {
    setLoading(true)
    setError(null)
    try {
      const data = await askQuestion(question)
      setResult(data)
    } catch (err) {
      setResult(null)
      setError(
        err instanceof FriendlyError
          ? err.message
          : 'Something unexpected happened. Please try again.',
      )
    } finally {
      setLoading(false)
    }
  }

  const chartShape = result ? detectChartShape(result.columns, result.rows) : null

  return (
    <div className="min-h-screen bg-paper">
      <div className="mx-auto max-w-[720px] px-5 py-14 sm:px-6 sm:py-20">
        <header className="mb-12 border-b border-hairline pb-10 text-center">
          <p className="font-sans text-xs font-semibold uppercase tracking-[0.15em] text-accent">
            Field notes from your database
          </p>
          <h1 className="mt-3 font-display text-4xl font-bold leading-[1.15] text-ink sm:text-5xl">
            The Data Desk
          </h1>
          <p className="mx-auto mt-4 max-w-md text-[15px] text-muted">
            Plain-English reporting on customers, orders, and revenue — no SQL
            required.
          </p>
        </header>

        <QuestionForm onAsk={handleAsk} loading={loading} />

        <div className="mt-10 flex flex-col gap-8">
          {loading && <LoadingState />}
          {!loading && error && <ErrorState message={error} />}

          {!loading && !error && result && (
            <>
              <AnswerCard question={result.question} summary={result.summary} />

              {chartShape && <ResultChart shape={chartShape} />}

              <DataTable columns={result.columns} rows={result.rows} />

              <DetailsSection sql={result.sql} provider={result.provider} attempts={result.attempts} />
            </>
          )}
        </div>
      </div>
    </div>
  )
}
