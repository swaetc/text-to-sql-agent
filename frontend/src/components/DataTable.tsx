import { useMemo, useState } from 'react'

interface Props {
  columns: string[]
  rows: unknown[][]
}

const PAGE_SIZE = 20

type SortDir = 'asc' | 'desc'

function formatCell(value: unknown): string {
  if (value === null || value === undefined) return '—'
  if (typeof value === 'number') {
    return Number.isInteger(value) ? value.toLocaleString() : value.toLocaleString(undefined, { maximumFractionDigits: 2 })
  }
  return String(value)
}

export function DataTable({ columns, rows }: Props) {
  const [sortCol, setSortCol] = useState<number | null>(null)
  const [sortDir, setSortDir] = useState<SortDir>('asc')
  const [page, setPage] = useState(0)

  const sortedRows = useMemo(() => {
    if (sortCol === null) return rows
    const copy = [...rows]
    copy.sort((a, b) => {
      const av = a[sortCol]
      const bv = b[sortCol]
      let cmp: number
      if (typeof av === 'number' && typeof bv === 'number') {
        cmp = av - bv
      } else {
        cmp = String(av).localeCompare(String(bv))
      }
      return sortDir === 'asc' ? cmp : -cmp
    })
    return copy
  }, [rows, sortCol, sortDir])

  const pageCount = Math.max(1, Math.ceil(sortedRows.length / PAGE_SIZE))
  const currentPage = Math.min(page, pageCount - 1)
  const pageRows = sortedRows.slice(currentPage * PAGE_SIZE, currentPage * PAGE_SIZE + PAGE_SIZE)

  function toggleSort(colIndex: number) {
    if (sortCol === colIndex) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortCol(colIndex)
      setSortDir('asc')
    }
    setPage(0)
  }

  if (rows.length === 0) {
    return (
      <p className="rounded-xl border border-slate-200 bg-white p-6 text-center text-sm text-slate-500">
        The query ran successfully but didn't return any rows.
      </p>
    )
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50">
              {columns.map((col, i) => (
                <th key={col} scope="col" className="text-left">
                  <button
                    type="button"
                    onClick={() => toggleSort(i)}
                    className="flex w-full items-center gap-1 px-4 py-2.5 text-left text-xs font-semibold uppercase tracking-wide text-slate-500 hover:text-slate-800"
                  >
                    {col}
                    <span className="text-slate-400">
                      {sortCol === i ? (sortDir === 'asc' ? '▲' : '▼') : ''}
                    </span>
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {pageRows.map((row, rowIndex) => (
              <tr
                key={currentPage * PAGE_SIZE + rowIndex}
                className="border-b border-slate-100 last:border-0 even:bg-slate-50/60"
              >
                {row.map((cell, cellIndex) => (
                  <td
                    key={cellIndex}
                    className="whitespace-nowrap px-4 py-2.5 text-slate-700 [font-variant-numeric:tabular-nums]"
                  >
                    {formatCell(cell)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {pageCount > 1 && (
        <div className="flex items-center justify-between gap-3 border-t border-slate-200 px-4 py-3 text-sm text-slate-500">
          <span>
            Showing {currentPage * PAGE_SIZE + 1}–
            {Math.min((currentPage + 1) * PAGE_SIZE, sortedRows.length)} of {sortedRows.length} rows
          </span>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={currentPage === 0}
              className="rounded-lg border border-slate-300 px-3 py-1.5 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Previous
            </button>
            <button
              type="button"
              onClick={() => setPage((p) => Math.min(pageCount - 1, p + 1))}
              disabled={currentPage >= pageCount - 1}
              className="rounded-lg border border-slate-300 px-3 py-1.5 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
