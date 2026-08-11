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
    <div className="min-h-screen bg-slate-50">
      <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6 sm:py-14">
        <header className="mb-8 text-center">
          <h1 className="text-3xl font-semibold text-slate-900 sm:text-4xl">Ask Your Data</h1>
          <p className="mt-2 text-slate-500">
            Ask a plain-English question about customers, products, and orders — no SQL required.
          </p>
        </header>

        <QuestionForm onAsk={handleAsk} loading={loading} />

        <div className="mt-8 flex flex-col gap-5">
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
