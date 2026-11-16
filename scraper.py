"""
Scraper Layout-Aware per quotidiani in PDF (basato su PyMuPDF).
Scansiona tutte le pagine del quotidiano, filtra le pagine pubblicitarie,
ricostruisce titoli, occhielli, firme (autori), testo pulito (senza sillabazioni a capo)
e numeri chiave, producendo il catalogo completo degli articoli del giorno.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pymupdf


AD_KEYWORDS = [
    "overpost.biz",
    "www.alpecimbra.it",
    "messaggio promozionale",
    "pubblicità",
]


def clean_newspaper_text(raw: str) -> str:
    """
    Rimuove le sillabazioni di fine riga tipiche delle colonne di quotidiano
    (es. 'prote-\\nzione' -> 'protezione') e ricongiunge i capilettera (es. 'I\\nl Garante' -> 'Il Garante').
    """
    # Ricongiunge sillabazioni con trattino a fine riga
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", raw)
    # Ricongiunge capilettera isolati su riga singola all'inizio (es. "I\nl " o "P\nutin")
    text = re.sub(r"(?:^|\n)([A-ZÈÉÀÒÙÌ])\n([a-zàèéìòù])", r"\n\1\2", text)
    # Normalizza spazi multipli preservando i paragrafi
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    lines = [l for l in lines if l and not re.fullmatch(r"[\d\W]+", l)]
    return "\n".join(lines)


def extract_author(text: str) -> str:
    """Estrae la firma dell'articolo (es. 'di GIULIA BOERO' o 'dal nostro corrispondente PAOLO MASTROLILLI')."""
    m = re.search(
        r"(?:di|dal nostro corrispondente|dal nostro inviato)\s+([A-ZÀÈÉÌÒÙ][A-Za-zÀ-ÿ'\s]{3,35})",
        text,
    )
    if m:
        author = m.group(1).strip().splitlines()[0].strip()
        return author.title()
    return "Redazione"


def extract_numbers_and_stats(text: str) -> list[str]:
    """Individua cifre, percentuali, importi in euro/dollari e quantità significative nel testo."""
    patterns = [
        r"\b\d+(?:[.,]\d+)?\s*(?:miliardi|milioni|mila|%)\b(?:\s+di\s+[a-zA-Zàèéìòù]+)?",
        r"\b\d+(?:[.,]\d+)?\s*(?:euro|dollari|yuan|anni|giorni|ore)\b",
    ]
    found: list[str] = []
    for pat in patterns:
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            val = re.sub(r"\s+", " ", m.group(0)).strip()
            if val not in found:
                found.append(val)
    return found[:8]


def guess_category(page_num: int, text_lower: str) -> str:
    if page_num in (2, 3, 14, 15, 16, 17):
        return "Esteri & Mondo"
    if any(k in text_lower for k in ("garante", "privacy", "hacker", "intelligenza artificiale", "bot", "openai", "meta")):
        return "Tecnologia & Digitale"
    if any(k in text_lower for k in ("manovra", "irpef", "superbonus", "confindustria", "stipendi", "fabbrica", "volkswagen")):
        return "Economia & Lavoro"
    if any(k in text_lower for k in ("cinema", "film", "arte", "crusca", "lingua", "archeologica", "libri")):
        return "Cultura & Spettacolo"
    if any(k in text_lower for k in ("sinner", "mancini", "belgio", "coni", "calcio", "sport")):
        return "Sport"
    if page_num <= 11 or any(k in text_lower for k in ("governo", "meloni", "schlein", "conte", "parlamento")):
        return "Politica"
    return "Cronaca & Società"


