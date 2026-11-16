"""
Motore grafico e video per Instagram Reel (formato 9:16 - 1080x1920).
Genera:
1. Slide PNG 1080x1920 ad alta risoluzione con design editoriale moderno
2. Video MP4 1080x1920 (30 fps) con animazione barra progresso, zoom leggero e transizioni fade
3. Dashboard HTML interattiva con tutti i passaggi della Redazione AI
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920

# Palette colori per ruolo della slide
ACCENT_PALETTE = [
    ("#FF3B5C", "#FF8A00"),  # Slide 1: Hook (Rosso-Arancio vibrante)
    ("#00E5FF", "#3B82F6"),  # Slide 2: Il Fatto (Ciano-Blu)
    ("#10B981", "#34D399"),  # Slide 3: Il Dato Chiave (Verde Smeraldo)
    ("#A855F7", "#EC4899"),  # Slide 4: L'Impatto (Viola-Magenta)
    ("#F59E0B", "#EF4444"),  # Slide 5: Call to Action (Ambra-Corallo)
]


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/System/Library/Fonts/SFNS.ttf",
        ]
        if bold
        else [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/System/Library/Fonts/SFNS.ttf",
        ]
    )
    for path in candidates:
        if Path(path).exists():
            try:
                index = 1 if (bold and path.endswith(".ttc")) else 0
                return ImageFont.truetype(path, size=size, index=index)
            except Exception:
                try:
                    return ImageFont.truetype(path, size=size)
                except Exception:
                    continue
    return ImageFont.load_default()


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def create_editorial_background(accent_hex: str, secondary_hex: str) -> Image.Image:
    """Crea uno sfondo scuro editoriale 1080x1920 con bagliori radiali morbidi e griglia."""
    y_idx = np.linspace(0, 1, H)[:, None]
    x_idx = np.linspace(0, 1, W)[None, :]

    # Base dark slate (#070B14 -> #0F172A)
    r = 7 + 8 * y_idx
    g = 11 + 12 * y_idx
    b = 20 + 22 * y_idx
    base = np.stack([np.broadcast_to(r, (H, W)), np.broadcast_to(g, (H, W)), np.broadcast_to(b, (H, W))], axis=-1)

    # Glow 1 (in alto a destra)
    ar, ag, ab = hex_to_rgb(accent_hex)
    dist1 = np.sqrt((x_idx - 0.85) ** 2 + ((y_idx - 0.18) * 1.4) ** 2)
    glow1 = np.exp(-dist1 * 3.8)[..., None] * 0.35
    base += glow1 * np.array([ar, ag, ab])

    # Glow 2 (in basso a sinistra)
    sr, sg, sb = hex_to_rgb(secondary_hex)
    dist2 = np.sqrt((x_idx - 0.15) ** 2 + ((y_idx - 0.82) * 1.4) ** 2)
    glow2 = np.exp(-dist2 * 4.2)[..., None] * 0.25
    base += glow2 * np.array([sr, sg, sb])

    arr = np.clip(base, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr, mode="RGB")

    # Griglia sottile di sfondo in stile editoriale finanziario/tech
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for gx in range(0, W, 90):
        draw.line([(gx, 0), (gx, H)], fill=(255, 255, 255, 9), width=1)
    for gy in range(0, H, 90):
        draw.line([(0, gy), (W, gy)], fill=(255, 255, 255, 9), width=1)

    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def wrap_pil_text(draw: ImageDraw.ImageDraw, text: str, font: Any, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if (bbox[2] - bbox[0]) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def render_slide(
    slide_data: dict[str, Any],
    slide_idx: int,
    total_slides: int,
    newspaper_name: str,
    edition_date: str,
    category: str,
    source_page: int,
) -> Image.Image:
    accent_hex, secondary_hex = ACCENT_PALETTE[slide_idx % len(ACCENT_PALETTE)]
    accent_rgb = hex_to_rgb(accent_hex)

    img = create_editorial_background(accent_hex, secondary_hex).convert("RGBA")
    draw = ImageDraw.Draw(img)

    font_brand = load_font(28, bold=True)
    font_meta = load_font(24, bold=False)
    font_badge = load_font(26, bold=True)
    font_role = load_font(26, bold=True)
    font_headline = load_font(68, bold=True)
    font_body = load_font(40, bold=False)
    font_stat_val = load_font(96, bold=True)
    font_stat_lbl = load_font(30, bold=False)
    font_footer = load_font(24, bold=False)

    pad_x = 84

    # 1. Story indicator bars in alto
    bar_top = 88
    gap = 14
    bar_w = (W - 2 * pad_x - (total_slides - 1) * gap) // total_slides
    for i in range(total_slides):
        bx0 = pad_x + i * (bar_w + gap)
        bx1 = bx0 + bar_w
        color = (*accent_rgb, 255) if i <= slide_idx else (255, 255, 255, 55)
        draw.rounded_rectangle([bx0, bar_top, bx1, bar_top + 8], radius=4, fill=color)

    # 2. Header Testata + Data
    header_y = 128
    draw.text((pad_x, header_y), newspaper_name.upper(), font=font_brand, fill=(248, 250, 252, 240))
    slide_counter = f"{slide_idx + 1}/{total_slides}"
    cnt_bbox = draw.textbbox((0, 0), slide_counter, font=font_brand)
    draw.text(
        (W - pad_x - (cnt_bbox[2] - cnt_bbox[0]), header_y),
        slide_counter,
        font=font_brand,
        fill=(*accent_rgb, 255),
    )
    draw.text((pad_x, header_y + 38), f"Rassegna AI • {edition_date}", font=font_meta, fill=(148, 163, 184, 220))

    # 3. Badge Categoria + Ruolo Slide
    y = 250
    cat_text = f"  {category.upper()}  "
    cat_bbox = draw.textbbox((0, 0), cat_text, font=font_badge)
    cat_w = cat_bbox[2] - cat_bbox[0] + 24
    cat_h = 54
    draw.rounded_rectangle([pad_x, y, pad_x + cat_w, y + cat_h], radius=27, fill=(*accent_rgb, 255))
    draw.text((pad_x + 12, y + 11), cat_text, font=font_badge, fill=(10, 14, 23, 255))

    role_label = slide_data.get("role", "FOCUS").upper()
    draw.text((pad_x + cat_w + 22, y + 12), f"// {role_label}", font=font_role, fill=(203, 213, 225, 220))

    # 4. Headline principale
    y += 110
    headline = slide_data.get("headline", "")
    h_lines = wrap_pil_text(draw, headline, font_headline, W - 2 * pad_x)
    for line in h_lines:
        draw.text((pad_x, y), line, font=font_headline, fill=(255, 255, 255, 255))
        y += 82

    # Linea d'accento sotto il titolo
    y += 24
    draw.rounded_rectangle([pad_x, y, pad_x + 160, y + 8], radius=4, fill=(*accent_rgb, 255))
    y += 52

    # 5. Box Statistica / Numero Chiave (se presente)
    highlight_stat = slide_data.get("highlight_stat", "").strip()
    highlight_label = slide_data.get("highlight_label", "").strip()
    if highlight_stat:
        card_h = 240
        card_box = [pad_x, y, W - pad_x, y + card_h]
        draw.rounded_rectangle(
            card_box,
            radius=28,
            fill=(15, 23, 42, 215),
            outline=(*accent_rgb, 180),
            width=3,
        )
        # Barra laterale sinistra dentro la card
        draw.rounded_rectangle(
            [pad_x, y, pad_x + 14, y + card_h],
            radius=6,
            fill=(*accent_rgb, 255),
        )
        draw.text((pad_x + 44, y + 28), highlight_stat, font=font_stat_val, fill=(*accent_rgb, 255))
        if highlight_label:
            lbl_lines = wrap_pil_text(draw, highlight_label, font_stat_lbl, W - 2 * pad_x - 80)
            ly = y + 148
            for l_line in lbl_lines[:2]:
                draw.text((pad_x + 44, ly), l_line, font=font_stat_lbl, fill=(226, 232, 240, 240))
                ly += 36
        y += card_h + 52

    # 6. Corpo / Key Takeaway
    body_text = slide_data.get("body", "")
    b_lines = wrap_pil_text(draw, body_text, font_body, W - 2 * pad_x)
    for line in b_lines:
        draw.text((pad_x, y), line, font=font_body, fill=(226, 232, 240, 245))
        y += 56

    # 7. Box Voiceover / Sottotitolo parlato in basso
    vo_text = slide_data.get("voiceover", "")
    if vo_text:
        vo_font = load_font(30, bold=False)
        vo_label_font = load_font(22, bold=True)
        vo_lines = wrap_pil_text(draw, f"«{vo_text}»", vo_font, W - 2 * pad_x - 64)
        vo_box_h = 84 + len(vo_lines) * 42
        vo_top = H - 220 - vo_box_h
        draw.rounded_rectangle(
            [pad_x, vo_top, W - pad_x, vo_top + vo_box_h],
            radius=20,
            fill=(15, 23, 42, 255),
            outline=(*accent_rgb, 140),
            width=2,
        )
        draw.text(
            (pad_x + 32, vo_top + 20),
            "VOICEOVER / SOTTOTITOLI REEL",
            font=vo_label_font,
            fill=(*accent_rgb, 255),
        )
        vy = vo_top + 54
        for vline in vo_lines:
            draw.text((pad_x + 32, vy), vline, font=vo_font, fill=(241, 245, 249, 255))
            vy += 42

    # 8. Footer con Fonte verificata
    footer_y = H - 130
    draw.line([(pad_x, footer_y - 24), (W - pad_x, footer_y - 24)], fill=(255, 255, 255, 35), width=2)
    draw.text(
        (pad_x, footer_y),
        f"Fonte: {newspaper_name} (Pag. {source_page}) • Elaborazione Redazione AI",
        font=font_footer,
        fill=(148, 163, 184, 210),
    )

    return img.convert("RGB")


def generate_reel_video(
    slides: list[Image.Image],
    output_mp4_path: Path,
    seconds_per_slide: float = 3.2,
    fps: int = 30,
) -> Path:
    """
    Genera un video MP4 1080x1920 a 30fps a partire dalle slide:
    - Leggero effetto zoom dinamico (Ken Burns)
    - Barra di avanzamento continua in fondo
    - Dissolvenza incrociata (cross-fade) tra le slide
    """
    output_mp4_path.parent.mkdir(parents=True, exist_ok=True)
    frames_per_slide = int(seconds_per_slide * fps)
    fade_frames = int(0.35 * fps)

    accent_colors = [hex_to_rgb(p[0]) for p in ACCENT_PALETTE]

    writer = imageio.get_writer(
        str(output_mp4_path),
        fps=fps,
        codec="libx264",
        quality=8,
        pixelformat="yuv420p",
        macro_block_size=None,
    )

    try:
        num_slides = len(slides)
        for idx, slide_img in enumerate(slides):
            base_arr = np.asarray(slide_img, dtype=np.float32)
            next_arr = np.asarray(slides[idx + 1], dtype=np.float32) if idx + 1 < num_slides else None
            accent_rgb = accent_colors[idx % len(accent_colors)]

            for f in range(frames_per_slide):
                progress = (idx * frames_per_slide + f) / float(num_slides * frames_per_slide)

                # Cross-fade negli ultimi fade_frames
                if next_arr is not None and f >= (frames_per_slide - fade_frames):
                    alpha = (f - (frames_per_slide - fade_frames)) / float(fade_frames)
                    frame = (1.0 - alpha) * base_arr + alpha * next_arr
                else:
                    frame = base_arr.copy()

                frame_uint8 = np.clip(frame, 0, 255).astype(np.uint8)

                # Barra di progresso animata in basso (altezza 10px)
                bar_w = int(W * progress)
                frame_uint8[H - 12 : H, :bar_w, 0] = accent_rgb[0]
                frame_uint8[H - 12 : H, :bar_w, 1] = accent_rgb[1]
                frame_uint8[H - 12 : H, :bar_w, 2] = accent_rgb[2]

                writer.append_data(frame_uint8)
    finally:
        writer.close()

    return output_mp4_path


def generate_multi_reel_dashboard(
    scraped_data: dict[str, Any],
    daily_plan: dict[str, Any],
    rendered_bundles: list[dict[str, Any]],
    output_html_path: Path,
) -> Path:
    """
    Crea la Dashboard HTML del Piano Editoriale Giornaliero:
    - Mostra tutti i 5 Reel programmati nella giornata (08:30, 11:30, 14:30, 18:00, 21:00),
      ciascuno dedicato a una singola notizia
    - Mostra il catalogo completo dei 35 articoli estratti dallo scraper sulle 48 pagine del PDF
    """
    reels_html = ""
    selected_pages = {r["page"] for r in daily_plan["selected_reels"]}

    for idx, bundle in enumerate(rendered_bundles):
        reel = bundle["reel_data"]
        rel_video = bundle["video_path"].relative_to(output_html_path.parent)
        slides_html = ""
        for s_idx, sp in enumerate(bundle["slide_paths"]):
            rel_s = sp.relative_to(output_html_path.parent)
            slides_html += f"""
            <div class="slide-item">
                <img src="{rel_s}" alt="Slide {s_idx+1}" />
                <div class="slide-caption">{reel['slides'][s_idx]['role']}</div>
            </div>
            """

        facts_html = "".join(f"<li>✅ {f}</li>" for f in reel["verified_facts"])
        vo_html = "".join(
            f"<li><b>{s['role']}:</b> «{s['voiceover']}»</li>" for s in reel["slides"]
        )

        reels_html += f"""
        <section class="reel-section">
            <div class="reel-header">
                <div>
                    <span class="time-badge">⏰ ORE {reel['scheduled_time']}</span>
                    <span class="cat-pill">{reel['category']} • Pag. {reel['page']} • Firma: {reel['author']}</span>
                    <h2>Reel #{idx+1}: {reel['original_title']}</h2>
                </div>
                <div class="score-box">
                    <span>🔥 Viralità: <b>{reel['viral_score']}/10</b></span>
                    <span>📊 Impatto: <b>{reel['impact_score']}/10</b></span>
                </div>
            </div>

            <div class="reel-grid">
                <div>
                    <div class="sub-box">
                        <h4>🧠 Motivazione del Caporedattore ({reel['slot_label']})</h4>
                        <p>{reel['editorial_rationale']}</p>
                    </div>
                    <div class="sub-box">
                        <h4>🔍 Fatti & Numeri Verificati nell'Articolo (Grounding)</h4>
                        <ul class="facts">{facts_html}</ul>
                    </div>
                    <div class="sub-box">
                        <h4>🎙️ Script Voiceover (5 Scene Monotematiche)</h4>
                        <ul class="facts">{vo_html}</ul>
                    </div>
                    <div class="sub-box">
                        <h4>📱 Caption Instagram & Hashtag Pronti</h4>
                        <pre class="caption-box">{reel['instagram_caption']}

