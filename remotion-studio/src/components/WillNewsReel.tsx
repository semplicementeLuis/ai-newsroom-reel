import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { ReelDirectorProps, SceneData, ThemeConfig } from "../types";
import { DynamicBackdrop } from "./DynamicBackdrop";

const FONT_FAMILY = "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";

const KaraokeSubtitles: React.FC<{
  text: string;
  durationFrames: number;
  accent: string;
}> = ({ text, durationFrames, accent }) => {
  const frame = useCurrentFrame();
  const words = text.split(/\s+/).filter(Boolean);
  const progress = Math.min(1, Math.max(0, frame / Math.max(1, durationFrames - 6)));
  const activeWordIdx = Math.floor(progress * words.length);

  // Mostra una finestra scorrevole di max 9 parole alla volta per massima leggibilità
  const windowSize = 9;
  const chunkIndex = Math.floor(activeWordIdx / windowSize);
  const start = chunkIndex * windowSize;
  const visibleWords = words.slice(start, start + windowSize);

  return (
    <div
      style={{
        position: "absolute",
        bottom: 195,
        left: 68,
        right: 68,
        display: "flex",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          backgroundColor: "rgba(5, 8, 16, 0.86)",
          border: `2px solid ${accent}66`,
          borderRadius: 24,
          padding: "22px 30px",
          textAlign: "center",
          boxShadow: "0 16px 40px rgba(0,0,0,0.55)",
          maxWidth: 920,
        }}
      >
        <div
          style={{
            fontSize: 40,
            fontWeight: 800,
            lineHeight: 1.32,
            letterSpacing: -0.4,
            fontFamily: FONT_FAMILY,
          }}
        >
          {visibleWords.map((word, idx) => {
            const globalIdx = start + idx;
            const isCurrent = globalIdx === activeWordIdx;
            const isPast = globalIdx < activeWordIdx;
            return (
              <span
                key={globalIdx}
                style={{
                  color: isCurrent ? accent : isPast ? "#FFFFFF" : "#94A3B8",
                  backgroundColor: isCurrent ? `${accent}24` : "transparent",
                  padding: isCurrent ? "2px 8px" : "0 2px",
                  borderRadius: 10,
                  marginRight: 8,
                  display: "inline-block",
                  transform: isCurrent ? "scale(1.06)" : "scale(1)",
                }}
              >
                {word}
              </span>
            );
          })}
        </div>
      </div>
    </div>
  );
};

