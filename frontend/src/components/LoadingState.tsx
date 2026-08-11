export function LoadingState() {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-slate-200 bg-white p-10 text-center">
      <div className="h-8 w-8 animate-spin rounded-full border-[3px] border-blue-200 border-t-blue-600" />
      <p className="text-slate-600">Looking through your data…</p>
      <p className="text-sm text-slate-400">This usually takes a few seconds.</p>
    </div>
  )
}