def scrape_newspaper_pdf(pdf_path: str | Path) -> dict[str, Any]:
    """
    Analizza l'intero PDF del quotidiano pagina per pagina e restituisce i metadati
    della testata e la lista strutturata di tutti gli articoli rilevati.
    """
    pdf_path = Path(pdf_path)
    doc = pymupdf.open(str(pdf_path))
    total_pages = len(doc)

    # Deduce nome testata e data dal nome file o dalla prima pagina
    stem = pdf_path.stem
    newspaper_name = "La Repubblica" if "repubblica" in stem.lower() else stem
    date_match = re.search(r"(\d{1,2}\s+[A-Za-zÀ-ÿ]+\s+\d{4})", stem)
    edition_date = date_match.group(1) if date_match else "Edizione Odierna"

    articles: list[dict[str, Any]] = []

    for pno in range(total_pages):
        page_number = pno + 1
        page = doc[pno]
        raw_page_text = page.get_text("text")

        # Salta pagine quasi vuote o puramente pubblicitarie
        if len(raw_page_text.strip()) < 600:
            continue
        lower_raw = raw_page_text.lower()
        if any(ad in lower_raw for ad in AD_KEYWORDS) and len(raw_page_text.strip()) < 3500:
            continue

        blocks = page.get_text("dict").get("blocks", [])
        headline_parts: list[tuple[float, float, str]] = []  # (y0, size, text)
        subtitle_parts: list[str] = []
        body_parts: list[str] = []

        for b in blocks:
            if b.get("type") != 0:
                continue
            for line in b.get("lines", []):
                y0 = line["bbox"][1]
                for span in line.get("spans", []):
                    t = span.get("text", "").strip()
                    sz = float(span.get("size", 0))
                    if not t:
                        continue
                    if sz >= 23.5 and len(t) > 2:
                        # Evita testate di sezione corte o numeri isolati
                        if t.upper() not in ("MONDO", "CRONACA", "POLITICA", "ECONOMIA", "CULTURA", "SPORT", "COMMENTI"):
                            headline_parts.append((y0, sz, t))
                    elif 14.0 <= sz < 23.5 and len(t) > 10:
                        subtitle_parts.append(t)
                    elif 8.0 <= sz < 14.0:
                        body_parts.append(t)

        cleaned_full_text = clean_newspaper_text(raw_page_text)
        if len(cleaned_full_text) < 800:
            continue

        # Ricostruzione titolo principale della pagina
        if headline_parts:
            # Raggruppa gli span con il font più grande sulla pagina
            max_sz = max(h[1] for h in headline_parts)
            main_h = [h[2] for h in headline_parts if abs(h[1] - max_sz) <= 4.5]
            title = " ".join(main_h[:5]).strip()
        else:
            first_lines = [l for l in cleaned_full_text.splitlines() if len(l) > 20]
            title = first_lines[0][:100] if first_lines else f"Articolo Pagina {page_number}"

        title = re.sub(r"\s+", " ", title).strip()
        if len(title) < 8:
            continue

        subtitle = " ".join(subtitle_parts[:4]).strip()
        subtitle = re.sub(r"\s+", " ", subtitle)[:260]

        author = extract_author(raw_page_text)
        stats = extract_numbers_and_stats(cleaned_full_text)
        category = guess_category(page_number, lower_raw)

        # Calcolo di uno score preliminare di "interesse social / notiziabilità"
        interest_score = 5.0
        if len(stats) >= 2:
            interest_score += 1.5
        if category in ("Tecnologia & Digitale", "Economia & Lavoro", "Esteri & Mondo"):
            interest_score += 1.5
        if len(cleaned_full_text) > 3500:
            interest_score += 1.0
        interest_score = min(10.0, round(interest_score, 1))

        articles.append(
            {
                "id": f"pag_{page_number:02d}",
                "page": page_number,
                "category": category,
                "author": author,
                "title": title,
                "subtitle": subtitle,
                "key_numbers": stats,
                "char_count": len(cleaned_full_text),
                "interest_score": interest_score,
                "excerpt": cleaned_full_text[:1400],
                "full_text": cleaned_full_text,
            }
        )

    doc.close()
    return {
        "newspaper_name": newspaper_name,
        "edition_date": edition_date,
        "source_pdf": str(pdf_path.name),
        "total_pages_scanned": total_pages,
        "total_articles_extracted": len(articles),
        "articles": articles,
    }


if __name__ == "__main__":
    import json

    pdf_file = Path(__file__).parent / "input" / "La Repubblica 15 Novembre 2026.pdf"
    res = scrape_newspaper_pdf(pdf_file)
    print(
        f"Testata: {res['newspaper_name']} ({res['edition_date']}) — "
        f"Pagine: {res['total_pages_scanned']} — Articoli estratti: {res['total_articles_extracted']}"
    )
    for art in res["articles"][:10]:
        print(f" - [Pag. {art['page']:02d} | {art['category']}] {art['title']} (Numeri: {art['key_numbers'][:3]})")
