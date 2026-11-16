import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { ThemeConfig } from "../types";

export const DynamicBackdrop: React.FC<{ theme: ThemeConfig }> = ({ theme }) => {
  const frame = useCurrentFrame();
  const driftX = Math.sin(frame / 45) * 40;
  const driftY = Math.cos(frame / 55) * 40;
  const pulse = interpolate(Math.sin(frame / 25), [-1, 1], [0.22, 0.42]);

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(165deg, ${theme.bg_primary} 0%, ${theme.bg_secondary} 100%)`,
        overflow: "hidden",
      }}
    >
      {/* Bagliore radiale primario */}
      <div
        style={{
          position: "absolute",
          top: -180 + driftY,
          right: -180 + driftX,
          width: 900,
          height: 900,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${theme.accent} 0%, transparent 70%)`,
          opacity: pulse,
          filter: "blur(60px)",
        }}
      />

      {/* Bagliore radiale secondario */}
      <div
        style={{
          position: "absolute",
          bottom: -220 - driftY,
          left: -200 - driftX,
          width: 850,
          height: 850,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${theme.secondary_accent} 0%, transparent 70%)`,
          opacity: 0.25,
          filter: "blur(70px)",
        }}
      />

      {/* Motif specifico per argomento */}
      {theme.motif === "cyber_grid" && (
        <svg width="1080" height="1920" style={{ position: "absolute", opacity: 0.14 }}>
          <defs>
            <pattern id="cyberGrid" width="80" height="80" patternUnits="userSpaceOnUse">
              <path d="M 80 0 L 0 0 0 80" fill="none" stroke={theme.secondary_accent} strokeWidth="1.5" />
            </pattern>
          </defs>
          <rect width="1080" height="1920" fill="url(#cyberGrid)" transform={`translate(0, ${(frame * 1.2) % 80})`} />
        </svg>
      )}

      {theme.motif === "financial_bars" && (
        <svg width="1080" height="1920" style={{ position: "absolute", opacity: 0.12 }}>
          {Array.from({ length: 12 }).map((_, i) => {
            const h = 250 + Math.sin(frame / 20 + i) * 140;
            return (
              <rect
                key={i}
                x={i * 95 + 15}
                y={1920 - h}
                width={52}
                height={h}
                rx={8}
                fill={i % 2 === 0 ? theme.accent : theme.secondary_accent}
              />
            );
          })}
        </svg>
      )}

      {theme.motif === "radar_routes" && (
        <svg width="1080" height="1920" style={{ position: "absolute", opacity: 0.15 }}>
          {[220, 380, 540, 700].map((r, idx) => (
            <circle
              key={idx}
              cx={540}
              cy={760}
              r={r + ((frame * 1.5) % 160)}
              fill="none"
              stroke={theme.secondary_accent}
              strokeWidth="2"
              strokeDasharray="12 12"
            />
          ))}
        </svg>
      )}

      {theme.motif === "network_nodes" && (
        <svg width="1080" height="1920" style={{ position: "absolute", opacity: 0.16 }}>
          {Array.from({ length: 8 }).map((_, i) => {
            const cx = 140 + ((i * 230) % 820);
            const cy = 260 + i * 190 + Math.sin(frame / 22 + i) * 28;
            return (
              <g key={i}>
                <circle cx={cx} cy={cy} r={14} fill={theme.accent} />
                <line x1={cx} y1={cy} x2={540} y2={960} stroke={theme.secondary_accent} strokeWidth="2" />
              </g>
            );
          })}
        </svg>
      )}

      {theme.motif === "editorial_frames" && (
        <svg width="1080" height="1920" style={{ position: "absolute", opacity: 0.13 }}>
          <rect
            x={70}
            y={200}
            width={940}
            height={1520}
            rx={32}
            fill="none"
            stroke={theme.accent}
            strokeWidth="3"
          />
          <rect
            x={96}
            y={226}
            width={888}
            height={1468}
            rx={24}
            fill="none"
            stroke={theme.secondary_accent}
            strokeWidth="1.5"
            strokeDasharray="14 10"
          />
        </svg>
      )}
    </AbsoluteFill>
  );
};