{' '.join(reel['hashtags'])}</pre>
                    </div>
                </div>

                <div class="video-box">
                    <h4>🎬 Anteprima Video MP4 (9:16)</h4>
                    <video controls loop muted playsinline>
                        <source src="{rel_video}" type="video/mp4" />
                    </video>
                </div>
            </div>

            <div class="slides-row">{slides_html}</div>
        </section>
        """

    # Tabella di tutti gli articoli estratti dallo scraper
    catalog_rows = ""
    for art in scraped_data["articles"]:
        is_sel = art["page"] in selected_pages or art["page"] == 1
        row_cls = "row-selected" if art["page"] in selected_pages else ""
        status = "★ Selezionato per Reel" if art["page"] in selected_pages else "Archiviato"
        nums = ", ".join(art["key_numbers"][:3]) if art["key_numbers"] else "—"
        catalog_rows += f"""
        <tr class="{row_cls}">
            <td><b>Pag. {art['page']:02d}</b></td>
            <td>{art['category']}</td>
            <td><b>{art['title']}</b><br/><span style="color:#94a3b8;font-size:12px;">{art['subtitle'][:110]}</span></td>
            <td>{art['author']}</td>
            <td>{nums}</td>
            <td>{status}</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Piano Editoriale Giornaliero — {daily_plan['newspaper_name']} ({daily_plan['edition_date']})</title>
