import { useState } from "react";

export default function AgentGuidance() {
  const [open, setOpen] = useState(false);

  return (
    <div className="agent-guidance">
      <button className="agent-guidance__toggle" onClick={() => setOpen(!open)}>
        {open ? "Hide" : "What can I ask THERMOS Agent?"} <span>{open ? "▲" : "▼"}</span>
      </button>
      {open && (
        <div className="agent-guidance__body">
          <p><strong>THERMOS Agent</strong> explains and recommends based on the live risk data on this screen — it never invents numbers.</p>
          <div className="agent-guidance__grid">
            <div>
              <div className="agent-guidance__label">✅ Good for</div>
              <ul>
                <li>"Which zone needs attention first, and why?"</li>
                <li>"What's driving the Loading Dock's risk score?"</li>
                <li>"Recommend an intervention for the Outdoor Yard"</li>
                <li>"Summarize today's risk for a report"</li>
              </ul>
            </div>
            <div>
              <div className="agent-guidance__label">❌ Not for</div>
              <ul>
                <li>Locations/data outside this facility</li>
                <li>Weather forecasts unrelated to these assets</li>
                <li>Medical or legal advice</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}