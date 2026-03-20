import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceDot,
} from "recharts";

export default function TrendChart({
  data = [],
  lines = [],
  nowIndex = null,
  peakIndex = null,
}) {
  if (!Array.isArray(data) || data.length === 0) {
    return (
      <div className="chart-empty-state">
        No trend data available
      </div>
    );
  }

  const nowPoint =
    nowIndex !== null && data[nowIndex] ? data[nowIndex] : null;

  const peakPoint =
    peakIndex !== null && data[peakIndex] ? data[peakIndex] : null;

  return (
    <div className="chart-wrapper">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid stroke="#333" strokeDasharray="3 3" />

          <XAxis
            dataKey="time"
            stroke="#aaa"
            tick={{ fill: "#aaa", fontSize: 12 }}
          />

          <YAxis
            domain={[0, 100]}
            stroke="#aaa"
            tick={{ fill: "#aaa", fontSize: 12 }}
          />

          <Tooltip
            contentStyle={{
              backgroundColor: "#111",
              border: "1px solid #333",
              color: "#fff",
            }}
          />

          {lines.map((line) => (
            <Line
              key={line.dataKey}
              type="monotone"
              dataKey={line.dataKey}
              stroke={line.stroke}
              strokeWidth={3}
              dot={false}
              isAnimationActive={false}
              connectNulls
            />
          ))}

          {nowPoint && lines[0]?.dataKey && nowPoint[lines[0].dataKey] !== null && (
            <ReferenceDot
              x={nowPoint.time}
              y={nowPoint[lines[0].dataKey]}
              r={5}
              fill="#ffffff"
              stroke="#22d3ee"
              ifOverflow="visible"
            />
          )}

          {peakPoint && lines[0]?.dataKey && peakPoint[lines[0].dataKey] !== null && (
            <ReferenceDot
              x={peakPoint.time}
              y={peakPoint[lines[0].dataKey]}
              r={6}
              fill="#facc15"
              stroke="#facc15"
              ifOverflow="visible"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}