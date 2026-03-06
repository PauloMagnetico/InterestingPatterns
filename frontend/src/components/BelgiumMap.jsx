/**
 * Clickable SVG map of Belgium with 3 regions: BE1 (Brussels), BE2 (Flanders), BE3 (Wallonia).
 * Clicking a region toggles it as the NUTS filter.
 */

const REGIONS = {
  BE2: {
    label: "Vlaanderen",
    // Flanders - northern strip (Brussels drawn on top)
    d: "M 45,85 L 55,65 L 80,55 L 120,50 L 165,48 L 200,50 L 240,48 L 280,50 L 320,48 L 360,50 L 400,48 L 445,55 L 475,65 L 485,85 L 490,110 L 488,140 L 485,165 L 470,172 L 445,168 L 415,173 L 385,168 L 355,173 L 325,168 L 295,173 L 265,168 L 240,172 L 240,148 L 210,148 L 210,172 L 188,172 L 158,168 L 128,173 L 98,168 L 68,173 L 48,168 L 40,152 L 38,130 L 40,108 Z",
    labelPos: [175, 115],
  },
  BE1: {
    label: "Brussel",
    // Brussels Capital — small rectangle enclave in Flanders
    d: "M 210,148 L 240,148 L 240,172 L 210,172 Z",
    labelPos: [225, 163],
  },
  BE3: {
    label: "Wallonië",
    // Wallonia — southern region
    d: "M 40,152 L 48,168 L 68,173 L 98,168 L 128,173 L 158,168 L 188,172 L 210,172 L 240,172 L 265,168 L 295,173 L 325,168 L 355,173 L 385,168 L 415,173 L 445,168 L 470,172 L 485,165 L 495,190 L 495,235 L 490,268 L 482,298 L 468,325 L 448,347 L 420,362 L 385,370 L 340,374 L 285,372 L 235,366 L 188,355 L 148,338 L 112,315 L 82,288 L 60,258 L 46,228 L 38,198 L 38,175 Z",
    labelPos: [265, 280],
  },
};

const COLORS = {
  default: "#e8edf2",
  hover: "#c8d8e8",
  active: "#2563eb",
  activeHover: "#1d4ed8",
  stroke: "#ffffff",
  strokeActive: "#1e40af",
};

export default function BelgiumMap({ value, onChange }) {
  const [hovered, setHovered] = React.useState(null);

  const handleClick = (code) => {
    onChange(value === code ? "" : code);
  };

  return (
    <div style={{ width: "100%", maxWidth: 320 }}>
      <svg
        viewBox="30 40 475 345"
        width="100%"
        style={{ display: "block", cursor: "pointer" }}
        aria-label="Kaart van België — klik op een regio"
      >
        {/* Render Wallonia first, then Flanders (on top), then Brussels (topmost) */}
        {["BE3", "BE2", "BE1"].map((code) => {
          const region = REGIONS[code];
          const isActive = value === code;
          const isHovered = hovered === code;
          const fill = isActive
            ? isHovered ? COLORS.activeHover : COLORS.active
            : isHovered ? COLORS.hover : COLORS.default;

          return (
            <g key={code}>
              <path
                d={region.d}
                fill={fill}
                stroke={isActive ? COLORS.strokeActive : COLORS.stroke}
                strokeWidth={isActive ? 1.5 : 1}
                onClick={() => handleClick(code)}
                onMouseEnter={() => setHovered(code)}
                onMouseLeave={() => setHovered(null)}
                style={{ transition: "fill 0.15s ease" }}
              />
              <text
                x={region.labelPos[0]}
                y={region.labelPos[1]}
                textAnchor="middle"
                fontSize={code === "BE1" ? 7 : 13}
                fontWeight={isActive ? "600" : "400"}
                fill={isActive ? "#ffffff" : "#374151"}
                style={{ pointerEvents: "none", userSelect: "none" }}
              >
                {region.label}
              </text>
            </g>
          );
        })}
      </svg>
      {value && (
        <div style={{ textAlign: "center", marginTop: 4 }}>
          <button
            onClick={() => onChange("")}
            style={{
              fontSize: 11,
              color: "#6b7280",
              background: "none",
              border: "none",
              cursor: "pointer",
              textDecoration: "underline",
              padding: 0,
            }}
          >
            filter wissen
          </button>
        </div>
      )}
    </div>
  );
}

// React must be in scope for JSX — import at top of file that uses this
import React from "react";
