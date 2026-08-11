export interface AskResponse {
  question: string
  sql: string | null
  columns: string[]
  rows: unknown[][]
  summary: string | null
  provider: string | null
  attempts: number
  error: string | null
}