const SceneCardContent: React.FC<{
  scene: SceneData;
  theme: ThemeConfig;
}> = ({ scene, theme }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 110 },
  });

  const translateY = interpolate(enter, [0, 1], [65, 0]);
  const opacity = interpolate(enter, [0, 1], [0, 1]);

  const cardEnter = spring({
    frame: Math.max(0, frame - 8),
    fps,
    config: { damping: 15, stiffness: 95 },
  });

  return (
    <div
      style={{
        position: "absolute",
        top: 235,
        left: 72,
        right: 72,
        transform: `translateY(${translateY}px)`,
        opacity,
        fontFamily: FONT_FAMILY,
      }}
    >
      {/* Badge ruolo della scena */}
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 28 }}>
        <div
          style={{
            backgroundColor: theme.accent,
            color: "#050A14",
            fontWeight: 900,
            fontSize: 24,
            padding: "10px 22px",
            borderRadius: 999,
            letterSpacing: 1,
            textTransform: "uppercase",
          }}
        >
          {scene.role}
        </div>
        <div
          style={{
            height: 4,
            width: 80,
            backgroundColor: theme.secondary_accent,
            borderRadius: 4,
          }}
        />
      </div>

      {/* Headline principale */}
      <h1
        style={{
          color: theme.text_primary,
          fontSize: scene.scene_type === "hook_kinetic" ? 72 : 62,
          fontWeight: 900,
          lineHeight: 1.12,
          margin: "0 0 36px 0",
          letterSpacing: -1.5,
        }}
      >
        {scene.headline}
      </h1>

      {/* BLOCCO VISUALE PERSONALIZZATO PER ARGOMENTO */}
      {scene.scene_type === "comparison_bars" && (
        <div
          style={{
            backgroundColor: "rgba(10, 16, 30, 0.88)",
            border: `2px solid ${theme.secondary_accent}88`,
            borderRadius: 28,
            padding: "34px 36px",
            marginBottom: 34,
            transform: `scale(${interpolate(cardEnter, [0, 1], [0.94, 1])})`,
          }}
        >
          <div
            style={{
              color: theme.secondary_accent,
              fontSize: 24,
              fontWeight: 800,
              textTransform: "uppercase",
              marginBottom: 26,
              letterSpacing: 0.8,
            }}
          >
            📊 {scene.visual_payload.chart_title}
          </div>

          {[
            {
              label: scene.visual_payload.left_label,
              val: scene.visual_payload.left_value_display,
              pct: scene.visual_payload.left_pct,
              color: theme.secondary_accent,
            },
            {
              label: scene.visual_payload.right_label,
              val: scene.visual_payload.right_value_display,
              pct: scene.visual_payload.right_pct,
              color: theme.accent,
            },
          ].map((bar, i) => {
            const barWidth = interpolate(
              Math.min(1, Math.max(0, (frame - 12 - i * 8) / 22)),
              [0, 1],
              [0, bar.pct]
            );
            return (
              <div key={i} style={{ marginBottom: i === 0 ? 24 : 0 }}>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    color: "#F8FAFC",
                    fontSize: 28,
                    fontWeight: 700,
                    marginBottom: 10,
                  }}
                >
                  <span>{bar.label}</span>
                  <span style={{ color: bar.color, fontWeight: 900 }}>{bar.val}</span>
                </div>
                <div
                  style={{
                    height: 30,
                    width: "100%",
                    backgroundColor: "rgba(255,255,255,0.08)",
                    borderRadius: 15,
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      height: "100%",
                      width: `${barWidth}%`,
                      backgroundColor: bar.color,
                      borderRadius: 15,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {scene.scene_type === "ui_alert_card" && (
        <div
          style={{
            backgroundColor: "rgba(12, 18, 34, 0.94)",
            border: `2px solid ${theme.accent}`,
            borderRadius: 28,
            padding: "32px 36px",
            marginBottom: 34,
            boxShadow: `0 20px 50px ${theme.accent}25`,
            transform: `scale(${interpolate(cardEnter, [0, 1], [0.92, 1])})`,
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 16,
            }}
          >
            <span style={{ color: theme.secondary_accent, fontWeight: 800, fontSize: 24 }}>
              🔔 {scene.visual_payload.app_name}
            </span>
            <span
              style={{
                backgroundColor: `${theme.accent}33`,
                color: theme.accent,
                fontSize: 20,
                fontWeight: 800,
                padding: "6px 14px",
                borderRadius: 10,
              }}
            >
              {scene.visual_payload.badge}
            </span>
          </div>
          <div style={{ color: "#94A3B8", fontSize: 24, fontWeight: 700, marginBottom: 10 }}>
            {scene.visual_payload.alert_title}
          </div>
          <div style={{ color: "#FFFFFF", fontSize: 32, fontWeight: 700, lineHeight: 1.35 }}>
            {scene.visual_payload.alert_message}
          </div>
        </div>
      )}

      {(scene.scene_type === "hook_kinetic" ||
        scene.scene_type === "stat_counter" ||
        scene.scene_type === "editorial_quote" ||
        scene.scene_type === "cta_outro") &&
        scene.highlight_stat && (
          <div
            style={{
              backgroundColor: "rgba(10, 15, 28, 0.88)",
              borderLeft: `12px solid ${theme.accent}`,
              borderTop: `1px solid ${theme.accent}55`,
              borderRight: `1px solid ${theme.accent}55`,
              borderBottom: `1px solid ${theme.accent}55`,
              borderRadius: 24,
              padding: "30px 36px",
              marginBottom: 34,
              transform: `scale(${interpolate(cardEnter, [0, 1], [0.95, 1])})`,
            }}
          >
            <div
              style={{
                color: theme.accent,
                fontSize: 84,
                fontWeight: 900,
                lineHeight: 1.05,
                marginBottom: 12,
                letterSpacing: -2,
              }}
            >
              {scene.highlight_stat}
            </div>
            <div style={{ color: "#E2E8F0", fontSize: 30, fontWeight: 600, lineHeight: 1.3 }}>
              {scene.highlight_label}
            </div>
          </div>
        )}

      {/* Corpo esplicativo stile Will Media */}
      <p
        style={{
          color: "#E2E8F0",
          fontSize: 36,
          fontWeight: 500,
          lineHeight: 1.4,
          margin: 0,
        }}
      >
        {scene.body}
      </p>
    </div>
  );
};

export const WillNewsReel: React.FC<ReelDirectorProps> = (props) => {
  const frame = useCurrentFrame();
  const { theme, scenes, total_frames } = props;

  // Trova quale scena è attiva per illuminare i segmenti Story in alto
  const activeSceneIdx = scenes.findIndex(
    (s) => frame >= s.start_frame && frame < s.start_frame + s.duration_frames
  );

  const audioSrc = props.audio_url || (props.audio_file ? staticFile(props.audio_file) : "");

  return (
    <AbsoluteFill style={{ backgroundColor: theme.bg_primary, fontFamily: FONT_FAMILY }}>
      <DynamicBackdrop theme={theme} />

      {/* Traccia Audio Narrante Italiana */}
      {audioSrc ? <Audio src={audioSrc} /> : null}

      {/* Header Fisso Stile Will Media (Barre Story + Testata + Tema) */}
      <div
        style={{
          position: "absolute",
          top: 64,
          left: 72,
          right: 72,
          zIndex: 10,
        }}
      >
        {/* Barre Story */}
        <div style={{ display: "flex", gap: 12, marginBottom: 26 }}>
          {scenes.map((s, idx) => {
            let fillPct = 0;
            if (idx < activeSceneIdx) fillPct = 100;
            else if (idx === activeSceneIdx) {
              fillPct = Math.min(100, Math.max(0, ((frame - s.start_frame) / s.duration_frames) * 100));
            }
            return (
              <div
                key={idx}
                style={{
                  flex: 1,
                  height: 8,
                  backgroundColor: "rgba(255,255,255,0.2)",
                  borderRadius: 4,
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    height: "100%",
                    width: `${fillPct}%`,
                    backgroundColor: theme.accent,
                  }}
                />
              </div>
            );
          })}
        </div>

        {/* Riga Testata */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <div style={{ color: "#FFFFFF", fontSize: 28, fontWeight: 900, letterSpacing: 0.6 }}>
              {props.newspaper_name.toUpperCase()}
            </div>
            <div style={{ color: theme.text_muted, fontSize: 22, fontWeight: 600 }}>
              {props.category} • {props.edition_date}
            </div>
          </div>
          <div
            style={{
              border: `2px solid ${theme.secondary_accent}`,
              color: theme.secondary_accent,
              padding: "8px 18px",
              borderRadius: 999,
              fontSize: 20,
              fontWeight: 800,
            }}
          >
            {theme.theme_label.toUpperCase()}
          </div>
        </div>
      </div>

      {/* Sequenza delle Scene Animate */}
      {scenes.map((scene) => (
        <Sequence
          key={scene.index}
          from={scene.start_frame}
          durationInFrames={scene.duration_frames}
        >
          <SceneCardContent scene={scene} theme={theme} />
          <KaraokeSubtitles
            text={scene.voiceover}
            durationFrames={scene.duration_frames}
            accent={theme.accent}
          />
        </Sequence>
      ))}

      {/* Footer & Barra Progresso Continua */}
      <div
        style={{
          position: "absolute",
          bottom: 58,
          left: 72,
          right: 72,
          display: "flex",
          justifyContent: "space-between",
          color: theme.text_muted,
          fontSize: 22,
          fontWeight: 600,
          borderTop: "1px solid rgba(255,255,255,0.16)",
          paddingTop: 18,
        }}
      >
        <span>Fonte: {props.newspaper_name} (Pag. {props.page})</span>
        <span>Di {props.author}</span>
      </div>

      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          height: 10,
          width: `${(frame / Math.max(1, total_frames)) * 100}%`,
          backgroundColor: theme.accent,
        }}
      />
    </AbsoluteFill>
  );
};
