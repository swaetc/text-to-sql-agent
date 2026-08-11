import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { ChartShape } from '../lib/chartShape'

interface Props {
  shape: ChartShape
}

const BAR_COLOR = '#2a78d6'
const GRID_COLOR = '#e1e0d9'
const AXIS_COLOR = '#898781'

function formatValue(value: number): string {
  return Number.isInteger(value) ? value.toLocaleString() : value.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

interface TooltipPayloadItem {
  value: number
  payload: { category: string; value: number }
}

function ChartTooltip({
  active,
  payload,
  valueLabel,
}: {
  active?: boolean
  payload?: TooltipPayloadItem[]
  valueLabel: string
}) {
  if (!active || !payload || payload.length === 0) return null
  const item = payload[0]
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm shadow-md">
      <p className="text-slate-500">{item.payload.category}</p>
      <p className="font-semibold text-slate-900">
        {formatValue(item.value)} <span className="font-normal text-slate-400">{valueLabel}</span>
      </p>
    </div>
  )
}

export function ResultChart({ shape }: Props) {
  const { data, categoryLabel, valueLabel } = shape

  const longestLabel = data.reduce((max, d) => Math.max(max, d.category.length), 0)
  const yAxisWidth = Math.min(160, Math.max(72, longestLabel * 6.5))

  const chartHeight = Math.max(180, data.length * 40 + 40)

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 sm:p-5">
      <p className="mb-3 text-sm font-medium text-slate-600">
        {valueLabel}
        {categoryLabel ? ` by ${categoryLabel}` : ''}
      </p>
      <ResponsiveContainer width="100%" height={chartHeight}>
        <BarChart data={data} layout="vertical" margin={{ top: 4, right: 24, bottom: 4, left: 0 }}>
          <CartesianGrid horizontal={false} stroke={GRID_COLOR} strokeDasharray="0" />
          <XAxis
            type="number"
            tick={{ fill: AXIS_COLOR, fontSize: 12 }}
            axisLine={{ stroke: GRID_COLOR }}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="category"
            width={yAxisWidth}
            tick={{ fill: '#52514e', fontSize: 12 }}
            axisLine={{ stroke: GRID_COLOR }}
            tickLine={false}
          />
          <Tooltip
            cursor={{ fill: 'rgba(42, 120, 214, 0.06)' }}
            content={<ChartTooltip valueLabel={valueLabel} />}
          />
          <Bar dataKey="value" fill={BAR_COLOR} radius={[0, 4, 4, 0]} barSize={22} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
