"""
Art Director AI & Generatore Voiceover (stile Will Media):
Trasforma i 5 Reel monotematici di `newsroom.py` in progetti video personalizzati
che adattano palette, motif visivi, tipologia di scena (grafici comparativi,
alert UI, contatori animati, citazioni editoriali) e voce narrante all'argomento.
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
from pathlib import Path
from typing import Any

import edge_tts


TOPIC_THEMES: dict[str, dict[str, Any]] = {
    "tech_privacy": {
        "theme_id": "tech_privacy",
        "theme_label": "Tech & Cyber Privacy",
        "bg_primary": "#050A14",
        "bg_secondary": "#0B162C",
        "accent": "#FF3B5C",
        "secondary_accent": "#00E5FF",
        "text_primary": "#F8FAFC",
        "text_muted": "#94A3B8",
        "motif": "cyber_grid",
        "voice": "it-IT-DiegoNeural",
        "voice_rate": "+6%",
    },
    "politics_ai": {
        "theme_id": "politics_ai",
        "theme_label": "Politica & Social AI",
        "bg_primary": "#0B0716",
        "bg_secondary": "#1A1033",
        "accent": "#EC4899",
        "secondary_accent": "#8B5CF6",
        "text_primary": "#F8FAFC",
        "text_muted": "#CBD5E1",
        "motif": "network_nodes",
        "voice": "it-IT-IsabellaNeural",
        "voice_rate": "+6%",
    },
    "economy_data": {
        "theme_id": "economy_data",
        "theme_label": "Economia & Data Journalism",
        "bg_primary": "#07100E",
        "bg_secondary": "#0D1F1B",
        "accent": "#10B981",
        "secondary_accent": "#F59E0B",
        "text_primary": "#F8FAFC",
        "text_muted": "#A7F3D0",
        "motif": "financial_bars",
        "voice": "it-IT-DiegoNeural",
        "voice_rate": "+5%",
    },
    "world_breaking": {
        "theme_id": "world_breaking",
        "theme_label": "Esteri & Breaking News",
        "bg_primary": "#080F1A",
        "bg_secondary": "#111E33",
        "accent": "#F59E0B",
        "secondary_accent": "#38BDF8",
        "text_primary": "#F8FAFC",
        "text_muted": "#94A3B8",
        "motif": "radar_routes",
        "voice": "it-IT-DiegoNeural",
        "voice_rate": "+6%",
    },
    "culture_cinema": {
        "theme_id": "culture_cinema",
        "theme_label": "Cultura, Cinema & Società",
        "bg_primary": "#120A0B",
        "bg_secondary": "#241115",
        "accent": "#FBBF24",
        "secondary_accent": "#FB7185",
        "text_primary": "#FFFBEB",
        "text_muted": "#FDE68A",
        "motif": "editorial_frames",
        "voice": "it-IT-ElsaNeural",
        "voice_rate": "+4%",
    },
}


def pick_theme_for_reel(reel_data: dict[str, Any]) -> dict[str, Any]:
    cat = reel_data.get("category", "").lower()
    rid = reel_data.get("reel_id", "").lower()
    if "privacy" in cat or "meta" in rid or "tecnologia" in cat:
        return TOPIC_THEMES["tech_privacy"]
    if "politica" in cat or "bot" in rid:
        return TOPIC_THEMES["politics_ai"]
    if "economia" in cat or "manovra" in rid:
        return TOPIC_THEMES["economy_data"]
    if "esteri" in cat or "mondo" in cat or "voli" in rid:
        return TOPIC_THEMES["world_breaking"]
    return TOPIC_THEMES["culture_cinema"]


def build_scene_visuals(reel_data: dict[str, Any], theme: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Assegna a ciascuna delle 5 scene un tipo di componente Remotion personalizzato
    in stile Will Media in base al tema e ai dati dell'articolo.
    """
    rid = reel_data["reel_id"]
    slides = reel_data["slides"]
    enriched_scenes: list[dict[str, Any]] = []

    for idx, slide in enumerate(slides):
        scene: dict[str, Any] = {
            "index": idx,
            "role": slide["role"],
            "headline": slide["headline"],
            "highlight_stat": slide["highlight_stat"],
            "highlight_label": slide["highlight_label"],
            "body": slide["body"],
            "voiceover": slide["voiceover"],
            "scene_type": "stat_counter",
            "visual_payload": {},
        }

        if idx == 0:
            scene["scene_type"] = "hook_kinetic"
            scene["visual_payload"] = {
                "kicker": f"{reel_data['category'].upper()} • PAG. {reel_data['page']}",
                "highlight_words": [w for w in slide["headline"].split() if w.isupper() or len(w) > 7][:2],
            }
        elif idx == len(slides) - 1:
            scene["scene_type"] = "cta_outro"
            scene["visual_payload"] = {
                "action_label": slide["highlight_stat"],
                "prompt_question": slide["headline"],
            }
        else:
            # Personalizzazione specifica per argomento!
            if "meta" in rid and idx == 2:
                scene["scene_type"] = "ui_alert_card"
                scene["visual_payload"] = {
                    "app_name": "Facebook per Android",
                    "alert_title": "Richiesta autorizzazione generica",
                    "alert_message": "«Abilitare altre funzioni» → Accesso permanente a Foto, Video e Metadati di 20M di utenti.",
                    "badge": "ART. 122 CODICE PRIVACY",
                }
            elif "bot" in rid and idx in (1, 2):
                scene["scene_type"] = "ui_alert_card"
                scene["visual_payload"] = {
                    "app_name": "Commento Bot Intercettato",
                    "alert_title": "@profilo_hackerato • Risposta automatica AI",
                    "alert_message": (
                        "«Non posso scrivere un messaggio volto a insultare uno specifico partito politico.»"
                        if idx == 1
                        else "«Non posso scrivere un messaggio per convincere specifici eurodeputati a sostenere una proposta.»"
                    ),
                    "badge": "FILTRO ETICO AI ESPOSTO",
                }
            elif "manovra" in rid and idx == 1:
                scene["scene_type"] = "comparison_bars"
                scene["visual_payload"] = {
                    "chart_title": "Crediti Superbonus delle imprese",
                    "left_label": "Atteso (2026-27)",
                    "left_value_display": "2 anni",
                    "left_pct": 25,
                    "right_label": "Manovra (Spalmacrediti)",
                    "right_value_display": "10 anni",
                    "right_pct": 100,
                }
            elif "voli" in rid and idx == 3:
                scene["scene_type"] = "comparison_bars"
                scene["visual_payload"] = {
                    "chart_title": "Fondi Congresso per la Rete Aerea USA",
                    "left_label": "Richiesti (FAA)",
                    "left_value_display": "50 Mld $",
                    "left_pct": 100,
                    "right_label": "Concessi",
                    "right_value_display": "12,5 Mld $",
                    "right_pct": 25,
                }
            elif "film_cinese" in rid and idx == 1:
                scene["scene_type"] = "comparison_bars"
                scene["visual_payload"] = {
                    "chart_title": "Sanxingdui (1° Film AI in Cina)",
                    "left_label": "Budget Speso",
                    "left_value_display": "1,3 Mln €",
                    "left_pct": 100,
                    "right_label": "Incasso Sale",
                    "right_value_display": "230 Mila €",
                    "right_pct": 18,
                }
            elif idx == 3:
                scene["scene_type"] = "editorial_quote"
                scene["visual_payload"] = {
                    "quote_source": f"Inchiesta di {reel_data['author']} • La Repubblica",
                }
            else:
                scene["scene_type"] = "stat_counter"

        enriched_scenes.append(scene)

    return enriched_scenes


