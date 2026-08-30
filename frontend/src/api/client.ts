
import type {
  Asset,
  HeatReading,
  RiskAndPriorityResponse,
  RiskScore,
  ScenarioResult,
  InterventionType,
  AgentResponse,
  ApiEnvelope,
  Facility,
  FacilitySelectResult,
} from "../types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new Error("Can't reach the THERMOS backend. Is it running on port 8000?");
  }

  let json: ApiEnvelope<T>;
  try {
    json = await res.json();
  } catch {
    throw new Error(`Unexpected response from server (status ${res.status}).`);
  }

  if (!res.ok || !json.success) {
    const code = json.error?.code;
    if (code === "FORTYGUARD_UNAVAILABLE") {
      throw new Error("Heat intelligence data is temporarily unavailable. Please try again shortly.");
    }
    if (code === "ASSET_NOT_FOUND") {
      throw new Error("This zone could not be found.");
    }
    const message = json.error?.message || `Something went wrong (status ${res.status}).`;
    throw new Error(message);
  }

  return json.data as T;
}

export const api = {
  getAssets: () => request<Asset[]>("/assets"),

  getAsset: (assetId: string) => request<Asset>(`/assets/${assetId}`),

  getCurrentHeat: (assetId: string) =>
    request<HeatReading>(`/heat/current/${assetId}`),

  getForecastHeat: (assetId: string, hoursAhead = 6) =>
    request<HeatReading>(`/heat/forecast/${assetId}?hours_ahead=${hoursAhead}`),

  getRisk: (assetId: string) => request<RiskScore>(`/risk/${assetId}`),

  getAllRiskAndPriority: () => request<RiskAndPriorityResponse>("/risk"),

  simulateScenario: (assetId: string, intervention: InterventionType) =>
    request<ScenarioResult>("/scenarios/simulate", {
      method: "POST",
      body: JSON.stringify({ asset_id: assetId, intervention }),
    }),

  askAgent: (question: string, assetId?: string) =>
    request<AgentResponse>("/agent/ask", {
      method: "POST",
      body: JSON.stringify({ question, asset_id: assetId }),
    }),

  getFacility: () => request<Facility>("/facility"),
  selectFacility: (
  lat: number,
  lng: number,
  name: string,
  city: string,
  state: string,
  country: string
) =>
  request<FacilitySelectResult>("/facility/select", {
    method: "POST",
    body: JSON.stringify({ lat, lng, name, city, state, country }),
  }),

resetFacility: () =>
  request<FacilitySelectResult>("/facility/reset", { method: "POST" }),
getFacilityHeatmap: () => request<FacilityHeatmap>("/heat/facility-map"),
};

