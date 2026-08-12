export function LoadingState() {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-[4px] border border-hairline bg-white p-10 text-center">
      <div className="h-7 w-7 animate-spin rounded-full border-[3px] border-hairline border-t-accent" />
      <p className="font-sans text-ink">Looking through your data…</p>
      <p className="font-sans text-sm text-muted">This usually takes a few seconds.</p>
    </div>
  )
}
