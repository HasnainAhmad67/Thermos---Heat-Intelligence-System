import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { HeatReading } from "../types";

interface Props {
  assetId: string | null;
}

const DATA_STATE_LABELS: Record<string, string> = {
  RECENT_OBSERVED: "Recent",
  MODELED: "Modeled",
  SIMULATED: "Simulated",
  DEMO: "Demo",
};

export default function HeatPanel({ assetId }: Props) {
  const [current, setCurrent] = useState<HeatReading | null>(null);
  const [forecast, setForecast] = useState<HeatReading | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!assetId) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    Promise.all([api.getCurrentHeat(assetId), api.getForecastHeat(assetId, 6)])
      .then(([currentReading, forecastReading]) => {
        if (cancelled) return;
        setCurrent(currentReading);
        setForecast(forecastReading);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [assetId]);

  if (!assetId) {
    return (
      <div className="panel">
        <h2>Heat Intelligence</h2>
        <p className="muted">Select an asset to see heat data.</p>
      </div>
    );
  }

  return (
    <div className="panel">
      <h2>Heat Intelligence</h2>
      {loading && <p className="muted">Loading heat data…</p>}
      {error && <p className="error-text">{error}</p>}

      {current && (
        <div className="heat-row">
          <span className="heat-row__label">Current</span>
          <span className="heat-row__value">{current.temperature_c}°C</span>
          <span className="tag">{DATA_STATE_LABELS[current.data_state] ?? current.data_state}</span>
        </div>
      )}

      {forecast && (
        <div className="heat-row">
          <span className="heat-row__label">Forecast (6h)</span>
          <span className="heat-row__value">{forecast.temperature_c}°C</span>
          <span className="tag">{DATA_STATE_LABELS[forecast.data_state] ?? forecast.data_state}</span>
        </div>
      )}

      {current?.persistence_score != null ? (
        <div className="heat-row">
          <span className="heat-row__label">Persistence</span>
          <span className="heat-row__value">
            {Math.round(current.persistence_score * 100)}%
          </span>
        </div>
      ) : (
        <div className="heat-row">
          <span className="heat-row__label">Persistence</span>
          <span className="heat-row__value muted">No live signal — using modeled default</span>
        </div>
      )}
    </div>
  );
}