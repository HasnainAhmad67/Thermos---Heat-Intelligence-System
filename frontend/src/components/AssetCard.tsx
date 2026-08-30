import { useState } from "react";
import type { Asset, RiskScore } from "../types";

interface Props {
  asset: Asset;
  risk?: RiskScore;
  isSelected: boolean;
  onSelect: (assetId: string) => void;
}

const LEVEL_COLORS: Record<string, string> = {
  LOW: "#2e7d32",
  MEDIUM: "#f9a825",
  HIGH: "#ef6c00",
  CRITICAL: "#c62828",
};

const DRIVER_LABELS: Record<string, string> = {
  hazard: "Hazard (temperature)",
  exposure: "Exposure (sun/coverage)",
  vulnerability: "Vulnerability (criticality)",
  persistence: "Persistence (how sustained)",
  response_gap: "Response Gap",
};

export default function AssetCard({ asset, risk, isSelected, onSelect }: Props) {
  const [showWhy, setShowWhy] = useState(false);

  return (
    <div
      className={`asset-card ${isSelected ? "asset-card--selected" : ""}`}
      onClick={() => onSelect(asset.id)}
    >
      <div className="asset-card__header">
        <h3>{asset.name}</h3>
        {risk && (
          <span className="risk-badge" style={{ backgroundColor: LEVEL_COLORS[risk.level] }}>
            {risk.level}
          </span>
        )}
      </div>
      <p className="asset-card__desc">{asset.description}</p>

      {risk ? (
        <div className="asset-card__score-row">
          <div className="asset-card__score">
            Risk score: <strong>{risk.score}</strong> / 100
          </div>
          <button
            className="asset-card__why-btn"
            onClick={(e) => {
              e.stopPropagation();
              setShowWhy(!showWhy);
            }}
          >
            {showWhy ? "Hide" : "Why?"}
          </button>
        </div>
      ) : (
        <div className="asset-card__score">Loading risk…</div>
      )}

      {showWhy && risk && (
        <div className="asset-card__why" onClick={(e) => e.stopPropagation()}>
          {Object.entries(risk.drivers)
            .sort((a, b) => b[1] - a[1])
            .map(([key, value]) => (
              <div key={key} className="asset-card__driver-row">
                <span className="asset-card__driver-label">{DRIVER_LABELS[key] ?? key}</span>
                <div className="asset-card__driver-bar-track">
                  <div
                    className="asset-card__driver-bar-fill"
                    style={{ width: `${value}%` }}
                  />
                </div>
                <span className="asset-card__driver-value">{value}</span>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}