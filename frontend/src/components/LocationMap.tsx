import { useState, useEffect } from "react";
import { MapContainer, TileLayer, Marker, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import AnalysisLoadingOverlay from "./AnalysisLoadingOverlay";

// Fix default marker icon paths (known Vite/Leaflet bundling issue)
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

interface SearchResult {
  display_name: string;
  lat: string;
  lon: string;
}

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (
    lat: number,
    lng: number,
    name: string,
    city: string,
    state: string,
    country: string
  ) => void;
  currentLat: number;
  currentLng: number;
  switching: boolean;
  switchError: string | null;
}

function ClickHandler({ onPick }: { onPick: (lat: number, lng: number) => void }) {
  useMapEvents({
    click(e) {
      onPick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

export default function LocationMap({
  isOpen,
  onClose,
  onConfirm,
  currentLat,
  currentLng,
  switching,
  switchError,
}: Props) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [picked, setPicked] = useState<{ lat: number; lng: number; label: string } | null>(null);

  useEffect(() => {
    if (isOpen) {
      setPicked(null);
      setQuery("");
      setResults([]);
    }
  }, [isOpen]);

  const runSearch = async () => {
    if (!query.trim()) return;
    setSearching(true);
    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
          query
        )}&countrycodes=us&limit=5`
      );
      const data = await res.json();
      setResults(data);
    } catch {
      setResults([]);
    } finally {
      setSearching(false);
    }
  };

  const handlePick = (lat: number, lng: number, label?: string) => {
    setPicked({ lat, lng, label: label || `${lat.toFixed(4)}, ${lng.toFixed(4)}` });
  };

  const handleConfirm = () => {
    if (!picked) return;
    const parts = picked.label.split(",").map((p) => p.trim());
    const city = parts[0] || "Selected Location";
    const state = parts.length > 2 ? parts[parts.length - 3] : "";
    onConfirm(picked.lat, picked.lng, city, city, state, "USA");
  };

  if (!isOpen) return null;

  return (
    <div className="map-modal-overlay" onClick={onClose}>
      <div className="map-modal" onClick={(e) => e.stopPropagation()}>
        <div className="map-modal__header">
          <h3>Select a Facility Location</h3>
          <button className="map-modal__close" onClick={onClose}>✕</button>
        </div>

        <div className="map-modal__search">
          <input
            type="text"
            placeholder="Search a US city or address…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && runSearch()}
          />
          <button onClick={runSearch} disabled={searching}>
            {searching ? "Searching…" : "Search"}
          </button>
        </div>

        {results.length > 0 && (
          <ul className="map-modal__results">
            {results.map((r, i) => (
              <li
                key={i}
                onClick={() => {
                  handlePick(parseFloat(r.lat), parseFloat(r.lon), r.display_name);
                  setResults([]);
                  setQuery(r.display_name);
                }}
              >
                {r.display_name}
              </li>
            ))}
          </ul>
        )}

        <div className="map-modal__map">
          <MapContainer center={[currentLat, currentLng]} zoom={11} style={{ height: "360px", width: "100%" }}>
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution="&copy; OpenStreetMap contributors"
            />
            <ClickHandler onPick={(lat, lng) => handlePick(lat, lng)} />
            {picked && <Marker position={[picked.lat, picked.lng]} />}
          </MapContainer>
        </div>

        <p className="map-modal__hint">
          Click anywhere on the map, or search above. FortyGuard coverage is US-only — we'll verify coverage when you confirm.
        </p>

        {switchError && <p className="error-text">{switchError}</p>}
        {switching && <AnalysisLoadingOverlay />}

        <div className="map-modal__footer">
          {picked && <span className="map-modal__picked">📍 {picked.label}</span>}
          <button className="map-modal__confirm" onClick={handleConfirm} disabled={!picked || switching}>
            {switching ? "Verifying coverage & analyzing…" : "Analyze This Location"}
          </button>
        </div>
      </div>
    </div>
  );
}