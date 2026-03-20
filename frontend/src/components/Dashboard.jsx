import { useEffect, useState, useMemo } from "react";
import ControlCard from "./ControlCard";
import TrendChart from "./TrendChart";
import ContextBadges from "./ContextBadges";
import predictService from "../services/predictService.js";
import airesLogo from "../images/Airies+Applied+Quantum+Technology+Navbar+NoBG.png.webp";

function formatWindowLabel(timeWindow) {
  if (timeWindow === "30m") return "Last 30m";
  if (timeWindow === "1h") return "Last 1h";
  if (timeWindow === "3h") return "Last 3h";
  return "Select";
}

function formatPointTime(time) {
  try {
    return new Date(time).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return time;
  }
}

export default function Dashboard() {
  const [timeWindow, setTimeWindow] = useState("");
  const [locationId, setLocationId] = useState("");
  const [locations, setLocations] = useState([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  const [prediction, setPrediction] = useState(null);
  const [scenarioPrediction, setScenarioPrediction] = useState(null);

  const [manualInput, setManualInput] = useState("");

  useEffect(() => {
    (async () => {
      const res = await predictService.getLocations();
      setLocations(res.locations || []);
      setLocationId("");
    })();
  }, []);

  useEffect(() => {
    if (!locationId || !timeWindow) return;

    setLoading(true);
    setError(false);

    predictService
      .getPrediction(timeWindow, locationId)
      .then((res) => {
        setPrediction(res);
        setScenarioPrediction(null);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError(true);
        setLoading(false);
      });
  }, [timeWindow, locationId]);

  const outlookData = useMemo(() => {
    if (!prediction?.history) return [];

    let data = prediction.history.map((item, idx) => ({
      time: formatPointTime(item.time),
      crowdedness: Number(((item.value ?? 0) * 100).toFixed(2)),
      pointType: idx === 0 ? "now" : "future",
    }));

    if (data.length === 1) {
      const first = data[0];

      data = [
        {
          ...first,
          time: first.time,
        },
        {
          ...first,
          time: first.time + " ",
        },
      ];
    }

    return data;
  }, [prediction]);

  const scenarioCompareData = useMemo(() => {
  if (!prediction?.history || !scenarioPrediction?.history) return [];

  const maxLen = Math.max(
    prediction.history.length || 0,
    scenarioPrediction.history.length || 0
  );

  let data = Array.from({ length: maxLen }).map((_, idx) => {
    const baseItem = prediction.history[idx];
    const scenarioItem = scenarioPrediction.history[idx];

    return {
      time: formatPointTime(baseItem?.time || scenarioItem?.time || `t-${idx}`),
      baseline: baseItem
        ? Number(((baseItem.value ?? 0) * 100).toFixed(2))
        : null,
      scenario: scenarioItem
        ? Number(((scenarioItem.value ?? 0) * 100).toFixed(2))
        : null,
    };
  });

  if (data.length === 1) {
    const first = data[0];

    data = [
      { ...first },
      { ...first, time: first.time + " " },
    ];
  }

  return data;
}, [prediction, scenarioPrediction]);

  const scenarioOnlyData = useMemo(() => {
  if (!scenarioPrediction?.history) return [];

  let data = scenarioPrediction.history.map((item) => ({
    time: formatPointTime(item.time),
    crowdedness: Number(((item.value ?? 0) * 100).toFixed(2)),
  }));

  // 🔥 FIX: kalau cuma 1 titik
  if (data.length === 1) {
    const first = data[0];

    data = [
      { ...first },
      { ...first, time: first.time + " " },
    ];
  }

  return data;
}, [scenarioPrediction]);

  const insightData = useMemo(() => {
    if (!outlookData.length) {
      return {
        peakTime: "-",
        peakValue: 0,
        averageValue: 0,
        trendText: "-",
      };
    }

    const peakPoint = outlookData.reduce((max, curr) =>
      curr.crowdedness > max.crowdedness ? curr : max
    );

    const averageValue =
      outlookData.reduce((sum, item) => sum + item.crowdedness, 0) /
      outlookData.length;

    const first = outlookData[0]?.crowdedness ?? 0;
    const last = outlookData[outlookData.length - 1]?.crowdedness ?? 0;
    const diff = last - first;

    let trendText = "Stable";
    if (diff > 1) trendText = "Increasing 📈";
    else if (diff < -1) trendText = "Decreasing 📉";

    return {
      peakTime: peakPoint.time,
      peakValue: peakPoint.crowdedness,
      averageValue,
      trendText,
    };
  }, [outlookData]);

  const scenarioImpact = useMemo(() => {
    if (!prediction || !scenarioPrediction) return null;

    const baselineScore = (prediction.score ?? 0) * 100;
    const scenarioScore = (scenarioPrediction.score ?? 0) * 100;
    const delta = scenarioScore - baselineScore;

    return {
      delta: delta.toFixed(1),
      baselineScore: baselineScore.toFixed(1),
      scenarioScore: scenarioScore.toFixed(1),
    };
  }, [prediction, scenarioPrediction]);

  function parseManualInput() {
    if (!manualInput.trim()) {
      alert("Please enter at least one variable.");
      return null;
    }

    const payload = {};

    const pairs = manualInput
      .split(/[\n,]+/)
      .map((p) => p.trim())
      .filter(Boolean);

    pairs.forEach((pair) => {
      const [key, value] = pair.split("=");

      if (!key || value === undefined) return;

      const cleanedKey = key.trim();
      const cleanedValue = value.trim();

      payload[cleanedKey] = isNaN(cleanedValue)
        ? cleanedValue
        : Number(cleanedValue);
    });

    return payload;
  }

  function validateFeatureInput(payload) {
  if ("day_of_week" in payload && (payload.day_of_week < 0 || payload.day_of_week > 6)) {
    return "day_of_week must be between 0-6";
  }

  if ("hour_of_day" in payload && (payload.hour_of_day < 0 || payload.hour_of_day > 23)) {
    return "hour_of_day must be between 0-23";
  }

  if ("is_weekend" in payload && ![0, 1].includes(payload.is_weekend)) {
    return "is_weekend must be 0 or 1";
  }

  if ("is_public_holiday" in payload && ![0, 1].includes(payload.is_public_holiday)) {
    return "is_public_holiday must be 0 or 1";
  }

  if ("temperature" in payload && (payload.temperature < -20 || payload.temperature > 40)) {
    return "temperature must be between -20 to 40";
  }

  if ("humidity" in payload && (payload.humidity < 0 || payload.humidity > 100)) {
    return "humidity must be between 0 to 100";
  }

  if (
    "weather" in payload &&
    !["clear", "cloudy", "night_clear", "rainy"].includes(payload.weather)
  ) {
    return "weather must be clear, cloudy, night_clear, or rainy";
  }

  return null;
}

  async function handleManualPrediction() {
  const payload = parseManualInput();

  if (!payload || !locationId || !timeWindow) return;

  const errorMsg = validateFeatureInput(payload);

  if (errorMsg) {
    alert(errorMsg);
    return;
  }

  try {
    const res = await predictService.getPrediction(
      timeWindow,
      locationId,
      payload
    );

    setScenarioPrediction(res);
  } catch (err) {
    console.error(err);
    alert("Prediction failed.");
  }
}

  function resetScenario() {
    setScenarioPrediction(null);
    setManualInput("");
  }

  return (
    <div className="dashboard-root">
      <div className="dashboard-header">
        <img
          src={airesLogo}
          className="dashboard-logo"
          alt="Aires Logo"
          onClick={() => window.location.reload()}
        />

        <h1 className="dashboard-title">Crowdedness Dashboard</h1>
      </div>

      <div className="dashboard-divider" />

      <div className="filter-section">
        <ControlCard
          timeWindow={timeWindow}
          setTimeWindow={setTimeWindow}
          locationId={locationId}
          setLocationId={setLocationId}
          locations={locations}
        />
      </div>

      {!loading && prediction && (
        <div className="dashboard-info">
          <div className="dashboard-cards">
            <div className={`dashboard-level ${prediction.level?.toLowerCase?.()}`}>
              <div className="dashboard-level-title">CROWDEDNESS LEVEL</div>
              <div className="dashboard-level-value">{prediction.level}</div>
            </div>

            <div className="dashboard-score">
              <div className="dashboard-score-title">CROWDEDNESS SCORE</div>
              <div className="dashboard-score-value">
                <strong>{(prediction.score * 100).toFixed(0)}%</strong>
              </div>
            </div>

            <div className="dashboard-window">
              <div className="dashboard-window-title">SELECTED WINDOW</div>
              <div className="dashboard-window-value">
                {formatWindowLabel(timeWindow)}
              </div>
            </div>
          </div>

          <p className="dashboard-subtitle">
            Real-time multi-location crowd monitoring
          </p>
        </div>
      )}

      {!loading && !error && prediction && (
        <>
          <div className="single-chart-section">
            <div className="trend-card full-width-card">
              <h2>Crowd Outlook (Now → Future)</h2>

              <TrendChart
                data={outlookData}
                lines={[
                  {
                    dataKey: "crowdedness",
                    stroke: "#22d3ee",
                    name: "Crowdedness",
                  },
                ]}
                nowIndex={0}
                peakIndex={
                  outlookData.length
                    ? outlookData.findIndex(
                        (item) => item.crowdedness === insightData.peakValue
                      )
                    : null
                }
              />
            </div>
          </div>

          <div className="insight-grid">
            <div className="insight-card">
              <div className="insight-label">Peak Crowd</div>
              <div className="insight-value">
                {insightData.peakTime} · {Math.round(insightData.peakValue)}%
              </div>
            </div>

            <div className="insight-card">
              <div className="insight-label">Average Outlook</div>
              <div className="insight-value">
                {Math.round(insightData.averageValue)}%
              </div>
            </div>

            <div className="insight-card">
              <div className="insight-label">Trend Direction</div>
              <div className="insight-value">{insightData.trendText}</div>
            </div>
          </div>
        </>
      )}

      {scenarioPrediction && (
        <>
          <div className="scenario-section">
            <div className="trend-card full-width-card">
              <h2>Scenario vs Baseline</h2>

              <TrendChart
                data={scenarioCompareData}
                lines={[
                  {
                    dataKey: "baseline",
                    stroke: "#22d3ee",
                    name: "Baseline",
                  },
                  {
                    dataKey: "scenario",
                    stroke: "#ef4444",
                    name: "Scenario",
                  },
                ]}
              />
            </div>
          </div>

          <div className="impact-grid">
            <div className="impact-card">
              <div className="impact-title">Scenario Impact</div>
              <div
                className={`impact-value ${
                  Number(scenarioImpact?.delta) >= 0 ? "positive" : "negative"
                }`}
              >
                {Number(scenarioImpact?.delta) >= 0 ? "+" : ""}
                {scenarioImpact?.delta}%
              </div>
              <div className="impact-subtext">
                Baseline {scenarioImpact?.baselineScore}% → Scenario{" "}
                {scenarioImpact?.scenarioScore}%
              </div>
            </div>

            <div className="trend-card compact-scenario-card">
              <h2>Scenario Only</h2>

              <TrendChart
                data={scenarioOnlyData}
                lines={[
                  {
                    dataKey: "crowdedness",
                    stroke: "#ef4444",
                    name: "Scenario",
                  },
                ]}
              />

              <button onClick={resetScenario} className="reset-button">
                Reset Scenario
              </button>
            </div>
          </div>
        </>
      )}

      <div className="feature-input-section">
        <h3>User Additional Feature Needs</h3>

        <textarea
          rows="6"
          value={manualInput}
          onChange={(e) => setManualInput(e.target.value)}
          placeholder={`Example:
          day_of_week=2
          hour_of_day=14
          is_weekend=0  
          is_public_holiday=0
          temperature=24.8
          humidity=93.5
          weather=rainy`}
        />

        <button onClick={handleManualPrediction} className="submit-button">
          Submit Features
        </button>
      </div>

      {!loading && prediction && (
        <ContextBadges
          timeWindow={timeWindow}
          meta={prediction.meta}
          context={prediction.context}
        />
      )}
    </div>
  );
}