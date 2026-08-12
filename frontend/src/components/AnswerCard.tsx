interface Props {
  question: string
  summary: string | null
}

export function AnswerCard({ question, summary }: Props) {
  return (
    <div className="rounded-[4px] border border-hairline bg-white p-6 sm:p-8">
      <p className="font-sans text-xs font-semibold uppercase tracking-[0.05em] text-accent">
        You asked
      </p>
      <p className="mt-1.5 font-sans text-sm text-muted sm:text-[15px]">{question}</p>

      <div className="mt-5 border-t border-hairline pt-6">
        {summary ? (
          <p className="font-display text-[32px] font-semibold leading-[1.2] text-ink sm:text-[38px]">
            {summary}
          </p>
        ) : (
          <p className="font-sans text-lg text-muted">
            The data came back, but we couldn't put together a written summary this
            time — the numbers below have the full answer.
          </p>
        )}
      </div>
    </div>
  )
}
