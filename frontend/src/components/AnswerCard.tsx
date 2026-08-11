interface Props {
  question: string
  summary: string | null
}

export function AnswerCard({ question, summary }: Props) {
  return (
    <div className="rounded-2xl border border-blue-100 bg-gradient-to-br from-blue-50 to-white p-6 sm:p-8">
      <p className="text-sm font-medium uppercase tracking-wide text-blue-600">
        You asked
      </p>
      <p className="mt-1 text-sm text-slate-500 sm:text-base">{question}</p>

      <div className="mt-5 border-t border-blue-100 pt-5">
        {summary ? (
          <p className="text-2xl font-semibold leading-snug text-slate-900 sm:text-3xl">
            {summary}
          </p>
        ) : (
          <p className="text-lg text-slate-500">
            The data came back, but we couldn't put together a written summary this
            time — the numbers below have the full answer.
          </p>
        )}
      </div>
    </div>
  )
}
