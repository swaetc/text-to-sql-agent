interface Props {
  message: string
}

export function ErrorState({ message }: Props) {
  return (
    <div className="flex flex-col items-center gap-2 rounded-[4px] border border-hairline bg-white p-8 text-center">
      <svg className="h-7 w-7 text-muted" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <circle cx="12" cy="12" r="9" strokeWidth="1.5" />
        <path d="M12 8v5" strokeWidth="1.5" strokeLinecap="round" />
        <circle cx="12" cy="16" r="0.75" fill="currentColor" stroke="none" />
      </svg>
      <p className="font-sans font-medium text-ink">{message}</p>
    </div>
  )
}
