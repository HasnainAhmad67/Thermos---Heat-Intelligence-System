import { useEffect, useState } from "react";
import { MapContainer, TileLayer, GeoJSON, CircleMarker, Tooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { api } from "../api/client";
import type { Asset, RiskScore, FacilityHeatmap } from "../types";

interface Props {
  centerLat: number;
  centerLng: number;
  assets: Asset[];
  riskByAssetId: Record<string, RiskScore>;
  selectedAssetId: string | null;
  onSelectAsset: (id: string) => void;
  facilityId: string; // used to trigger refetch when facility changes
}

const RISK_COLORS: Record<string, string> = {
  LOW: "#2e7d32",
  MEDIUM: "#f9a825",
  HIGH: "#ef6c00",
  CRITICAL: "#c62828",
};

function tempToColor(temp: number, min: number, max: number): string {
  if (max === min) return "#f9a825";
  const t = Math.max(0, Math.min(1, (temp - min) / (max - min)));
  // blue (cool) -> yellow -> red (hot)
  if (t < 0.5) {
    const p = t / 0.5;
    return `rgb(${Math.round(255 * p)}, ${Math.round(200 * p + 55)}, ${Math.round(255 * (1 - p))})`;
  }
  const p = (t - 0.5) / 0.5;
  return `rgb(255, ${Math.round(255 * (1 - p))}, 0)`;
}

export default function FacilityMap({
  centerLat,
  centerLng,
  assets,
  riskByAssetId,
  selectedAssetId,
  onSelectAsset,
  facilityId,
}: Props) {
  const [heatmap, setHeatmap] = useState<FacilityHeatmap | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api
      .getFacilityHeatmap()
      .then(setHeatmap)
      .catch((err) => setError((err as Error).message))
      .finally(() => setLoading(false));
  }, [facilityId]);

  const tempRange = heatmap?.temperature_range;

  return (
    <div className="panel facility-map-panel">
      <div className="facility-map-panel__header">
        <h2>Thermal Map</h2>
        {loading && <span className="tag">Loading heatmap…</span>}
      </div>

      {error && <p className="error-text">{error}</p>}

      <div className="facility-map-panel__map">
        <MapContainer center={[centerLat, centerLng]} zoom={15} style={{ height: "320px", width: "100%" }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="&copy; OpenStreetMap contributors"
          />

          {heatmap && tempRange?.min != null && tempRange?.max != null && (
            <GeoJSON
              key={facilityId}
              data={heatmap as any}
              style={(feature: any) => ({
                fillColor: tempToColor(
                  feature.properties.average_temperature,
                  tempRange.min as number,
                  tempRange.max as number
                ),
                fillOpacity: 0.45,
                color: "transparent",
                weight: 0,
              })}
            />
          )}

          {assets.map((asset) => {
            const risk = riskByAssetId[asset.id];
            const isSelected = asset.id === selectedAssetId;
            return (
              <CircleMarker
                key={asset.id}
                center={[asset.lat, asset.lng]}
                radius={isSelected ? 12 : 8}
                pathOptions={{
                  fillColor: risk ? RISK_COLORS[risk.level] : "#9aa0ab",
                  fillOpacity: 1,
                  color: isSelected ? "#ffffff" : "#1a1d24",
                  weight: isSelected ? 3 : 2,
                }}
                eventHandlers={{ click: () => onSelectAsset(asset.id) }}
              >
                <Tooltip direction="top" offset={[0, -8]}>
                  <strong>{asset.name}</strong>
                  {risk && ` — ${risk.level} (${risk.score}/100)`}
                </Tooltip>
              </CircleMarker>
            );
          })}
        </MapContainer>
      </div>

      {tempRange?.min != null && (
        <div className="facility-map-panel__legend">
          <span>{tempRange.min}°C</span>
          <div className="facility-map-panel__legend-bar" />
          <span>{tempRange.max}°C</span>
        </div>
      )}
    </div>
  );
}