async def _synthesize_edge_tts(text: str, voice: str, rate: str, out_mp3: Path) -> None:
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
    await communicate.save(str(out_mp3))


def get_audio_duration_sec(audio_path: Path) -> float:
    """Usa ffmpeg (bundled con imageio-ffmpeg) per leggere la durata esatta dell'audio."""
    import imageio_ffmpeg

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    res = subprocess.run(
        [ffmpeg_exe, "-i", str(audio_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    # Cerca "Duration: 00:00:05.12"
    import re

    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", res.stderr)
    if m:
        h, mins, secs = int(m.group(1)), int(m.group(2)), float(m.group(3))
        return h * 3600 + mins * 60 + secs
    return 4.5


def concat_audio_clips(clip_paths: list[Path], out_mp3: Path) -> Path:
    """Concatena i clip audio MP3 delle singole scene in una traccia unica continua."""
    import imageio_ffmpeg

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    list_file = out_mp3.parent / "audio_concat.txt"
    lines = [f"file '{p.resolve()}'" for p in clip_paths]
    list_file.write_text("\n".join(lines), encoding="utf-8")

    subprocess.run(
        [
            ffmpeg_exe,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
            "-c:a",
            "libmp3lame",
            "-q:a",
            "2",
            str(out_mp3),
        ],
        capture_output=True,
        check=True,
    )
    return out_mp3


def prepare_reel_director_package(
    reel_data: dict[str, Any],
    newspaper_name: str,
    edition_date: str,
    audio_dir: Path,
    fps: int = 30,
) -> dict[str, Any]:
    """
    Genera la regia visiva personalizzata per argomento + la traccia audio
    TTS in italiano scena per scena, calcolando i frame esatti di ogni scena.
    """
    audio_dir.mkdir(parents=True, exist_ok=True)
    theme = pick_theme_for_reel(reel_data)
    scenes = build_scene_visuals(reel_data, theme)

    clip_paths: list[Path] = []
    current_frame = 0

    for scene in scenes:
        clip_path = audio_dir / f"scene_{scene['index'] + 1:02d}.mp3"
        asyncio.run(
            _synthesize_edge_tts(
                scene["voiceover"],
                voice=theme["voice"],
                rate=theme["voice_rate"],
                out_mp3=clip_path,
            )
        )
        dur = get_audio_duration_sec(clip_path)
        # Aggiungi un piccolo margine di 0.15s per respiro visivo naturale
        duration_frames = max(int((dur + 0.15) * fps), 60)
        scene["duration_sec"] = round(dur, 2)
        scene["start_frame"] = current_frame
        scene["duration_frames"] = duration_frames
        current_frame += duration_frames
        clip_paths.append(clip_path)

    full_audio_path = audio_dir / "voiceover_full.mp3"
    concat_audio_clips(clip_paths, full_audio_path)

    return {
        "reel_id": reel_data["reel_id"],
        "newspaper_name": newspaper_name,
        "edition_date": edition_date,
        "scheduled_time": reel_data["scheduled_time"],
        "category": reel_data["category"],
        "author": reel_data["author"],
        "page": reel_data["page"],
        "original_title": reel_data["original_title"],
        "theme": theme,
        "fps": fps,
        "total_frames": current_frame,
        "total_duration_sec": round(current_frame / float(fps), 2),
        "audio_file": full_audio_path.name,
        "scenes": scenes,
    }
