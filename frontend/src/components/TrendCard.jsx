import TrendChart from "./TrendChart";

export default function TrendCard({ data, timeWindow }) {
  return (
    <div className="bg-neutral-800 rounded-xl px-6 py-6">
      <h3 className="text-center font-semibold text-gray-200 mb-4">
        Crowd Trend (last {timeWindow})
      </h3>

      <TrendChart data={data} />
    </div>
  );
}
