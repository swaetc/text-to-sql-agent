export interface ChartShape {
  categoryIndex: number | null
  categoryLabel: string
  valueIndex: number
  valueLabel: string
  data: { category: string; value: number }[]
}

const MAX_CHART_ROWS = 25

function isNumeric(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value)
}

const ID_COLUMN_PATTERN = /(^id$)|(_id$)/i

/**
 * A result is chartable when it's exactly one numeric column, plus at most
 * one categorical column, over a small number of rows. Anything wider or
 * longer is a detail table, not a chart. Identifier columns (id, customer_id)
 * are ignored for this check — they're numeric but not a chartable metric.
 */
export function detectChartShape(columns: string[], rows: unknown[][]): ChartShape | null {
  const chartableIndexes = columns
    .map((name, i) => ({ name, i }))
    .filter(({ name }) => !ID_COLUMN_PATTERN.test(name))
    .map(({ i }) => i)

  if (chartableIndexes.length === 0 || chartableIndexes.length > 2) return null
  if (rows.length === 0 || rows.length > MAX_CHART_ROWS) return null

  const numericColumns: number[] = []
  const otherColumns: number[] = []

  chartableIndexes.forEach((colIndex) => {
    const values = rows.map((row) => row[colIndex])
    if (values.every(isNumeric)) {
      numericColumns.push(colIndex)
    } else {
      otherColumns.push(colIndex)
    }
  })

  if (numericColumns.length !== 1) return null
  if (otherColumns.length > 1) return null

  const valueIndex = numericColumns[0]
  const categoryIndex = otherColumns.length === 1 ? otherColumns[0] : null

  const data = rows.map((row, i) => ({
    category: categoryIndex === null ? `Row ${i + 1}` : String(row[categoryIndex]),
    value: row[valueIndex] as number,
  }))

  return {
    categoryIndex,
    categoryLabel: categoryIndex === null ? '' : columns[categoryIndex],
    valueIndex,
    valueLabel: columns[valueIndex],
    data,
  }
}