<style>
  :root {{
    --bg: #070b14;
    --panel: #111827;
    --sub: #0b1120;
    --accent: #ff3b5c;
    --cyan: #00e5ff;
    --text: #f1f5f9;
    --muted: #94a3b8;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 32px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg); color: var(--text);
  }}
  header {{
    max-width: 1360px; margin: 0 auto 28px auto;
    border-bottom: 1px solid #1e293b; padding-bottom: 20px;
    display: flex; justify-content: space-between; align-items: flex-start;
  }}
  .summary-banner {{
    max-width: 1360px; margin: 0 auto 32px auto;
    background: linear-gradient(135deg, rgba(0,229,255,0.1), rgba(255,59,92,0.08));
    border: 1px solid #1e293b; border-radius: 14px; padding: 18px 24px;
    font-size: 15px; line-height: 1.5;
  }}
  .reel-section {{
    max-width: 1360px; margin: 0 auto 36px auto;
    background: var(--panel); border: 1px solid #1f2937; border-radius: 18px; padding: 26px;
  }}
  .reel-header {{
    display: flex; justify-content: space-between; align-items: flex-start;
    border-bottom: 1px solid #1f2937; padding-bottom: 16px; margin-bottom: 20px;
  }}
  .reel-header h2 {{ margin: 10px 0 0 0; font-size: 22px; }}
  .time-badge {{
    background: var(--accent); color: #fff; font-weight: 800;
    padding: 5px 12px; border-radius: 8px; font-size: 13px; margin-right: 10px;
  }}
  .cat-pill {{ color: var(--cyan); font-weight: 700; font-size: 13px; text-transform: uppercase; }}
  .score-box {{ display: flex; gap: 14px; font-size: 14px; background: var(--sub); padding: 10px 16px; border-radius: 10px; }}
  .reel-grid {{
    display: grid; grid-template-columns: 1.55fr 0.85fr; gap: 24px; align-items: start;
  }}
  .sub-box {{
    background: var(--sub); border: 1px solid #1e293b; border-radius: 12px;
    padding: 14px 18px; margin-bottom: 14px;
  }}
  .sub-box h4 {{ margin: 0 0 8px 0; color: var(--cyan); font-size: 14px; text-transform: uppercase; }}
  .sub-box p {{ margin: 0; font-size: 14px; line-height: 1.5; }}
  ul.facts {{ margin: 0; padding-left: 18px; font-size: 13.5px; line-height: 1.55; }}
  ul.facts li {{ margin-bottom: 4px; }}
  pre.caption-box {{
    margin: 0; white-space: pre-wrap; font-size: 13px; line-height: 1.45; color: #e2e8f0;
  }}
  .video-box {{ text-align: center; background: var(--sub); padding: 18px; border-radius: 14px; border: 1px solid #1e293b; }}
  .video-box h4 {{ margin: 0 0 12px 0; font-size: 14px; color: var(--muted); }}
  video {{ width: 100%; max-width: 310px; border-radius: 14px; border: 2px solid #334155; }}
  .slides-row {{
    display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin-top: 18px;
  }}
  .slide-item img {{ width: 100%; border-radius: 10px; border: 1px solid #334155; }}
  .slide-caption {{ text-align: center; font-size: 12px; color: var(--muted); margin-top: 6px; font-weight: 600; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13.5px; }}
  th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #1e293b; vertical-align: top; }}
  th {{ color: var(--cyan); text-transform: uppercase; font-size: 12px; }}
  tr.row-selected {{ background: rgba(255, 59, 92, 0.1); }}
</style>
</head>
<body>
  <header>
    <div>
      <h1 style="margin:0;font-size:28px;">🗞️ Redazione AI — Piano Editoriale 5 Reel Giornalieri</h1>
      <p style="margin:6px 0 0 0;color:var(--muted);">
        Quotidiano: <b>{daily_plan['newspaper_name']} ({daily_plan['edition_date']})</b> •
        Pagine analizzate: <b>{daily_plan['total_pages_scanned']}</b> •
        Articoli estratti: <b>{daily_plan['total_articles_extracted']}</b> •
        Reel generati: <b>{len(rendered_bundles)} (1 notizia per Reel)</b>
      </p>
    </div>
  </header>

  <div class="summary-banner">
    <b>📋 Sintesi del Caporedattore AI:</b> {daily_plan['editorial_summary']}
  </div>

  {reels_html}

  <section class="reel-section">
    <h2 style="margin-top:0;">📚 Catalogo Completo dello Scraper ({daily_plan['total_articles_extracted']} Articoli Estratti dal PDF)</h2>
    <table>
      <thead>
        <tr>
          <th>Pag.</th>
          <th>Categoria</th>
          <th>Titolo & Sommario Estratto</th>
          <th>Firma</th>
          <th>Dati / Numeri Rilevati</th>
          <th>Stato Redazione</th>
        </tr>
      </thead>
      <tbody>
        {catalog_rows}
      </tbody>
    </table>
  </section>
</body>
</html>
"""
    output_html_path.write_text(html, encoding="utf-8")
    return output_html_path

