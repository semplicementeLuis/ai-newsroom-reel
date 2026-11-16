export interface ThemeConfig {
  theme_id: string;
  theme_label: string;
  bg_primary: string;
  bg_secondary: string;
  accent: string;
  secondary_accent: string;
  text_primary: string;
  text_muted: string;
  motif: "cyber_grid" | "network_nodes" | "financial_bars" | "radar_routes" | "editorial_frames";
  voice: string;
}

export interface SceneData {
  index: number;
  role: string;
  headline: string;
  highlight_stat: string;
  highlight_label: string;
  body: string;
  voiceover: string;
  scene_type: "hook_kinetic" | "stat_counter" | "comparison_bars" | "ui_alert_card" | "editorial_quote" | "cta_outro";
  visual_payload: Record<string, any>;
  duration_sec: number;
  start_frame: number;
  duration_frames: number;
}

export interface ReelDirectorProps {
  reel_id: string;
  newspaper_name: string;
  edition_date: string;
  scheduled_time: string;
  category: string;
  author: string;
  page: number;
  original_title: string;
  theme: ThemeConfig;
  fps: number;
  total_frames: number;
  total_duration_sec: number;
  audio_file: string;
  audio_url?: string;
  scenes: SceneData[];
}
