export type DataState = "RECENT_OBSERVED" | "MODELED" | "SIMULATED" | "DEMO";
export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface Asset {
  id: string;
  name: string;
  type: string;
  lat: number;
  lng: number;
  criticality: number;
  description?: string;
}
export interface FacilitySelectResult {
  facility: Facility;
  assets: Asset[];
}

export interface HeatReading {
  asset_id: string;
  temperature_c: number;
  exceedance_minutes?: number;
  persistence_score?: number;
  source: "fortyguard" | "demo";
  timestamp: string;
  data_state: DataState;
}

export interface RiskDrivers {
  hazard: number;
  exposure: number;
  vulnerability: number;
  persistence: number;
  response_gap: number;
}

export interface RiskScore {
  asset_id: string;
  score: number;
  level: RiskLevel;
  drivers: RiskDrivers;
  model_version: string;
  data_state: DataState;
}

export interface PriorityItem {
  asset_id: string;
  asset_name: string;
  risk_score: number;
  criticality: number;
  priority_score: number;
  rank: number;
  reason: string;
  recommended_action: string;

}

export type InterventionType =
  | "shade_structure"
  | "reflective_coating"
  | "ventilation_fans"
  | "vegetation_buffer";

export interface ScenarioResult {
  asset_id: string;
  intervention: string;
  baseline_risk: number;
  projected_risk: number;
  risk_reduction_pct: number;
  notes: string;
  data_state: "SIMULATED";
}

export interface AgentResponse {
  answer: string;
  grounded_on: string[];
}

export interface RiskAndPriorityResponse {
  risks: RiskScore[];
  priorities: PriorityItem[];
  overall: OverallRisk;
}

export interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
  metadata: Record<string, unknown>;
  error: { code: string; message: string } | null;
}
export interface FacilityLocation {
  city: string;
  state: string;
  country: string;
  lat: number;
  lng: number;
}

export interface Facility {
  id: string;
  name: string;
  location: FacilityLocation;
}

export interface OverallRisk {
  score: number;
  level: RiskLevel;
}
export interface HeatmapFeature {
  id: string;
  type: "Feature";
  properties: {
    tile_id: number;
    average_temperature: number;
    min_temperature: number;
    max_temperature: number;
  };
  geometry: {
    type: "Polygon";
    coordinates: number[][][];
  };
}

export interface FacilityHeatmap {
  type: "FeatureCollection";
  features: HeatmapFeature[];
  temperature_range: { min: number | null; max: number | null };
  reference_time: string;
}