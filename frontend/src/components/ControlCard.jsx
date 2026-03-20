import TimeWindowSelector from "./TimeWindowSelector";

export default function ControlCard({
  timeWindow,
  setTimeWindow,
  locationId,
  setLocationId,
  locations,
}) {
  return (
    <div className="filter-bar">

      {/* LEFT */}
      <div className="filter-left">

        <label className="filter-label">
          Time Window
        </label>

        <TimeWindowSelector
          value={timeWindow || ""}
          onChange={setTimeWindow}
        />

      </div>


      {/* RIGHT */}
      <div className="filter-right">

        <label className="filter-label">
          Location
        </label>

        <select
          className="location-select"
          value={locationId || ""}
          onChange={(e) => setLocationId(e.target.value)}
        >

          <option value="" disabled>
            Select
          </option>

          {locations?.map((l) => (
            <option key={l.id} value={l.id}>
              {l.name}
            </option>
          ))}

        </select>

      </div>

    </div>
  );
}