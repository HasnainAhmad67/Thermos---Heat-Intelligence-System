import type { PriorityItem } from "../types";

interface Props {
  priorities: PriorityItem[];
  selectedAssetId: string | null;
  onSelect: (assetId: string) => void;
}

export default function RiskPriorityPanel({ priorities, selectedAssetId, onSelect }: Props) {
  return (
    <div className="panel">
      <h2>Priority Ranking</h2>
      <p className="muted priority-panel__subnote">
        Ranked by risk + asset criticality — not risk alone.
      </p>
      {priorities.length === 0 && <p className="muted">No priority data yet.</p>}

      <ol className="priority-list">
        {priorities.map((item) => (
          <li
            key={item.asset_id}
            className={`priority-item ${item.asset_id === selectedAssetId ? "priority-item--selected" : ""}`}
            onClick={() => onSelect(item.asset_id)}
          >
            <div className="priority-item__rank">#{item.rank}</div>
            <div className="priority-item__body">
              <div className="priority-item__name">{item.asset_name}</div>
              <div className="priority-item__reason">{item.reason}</div>
              <div className="priority-item__meta">
                Risk: {item.risk_score} · Criticality: {Math.round(item.criticality * 100)}%
              </div>
            </div>
            <div className="priority-item__score">{item.priority_score}</div>
          </li>
        ))}
      </ol>
    </div>
  );
}