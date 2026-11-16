import React from "react";
import { Composition } from "remotion";
import { WillNewsReel } from "./components/WillNewsReel";
import { ReelDirectorProps } from "./types";

const DEFAULT_PROPS: ReelDirectorProps = {
  reel_id: "demo",
  newspaper_name: "La Repubblica",
  edition_date: "15 Novembre 2026",
  scheduled_time: "08:30",
  category: "Tecnologia & Privacy",
  author: "Giulia Boero",
  page: 30,
  original_title: "Demo",
  theme: {
    theme_id: "tech_privacy",
    theme_label: "Tech & Cyber Privacy",
    bg_primary: "#050A14",
    bg_secondary: "#0B162C",
    accent: "#FF3B5C",
    secondary_accent: "#00E5FF",
    text_primary: "#F8FAFC",
    text_muted: "#94A3B8",
    motif: "cyber_grid",
    voice: "it-IT-DiegoNeural",
  },
  fps: 30,
  total_frames: 150,
  total_duration_sec: 5,
  audio_file: "",
  scenes: [],
};

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="WillNewsReel"
      component={WillNewsReel as unknown as React.FC<Record<string, unknown>>}
      durationInFrames={150}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={DEFAULT_PROPS as unknown as Record<string, unknown>}
      calculateMetadata={({ props }) => {
        const p = props as unknown as ReelDirectorProps;
        return {
          durationInFrames: Math.max(60, p.total_frames || 150),
          fps: p.fps || 30,
          width: 1080,
          height: 1920,
        };
      }}
    />
  );
};
