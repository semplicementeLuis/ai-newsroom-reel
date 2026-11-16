# 🗞️ AI Newsroom → Instagram Reels (Stile Will Media)

Pipeline automatica che legge il PDF di un quotidiano, estrae e pulisce gli articoli, seleziona le 5 notizie più forti tramite una **Redazione AI**, genera una regia visiva adattiva per argomento e renderizza **5 Instagram Reel 9:16 (1080×1920)** con **Remotion**, completi di **voiceover italiano** e **sottotitoli sincronizzati parola per parola**.

## Architettura

1. **`scraper.py`** — Scraper layout-aware basato su `PyMuPDF` (`pymupdf`): rimuove le sillabazioni a capo, filtra le pagine pubblicitarie ed estrae titoli, sommari, firme, categorie e numeri chiave.
2. **`newsroom.py`** — Redazione AI (`gemini-4-hydrogen` via Google GenAI Interactions API con output JSON strutturato, più fallback dimostrativo locale): seleziona **5 notizie distinte** (1 notizia = 1 Reel) e pianifica gli slot orari della giornata (`08:30`, `11:30`, `14:30`, `18:00`, `21:00`).
3. **`art_director.py`** — Regista AI + Voiceover TTS (`edge-tts`): assegna a ogni Reel un tema grafico dedicato all'argomento (`tech_privacy`, `politics_ai`, `economy_data`, `world_breaking`, `culture_cinema`), sceglie il tipo di card/grafico per ogni scena e calcola la durata esatta in frame.
4. **`remotion-studio/`** — Motore video React/Remotion (`WillNewsReel.tsx` + `DynamicBackdrop.tsx`) che anima sfondi tematici, grafici a barre comparativi, schede alert UI e sottotitoli karaoke.
5. **`pipeline.py` & `renderer.py`** — Orchestrazione end-to-end e generazione della dashboard HTML `output/anteprima_redazione.html`.

## Installazione Rapida

```bash
# 1. Ambiente Python
uv venv
uv pip install -r requirements.txt

# 2. Dipendenze Remotion (Node.js)
cd remotion-studio && npm install && cd ..
```

## Utilizzo

Inserisci il PDF del quotidiano in `input/` (oppure specifica `--pdf`) ed esegui:

```bash
# Opzionale: abilita Gemini 4 Hydrogen live per qualsiasi quotidiano
export GEMINI_API_KEY="la_tua_api_key"

./.venv/bin/python pipeline.py --pdf "input/tuo_quotidiano.pdf"
```

Gli output vengono salvati in `output/reels/` (un MP4, le slide PNG e il JSON per ciascuno dei 5 Reel) insieme alla dashboard `output/anteprima_redazione.html`.
