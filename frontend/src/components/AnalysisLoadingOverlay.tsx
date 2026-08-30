import { useEffect, useState } from "react";

const MESSAGES = [
  "Connecting to FortyGuard thermal intelligence…",
  "Processing heatmap for this location…",
  "This can take up to a minute for a new location…",
  "Calculating THERMOS risk and priority…",
  "Almost there…",
];

export default function AnalysisLoadingOverlay({ label }: { label?: string }) {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((i) => Math.min(i + 1, MESSAGES.length - 1));
    }, 6000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="analysis-loading">
      <div className="analysis-loading__spinner" />
      <p className="analysis-loading__text">{label ?? MESSAGES[index]}</p>
      <p className="analysis-loading__hint">
        FortyGuard analysis is asynchronous — real thermal data takes real time.
      </p>
    </div>
  );
}