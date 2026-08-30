import { useState } from "react";
import { api } from "../api/client";
import type { InterventionType, ScenarioResult } from "../types";

interface Props {
  assetId: string | null;
}

const INTERVENTIONS: { value: InterventionType; label: string }[] = [
  { value: "shade_structure", label: "Shade Structure" },
  { value: "reflective_coating", label: "Reflective Coating" },
  { value: "ventilation_fans", label: "Ventilation Fans" },
  { value: "vegetation_buffer", label: "Vegetation Buffer" },
];

export default function ScenarioSimulator({ assetId }: Props) {
  const [intervention, setIntervention] =
    useState<InterventionType>("shade_structure");

  const [result, setResult] = useState<ScenarioResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runSimulation = async () => {
    if (!assetId) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await api.simulateScenario(assetId, intervention);
      setResult(res);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  if (!assetId) {
    return (
      <div className="panel">
        <h2>Scenario Simulator</h2>
        <p className="muted">Select an asset first.</p>
      </div>
    );
  }

  return (
    <div className="panel">
      <h2>Scenario Simulator (What-If)</h2>

      <div className="scenario-controls">
        <select
          value={intervention}
          onChange={(e) =>
            setIntervention(e.target.value as InterventionType)
          }
        >
          {INTERVENTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        <button onClick={runSimulation} disabled={loading}>
          {loading ? "Simulating…" : "Run Simulation"}
        </button>
      </div>

      {error && <p className="error-text">{error}</p>}

      {result && (
        <div className="scenario-result">
          <div className="scenario-flow">
            <div className="scenario-flow__step">
              <div className="scenario-flow__label">Current</div>
              <div className="scenario-flow__value">
                {result.baseline_risk}
              </div>
            </div>

            <div className="scenario-flow__arrow">→</div>

            <div className="scenario-flow__step">
              <div className="scenario-flow__label">Intervention</div>
              <div className="scenario-flow__value scenario-flow__value--intervention">
                {
                  INTERVENTIONS.find(
                    (i) => i.value === intervention
                  )?.label
                }
              </div>
            </div>

            <div className="scenario-flow__arrow">→</div>

            <div className="scenario-flow__step">
              <div className="scenario-flow__label">Projected</div>
              <div className="scenario-flow__value scenario-flow__value--projected">
                {result.projected_risk}
              </div>
            </div>
          </div>

          <div className="scenario-delta">
            <span className="positive">
              ↓ {result.risk_reduction_pct}% reduction
            </span>
          </div>

          <p className="scenario-result__notes">
            {result.notes}
          </p>

          <span className="tag">
            Simulated — not an observed FortyGuard measurement
          </span>
        </div>
      )}
    </div>
  );
}