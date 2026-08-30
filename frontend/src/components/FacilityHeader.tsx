import type { Facility, OverallRisk } from "../types";

interface Props {
  facility: Facility | null;
  overall: OverallRisk | null;
  onChangeLocation: () => void;
  onResetToDallas: () => void;
  isCustomFacility: boolean;
}

const LEVEL_COLORS: Record<string, string> = {
  LOW: "#2e7d32",
  MEDIUM: "#f9a825",
  HIGH: "#ef6c00",
  CRITICAL: "#c62828",
};

export default function FacilityHeader({
  facility,
  overall,
  onChangeLocation,
  onResetToDallas,
  isCustomFacility,
}: Props) {
  if (!facility) return null;

  return (
    <div className="facility-header">
      <div className="facility-header__info">
        <div className="facility-header__eyebrow">Facility</div>
        <h2 className="facility-header__name">{facility.name}</h2>
        <div className="facility-header__location">
          📍 {facility.location.city}
          {facility.location.state ? `, ${facility.location.state}` : ""}, {facility.location.country}
        </div>
        <div className="facility-header__actions">
          <button className="facility-header__link-btn" onClick={onChangeLocation}>
            Change Location
          </button>
          {isCustomFacility && (
            <button className="facility-header__link-btn" onClick={onResetToDallas}>
              Reset to Dallas (Default)
            </button>
          )}
        </div>
      </div>
      {overall && (
        <div className="facility-header__overall">
          <div className="facility-header__eyebrow">Overall Facility Risk</div>
          <div className="facility-header__score-row">
            <span className="risk-badge risk-badge--lg" style={{ backgroundColor: LEVEL_COLORS[overall.level] }}>
              {overall.level}
            </span>
            <span className="facility-header__score">
              {overall.score}
              <span className="muted">/100</span>
            </span>
          </div>
        </div>
      )}
    </div>
  );
}