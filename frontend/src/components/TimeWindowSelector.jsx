export default function TimeWindowSelector({ value, onChange }) {
  return (
    <select
      className="border rounded px-2 py-1 text-sm"
      value={value || ""}
      onChange={(e) => onChange(e.target.value)}
    >

      <option value="" disabled>
        Select
      </option>

      <option value="30m">Last 30 mins</option>
      <option value="1h">Last 1 hour</option>
      <option value="3h">Last 3 hours</option>

    </select>
  );
}