"""
Pipeline principale (v3 — Stile Will Media con Art Director AI + Remotion + Voiceover TTS):
1. Scansiona il quotidiano PDF caricato in `input/` tramite `scraper.py` (PyMuPDF layout-aware)
2. La Redazione AI (`newsroom.py`) seleziona i 5 articoli più interessanti e prepara
   5 Reel singoli (1 notizia = 1 Reel) pianificati lungo la giornata (08:30, 11:30, 14:30, 18:00, 21:00)
3. L'Art Director AI (`art_director.py`) personalizza tema visivo, grafici/alert per singola scena
   e genera il voiceover parlato in italiano (`edge-tts`), calcolando i frame esatti
4. Remotion (`remotion-studio/`) renderizza i 5 video MP4 1080x1920 @ 30fps con animazioni fluide,
   grafici animati, sottotitoli sincronizzati parola per parola e traccia audio integrata
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from art_director import prepare_reel_director_package
from newsroom import build_daily_editorial_plan
from renderer import generate_multi_reel_dashboard, render_slide
from scraper import scrape_newspaper_pdf


def find_input_pdf(input_dir: Path) -> Path:
    pdfs = sorted(
        [p for p in input_dir.glob("*.pdf") if p.name != "quotidiano_esempio.pdf"],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if pdfs:
        return pdfs[0]
    fallback = input_dir / "quotidiano_esempio.pdf"
    if fallback.exists():
        return fallback
    raise FileNotFoundError(f"Nessun file PDF trovato in {input_dir}")


def render_with_remotion(
    remotion_dir: Path,
    props_json_path: Path,
    audio_mp3_path: Path,
    output_mp4_path: Path,
    reel_id: str,
) -> Path:
    """
    Copia la traccia audio nella cartella `public/` di Remotion, aggiorna `audio_file`
    e lancia `npx remotion render` per compilare il video MP4 finale con audio e animazioni.
    """
    public_dir = remotion_dir / "public"
    public_dir.mkdir(parents=True, exist_ok=True)
    public_audio_name = f"{reel_id}.mp3"
    shutil.copy2(audio_mp3_path, public_dir / public_audio_name)

    props = json.loads(props_json_path.read_text(encoding="utf-8"))
    props["audio_file"] = public_audio_name
    props_json_path.write_text(json.dumps(props, indent=2, ensure_ascii=False), encoding="utf-8")

    cmd = [
        "npx",
        "remotion",
        "render",
        "src/index.ts",
        "WillNewsReel",
        str(output_mp4_path.resolve()),
        f"--props={props_json_path.resolve()}",
        "--log=error",
    ]
    subprocess.run(cmd, cwd=str(remotion_dir), check=True)
    return output_mp4_path


def run_pipeline(
    pdf_path: Path,
    output_dir: Path,
    num_reels: int = 5,
    remotion_dir: Path | None = None,
) -> dict[str, Any]:
    base_dir = Path(__file__).parent
    remotion_studio = remotion_dir or (base_dir / "remotion-studio")

    output_dir.mkdir(parents=True, exist_ok=True)
    reels_root = output_dir / "reels"
    if reels_root.exists():
        shutil.rmtree(reels_root)
    reels_root.mkdir(parents=True, exist_ok=True)

    print(f"📰 [1/4] Scansione ed estrazione articoli da: {pdf_path.name} ...")
    scraped_data = scrape_newspaper_pdf(pdf_path)
    extracted_json_path = output_dir / "01_articoli_estratti.json"
    extracted_json_path.write_text(
        json.dumps(scraped_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(
        f"   ✓ Pagine analizzate: {scraped_data['total_pages_scanned']} | "
        f"Articoli estratti: {scraped_data['total_articles_extracted']} -> {extracted_json_path.name}"
    )

    print(f"🧠 [2/4] Selezione Redazione AI dei {num_reels} articoli migliori (1 notizia = 1 Reel)...")
    daily_plan = build_daily_editorial_plan(scraped_data, target_reels=num_reels)
    plan_json_path = output_dir / "02_piano_editoriale_5_reel.json"
    plan_json_path.write_text(
        json.dumps(daily_plan, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"🎬 [3/4] Art Director AI + Voiceover TTS + Rendering Remotion (stile Will Media)...")
    rendered_bundles: list[dict[str, Any]] = []

    for idx, reel_data in enumerate(daily_plan["selected_reels"], start=1):
        time_slug = reel_data["scheduled_time"].replace(":", "-")
        folder_name = f"{idx:02d}_{time_slug}_{reel_data['reel_id']}"
        reel_dir = reels_root / folder_name
        slides_dir = reel_dir / "slides"
        audio_dir = reel_dir / "audio"
        slides_dir.mkdir(parents=True, exist_ok=True)
        audio_dir.mkdir(parents=True, exist_ok=True)

        # Scheda editoriale base
        single_json = reel_dir / "scheda_reel.json"
        single_json.write_text(
            json.dumps(reel_data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # Regia personalizzata per argomento + Voiceover italiano TTS
        director_pkg = prepare_reel_director_package(
            reel_data=reel_data,
            newspaper_name=daily_plan["newspaper_name"],
            edition_date=daily_plan["edition_date"],
            audio_dir=audio_dir,
            fps=30,
        )
        director_json = reel_dir / "director_props.json"
        director_json.write_text(
            json.dumps(director_pkg, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # Slide PNG di anteprima rapida
        slide_paths: list[Path] = []
        for s_idx, s_data in enumerate(reel_data["slides"]):
            img = render_slide(
                slide_data=s_data,
                slide_idx=s_idx,
                total_slides=len(reel_data["slides"]),
                newspaper_name=daily_plan["newspaper_name"],
                edition_date=daily_plan["edition_date"],
                category=reel_data["category"],
                source_page=reel_data["page"],
            )
            sp = slides_dir / f"slide_{s_idx + 1:02d}.png"
            img.save(sp, format="PNG")
            slide_paths.append(sp)

        # Rendering video MP4 con Remotion (animazioni + grafici + audio + sottotitoli karaoke)
        video_path = reel_dir / "reel.mp4"
        print(
            f"   🎥 Rendering Reel #{idx}/{len(daily_plan['selected_reels'])} "
            f"[{director_pkg['theme']['theme_label']} • {director_pkg['total_duration_sec']}s] ..."
        )
        render_with_remotion(
            remotion_dir=remotion_studio,
            props_json_path=director_json,
            audio_mp3_path=audio_dir / "voiceover_full.mp3",
            output_mp4_path=video_path,
            reel_id=reel_data["reel_id"],
        )
        print(f"      ✓ Pronto: {video_path.relative_to(output_dir)}")

        rendered_bundles.append(
            {
                "reel_data": reel_data,
                "director_pkg": director_pkg,
                "reel_dir": reel_dir,
                "slide_paths": slide_paths,
                "video_path": video_path,
                "json_path": single_json,
            }
        )

    print("🌐 [4/4] Aggiornamento Dashboard Piano Editoriale Giornaliero...")
    dashboard_path = output_dir / "anteprima_redazione.html"
    generate_multi_reel_dashboard(scraped_data, daily_plan, rendered_bundles, dashboard_path)
    print(f"   ✓ Dashboard pronta: {dashboard_path}")

    return {
        "extracted_json_path": extracted_json_path,
        "plan_json_path": plan_json_path,
        "dashboard_path": dashboard_path,
        "bundles": rendered_bundles,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Quotidiano PDF -> 5 Reel Personalizzati (Remotion + TTS)")
    parser.add_argument("--pdf", type=str, default="", help="Percorso del PDF (default: ultimo PDF in input/)")
    parser.add_argument("--out", type=str, default=str(Path(__file__).parent / "output"), help="Cartella output")
    parser.add_argument("--reels", type=int, default=5, help="Numero di Reel giornalieri da generare (default: 5)")
    args = parser.parse_args()

    base_dir = Path(__file__).parent
    pdf_path = Path(args.pdf).expanduser().resolve() if args.pdf else find_input_pdf(base_dir / "input")
    run_pipeline(pdf_path, Path(args.out).expanduser().resolve(), num_reels=args.reels)


if __name__ == "__main__":
    main()
