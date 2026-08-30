import { useEffect, useState } from "react";
import { api } from "../api/client";

import type {
  Asset,
  RiskScore,
  PriorityItem,
  Facility,
  OverallRisk,
} from "../types";

import AssetCard from "./AssetCard";
import HeatPanel from "./HeatPanel";
import RiskPriorityPanel from "./RiskPriorityPanel";
import ScenarioSimulator from "./ScenarioSimulator";
import AgentChat from "./AgentChat";
import FacilityHeader from "./FacilityHeader";
import LocationMap from "./LocationMap";
import FacilityMap from "./FacilityMap";

export default function Dashboard() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [risks, setRisks] = useState<RiskScore[]>([]);
  const [priorities, setPriorities] = useState<PriorityItem[]>([]);

  // Keep null on initial dashboard load.
  // Heat/forecast data will load only after the user selects an asset.
  const [selectedAssetId, setSelectedAssetId] = useState<string | null>(
    null
  );

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [facility, setFacility] = useState<Facility | null>(null);
  const [overall, setOverall] = useState<OverallRisk | null>(null);

  const [mapOpen, setMapOpen] = useState(false);
  const [switching, setSwitching] = useState(false);
  const [switchError, setSwitchError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [assetList, riskAndPriority, facilityData] = await Promise.all([
        api.getAssets(),
        api.getAllRiskAndPriority(),
        api.getFacility(),
      ]);

      setAssets(assetList);
      setRisks(riskAndPriority.risks);
      setPriorities(riskAndPriority.priorities);
      setOverall(riskAndPriority.overall);
      setFacility(facilityData);

      // IMPORTANT:
      // Do not automatically select an asset here.
      // This prevents HeatPanel from immediately fetching
      // current heat + forecast when the dashboard loads.
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSelectLocation = async (
    lat: number,
    lng: number,
    name: string,
    city: string,
    state: string,
    country: string
  ) => {
    setSwitching(true);
    setSwitchError(null);

    try {
      // Clear selected asset when switching facility.
      // User will select an asset from the new facility.
      setSelectedAssetId(null);

      await api.selectFacility(
        lat,
        lng,
        name,
        city,
        state,
        country
      );

      await loadData();

      setMapOpen(false);
    } catch (err) {
      setSwitchError((err as Error).message);
    } finally {
      setSwitching(false);
    }
  };

  const handleResetToDallas = async () => {
    setSwitching(true);
    setSwitchError(null);

    try {
      // Clear selected asset before loading the reset facility.
      setSelectedAssetId(null);

      await api.resetFacility();

      await loadData();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSwitching(false);
    }
  };

  const riskByAssetId = Object.fromEntries(
    risks.map((risk) => [risk.asset_id, risk])
  );

  const isCustomFacility =
    !!facility && facility.id !== "dallas-dc-01";

  return (
    <div className="dashboard">
      <header className="dashboard__header">
        <h1>🔥THERMOS — Heat Risk Intelligence Platform </h1>

        <button
          onClick={loadData}
          disabled={loading}
        >
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </header>

      <FacilityHeader
        facility={facility}
        overall={overall}
        onChangeLocation={() => setMapOpen(true)}
        onResetToDallas={handleResetToDallas}
        isCustomFacility={isCustomFacility}
      />

      {facility && (
        <FacilityMap
          centerLat={facility.location.lat}
          centerLng={facility.location.lng}
          assets={assets}
          riskByAssetId={riskByAssetId}
          selectedAssetId={selectedAssetId}
          onSelectAsset={setSelectedAssetId}
          facilityId={facility.id}
        />
      )}

      {error && (
        <p className="error-text">
          {error}
        </p>
      )}

      <section className="asset-grid">
        {assets.map((asset) => (
          <AssetCard
            key={asset.id}
            asset={asset}
            risk={riskByAssetId[asset.id]}
            isSelected={asset.id === selectedAssetId}
            onSelect={setSelectedAssetId}
          />
        ))}
      </section>

      <section className="dashboard__grid">
        <HeatPanel
          assetId={selectedAssetId}
        />

        <RiskPriorityPanel
          priorities={priorities}
          selectedAssetId={selectedAssetId}
          onSelect={setSelectedAssetId}
        />

        <ScenarioSimulator
          assetId={selectedAssetId}
        />

        <AgentChat
          selectedAssetId={selectedAssetId}
        />
      </section>

      <LocationMap
        isOpen={mapOpen}
        onClose={() => setMapOpen(false)}
        onConfirm={handleSelectLocation}
        currentLat={
          facility?.location.lat ?? 32.7767
        }
        currentLng={
          facility?.location.lng ?? -96.797
        }
        switching={switching}
        switchError={switchError}
      />
    </div>
  );
}