// src/services/predictService.js

const API_URL = "http://127.0.0.1:8000";

function sanitizePayload(payload) {
  return {
    ...payload,
    temperature: Math.max(-20, Math.min(40, payload.temperature)),
    humidity: Math.max(0, Math.min(100, payload.humidity))
  };
}

/*
------------------------------------
WINDOW → BINS MAPPING
------------------------------------
*/
const WINDOW_TO_BINS = {
  "30m": 6,
  "1h": 6,
  "3h": 6
};

/*
------------------------------------
GENERATE TIME SERIES
------------------------------------
*/
function generateTimeSeries(timeWindow, predictions) {
  const now = new Date();

  let stepMinutes = 10;

  if (timeWindow === "30m") stepMinutes = 5;
  if (timeWindow === "1h") stepMinutes = 10;
  if (timeWindow === "3h") stepMinutes = 30;

  let totalPoints = 6;

  if (timeWindow === "30m") totalPoints = 6;
  if (timeWindow === "1h") totalPoints = 6;
  if (timeWindow === "3h") totalPoints = 6;

  const history = [];

  for (let i = totalPoints; i >= 0; i--) {
    const t = new Date(now);
    t.setMinutes(now.getMinutes() - i * stepMinutes);

    const base =
      predictions[totalPoints - 1 - i]?.crowdedness_score ??
      predictions[0]?.crowdedness_score ??
      0;

    // small smooth variation (curve effect)
    const variation = Math.sin(i / 2) * 0.03;

    history.push({
      time: t.toISOString(),
      value: Math.max(0, Math.min(1, base + variation))
    });
  }

  return history;
}

/*
------------------------------------
GET LOCATIONS
------------------------------------
*/
async function getLocations() {
  const locations = [
    { id: "0", name: "Sembawang Eating House", freq: 4500 },
    { id: "1", name: "Kenn's Foodhouse", freq: 3800 },
    { id: "2", name: "S11 Upper Cross Street Food House", freq: 12500 },
    { id: "3", name: "Yummy Curry Eating House", freq: 5200 },
    { id: "4", name: "The Food Court", freq: 9800 },
    { id: "5", name: "HLY Eating House", freq: 4700 },
    { id: "6", name: "Kheng Jan Eating House", freq: 4300 },
    { id: "7", name: "243 Foodcourt", freq: 6100 },
    { id: "8", name: "Hong Xiang Eating House", freq: 4200 },
    { id: "9", name: "GCL Eating House Pte Ltd", freq: 5000 },
    { id: "10", name: "Yi Jia Food House", freq: 5400 },
    { id: "11", name: "Henly Huat Drinks Food Court", freq: 6300 },
    { id: "12", name: "Tastebud Foodcourt", freq: 7600 },
    { id: "13", name: "TLB 65 Eating House", freq: 10213 },
    { id: "14", name: "Bgain 442 Eating House", freq: 6900 },
    { id: "15", name: "Food Loft", freq: 8500 },
    { id: "16", name: "Chit Chat & Makan Eating House", freq: 7200 },
    { id: "17", name: "PGPR Air-Con Food Court", freq: 14000 },
    { id: "18", name: "New Garden Coffee Shop", freq: 6600 },
    { id: "19", name: "6033 Foodcourt LLP", freq: 5900 }
  ];

  return {
    locations,
    defaultLocationId: ""
  };
}

/*
------------------------------------
GET PREDICTION
------------------------------------
*/
async function getPrediction(timeWindow, locationId, features = {}) {
  const { locations } = await getLocations();

  const selectedLocation = locations.find(
    (l) => String(l.id) === String(locationId)
  );

  const locationFreq = selectedLocation?.freq ?? 5000;

  const binsAhead = WINDOW_TO_BINS[timeWindow] || 6;

  const payload = {
    location_id: String(locationId),
    location_freq: locationFreq,
    temperature: 29.5,
    humidity: 78,
    weather: "cloudy",
    is_public_holiday: 0,
    bins_ahead: binsAhead,
    ...features
  };

  const finalPayload = sanitizePayload(payload);
  console.log("Prediction Payload:", payload);

  const res = await fetch(`${API_URL}/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(finalPayload)
  });

  if (!res.ok) {
    const errorText = await res.text();
    console.error(errorText);
    throw new Error("Prediction API failed");
  }

  const data = await res.json();
  const predictions = data.predictions || [];

  return {
    predictions,

    level: predictions?.[0]?.crowd_label || "Unknown",

    score: predictions?.[0]?.crowdedness_score || 0,

    history: generateTimeSeries(timeWindow, predictions),

    meta: {
      modelVersion: "GradientBoosting_v1",
      source: "FastAPI ML model",
      binsAhead,
      lastUpdated: new Date().toISOString()
    }
  };
}

export default { getLocations, getPrediction };
