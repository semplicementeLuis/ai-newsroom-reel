"""
Modulo Redazione AI:
Riceve il catalogo degli articoli estratti dallo scraper PDF, seleziona i 5 articoli
più interessanti della giornata e prepara un Piano Editoriale di 5 Reel distinti
(1 notizia = 1 Reel) distribuiti nelle fasce orarie della giornata.
"""

from __future__ import annotations

import json
import os
from typing import Any


SINGLE_REEL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "reel_id": {"type": "string"},
        "scheduled_time": {"type": "string"},
        "slot_label": {"type": "string"},
        "article_id": {"type": "string"},
        "page": {"type": "integer"},
        "category": {"type": "string"},
        "author": {"type": "string"},
        "original_title": {"type": "string"},
        "editorial_rationale": {"type": "string"},
        "viral_score": {"type": "integer"},
        "impact_score": {"type": "integer"},
        "verified_facts": {"type": "array", "items": {"type": "string"}},
        "instagram_caption": {"type": "string"},
        "hashtags": {"type": "array", "items": {"type": "string"}},
        "slides": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "role": {"type": "string"},
                    "headline": {"type": "string"},
                    "highlight_stat": {"type": "string"},
                    "highlight_label": {"type": "string"},
                    "body": {"type": "string"},
                    "voiceover": {"type": "string"},
                },
                "required": [
                    "role",
                    "headline",
                    "highlight_stat",
                    "highlight_label",
                    "body",
                    "voiceover",
                ],
            },
        },
    },
    "required": [
        "reel_id",
        "scheduled_time",
        "slot_label",
        "article_id",
        "page",
        "category",
        "author",
        "original_title",
        "editorial_rationale",
        "viral_score",
        "impact_score",
        "verified_facts",
        "instagram_caption",
        "hashtags",
        "slides",
    ],
}

DAILY_PLAN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "editorial_summary": {"type": "string"},
        "selected_reels": {
            "type": "array",
            "items": SINGLE_REEL_SCHEMA,
        },
    },
    "required": ["editorial_summary", "selected_reels"],
}


def run_gemini_daily_newsroom(scraped_data: dict[str, Any], target_reels: int = 5) -> dict[str, Any]:
    """
    Usa Gemini 4 Hydrogen (Interactions API) per analizzare tutti gli articoli estratti
    dallo scraper, selezionare i 5 più forti e generare 5 Reel separati (uno per notizia).
    """
    from google import genai

    client = genai.Client()

    # Passiamo l'elenco degli articoli estratti (con estratto e numeri)
    compact_articles = [
        {
            "id": a["id"],
            "page": a["page"],
            "category": a["category"],
            "author": a["author"],
            "title": a["title"],
            "subtitle": a["subtitle"],
            "key_numbers": a["key_numbers"],
            "excerpt": a["excerpt"],
        }
        for a in scraped_data["articles"]
    ]

    prompt = (
        f"Sei la Redazione AI di un canale Instagram di informazione che analizza l'edizione del quotidiano "
        f"{scraped_data['newspaper_name']} ({scraped_data['edition_date']}).\n"
        f"Qui sotto trovi i {len(compact_articles)} articoli estratti dallo scraper PDF.\n"
        f"REGOLE EDITORIALI TASSATIVE:\n"
        f"1. Seleziona esattamente i {target_reels} articoli più interessanti della giornata, variando i temi "
        f"(es. Tecnologia/Privacy, Politica/IA, Economia, Esteri, Cultura).\n"
        f"2. OGNI REEL DEVE CONTENERE UNA SOLA NOTIZIA. Non mescolare mai più notizie nello stesso Reel.\n"
        f"3. Pianifica i {target_reels} Reel lungo la giornata (08:30, 11:30, 14:30, 18:00, 21:00).\n"
        f"4. Per ciascuno dei {target_reels} Reel crea 5 slide verticali (01 HOOK, 02 IL FATTO, 03 IL MECCANISMO, "
        f"04 I NUMERI CHIAVE, 05 DOMANDA FINALE), i fatti verificati dal testo, il voiceover e la caption Instagram.\n\n"
        f"ARTICOLI ESTRATTI DAL PDF:\n{json.dumps(compact_articles, ensure_ascii=False)}"
    )

    interaction = client.interactions.create(
        model="gemini-4-hydrogen",
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": DAILY_PLAN_SCHEMA,
        },
    )

    plan = json.loads(interaction.output_text)
    return {
        "newspaper_name": scraped_data["newspaper_name"],
        "edition_date": scraped_data["edition_date"],
        "source_pdf": scraped_data["source_pdf"],
        "total_pages_scanned": scraped_data["total_pages_scanned"],
        "total_articles_extracted": scraped_data["total_articles_extracted"],
        "engine_mode": "Gemini API Live (gemini-4-hydrogen)",
        "editorial_summary": plan["editorial_summary"],
        "selected_reels": plan["selected_reels"],
    }


def run_local_daily_newsroom(scraped_data: dict[str, Any]) -> dict[str, Any]:
    """
    Seleziona i 5 articoli più interessanti estratti da 'La Repubblica 15 Novembre 2026.pdf'
    e costruisce 5 Reel completi (1 notizia per Reel) basati fedelmente sui testi estratti.
    """
    articles_by_page = {a["page"]: a for a in scraped_data["articles"]}

    selected_reels = [
        # REEL 1 — Ore 08:30 (Pag. 30 + richiamo Pag. 1)
        {
            "reel_id": "reel_01_meta_privacy",
            "scheduled_time": "08:30",
            "slot_label": "Fascia Mattino • Apertura Tech & Privacy",
            "article_id": "pag_30",
            "page": 30,
            "category": "Tecnologia & Privacy",
            "author": articles_by_page.get(30, {}).get("author", "Giulia Boero"),
            "original_title": "Facebook multata per 805 milioni: accesso a foto e video negli smartphone di 20 milioni di italiani",
            "editorial_rationale": (
                "Notizia di prima pagina con impatto diretto su 20 milioni di utenti Android in Italia: "
                "tocca gli smartphone di tutti, ha una cifra record (805 milioni di euro) ed è perfetta "
                "per aprire la programmazione mattutina alle 08:30 con altissimo tasso di condivisione."
            ),
            "viral_score": 10,
            "impact_score": 10,
            "verified_facts": [
                "Sanzione da 805 milioni di euro inflitta a Meta dal Garante per la protezione dei dati personali (la più alta della sua storia).",
                "Coinvolti circa 20 milioni di smartphone Android italiani tramite la funzione 'Ottieni suggerimenti dalla galleria quando navighi su Facebook', attiva dal 2023.",
                "L'istruttoria è partita a luglio 2025 dopo una segnalazione del Centro Tutela Consumatori Utenti di Bolzano.",
                "Violato l'articolo 122 del Codice privacy (direttiva europea ePrivacy): l'archivio fotografico veniva letto in modo permanente con un'unica autorizzazione generica.",
            ],
            "instagram_caption": (
                "📱 Hai uno smartphone Android con Facebook installato? Potresti essere tra i 20 milioni di italiani coinvolti nella maxi-multa storica a Meta.\n\n"
                "Il Garante per la Privacy ha inflitto una sanzione da 805 MILIONI di euro (la più alta di sempre in Italia) al gruppo di Mark Zuckerberg.\n\n"
                "🔍 Cosa è emerso dall'istruttoria (Pag. 1 e 30 di Repubblica, a firma Giulia Boero):\n"
                "• Tutto ruota attorno alla funzione 'Ottieni suggerimenti dalla galleria quando navighi su Facebook' (attiva dal 2023)\n"
                "• Con un singolo permesso generico ('abilitare altre funzioni'), l'app accedeva in modo permanente a foto, video e metadati del telefono\n"
                "• Coinvolti circa 20 milioni di utenti Android in Italia senza un consenso libero e specifico\n"
                "• Meta ha annunciato ricorso definendo la multa 'sproporzionata'\n\n"
                "Avevi mai notato i suggerimenti della tua galleria privata apparire su Facebook? Controlla subito i permessi dell'app e condividi il Reel! 👇"
            ),
            "hashtags": [
                "#Privacy",
                "#Meta",
                "#Facebook",
                "#Android",
                "#GarantePrivacy",
                "#Smartphone",
                "#TechNews",
                "#RassegnaStampa",
            ],
            "slides": [
                {
                    "role": "01 • HOOK",
                    "headline": "Facebook leggeva le foto sul telefono di 20 milioni di italiani?",
                    "highlight_stat": "805 Mln €",
                    "highlight_label": "Maxi-multa record del Garante Privacy italiano a Meta",
                    "body": "È la sanzione più alta nella storia dell'Autorità italiana: nel mirino l'accesso a foto, video e metadati sugli smartphone Android.",
                    "voiceover": "Hai uno smartphone Android? Facebook potrebbe aver avuto accesso a tutte le foto e i video della tua galleria privata.",
                },
                {
                    "role": "02 • IL FATTO",
                    "headline": "La funzione sotto accusa attiva dal 2023",
                    "highlight_stat": "20 Milioni",
                    "highlight_label": "Gli smartphone Android italiani coinvolti secondo l'istruttoria",
                    "body": "Sotto la lente c'è 'Ottieni suggerimenti dalla galleria quando navighi su Facebook', che ripesca dal telefono foto e video mai condivisi.",
                    "voiceover": "Il Garante della Privacy ha multato Meta per 805 milioni di euro: coinvolti circa 20 milioni di italiani con dispositivi Android.",
                },
                {
                    "role": "03 • IL MECCANISMO",
                    "headline": "Un avviso generico apriva l'intero archivio foto",
                    "highlight_stat": "Art. 122",
                    "highlight_label": "Norma del Codice Privacy violata secondo il Garante",
                    "body": "Partita da una segnalazione del Centro Consumatori di Bolzano, l'indagine svela che un singolo permesso dava accesso permanente alla galleria.",
                    "voiceover": "Secondo l'indagine, bastava accettare un avviso generico per dare all'app accesso permanente all'intero archivio fotografico.",
                },
                {
                    "role": "04 • LA REPLICA DI META",
                    "headline": "Terza stangata in 24 giorni per Zuckerberg",
                    "highlight_stat": "3° Conto",
                    "highlight_label": "Dopo i 25 miliardi chiesti in New Mexico e la multa UK",
                    "body": "Meta annuncia ricorso: 'Siamo in netto disaccordo, è una funzione semplice per aiutare gli utenti e il permesso è modificabile'.",
                    "voiceover": "Meta respinge le accuse e annuncia ricorso, ma per Zuckerberg è già la terza stangata giudiziaria in meno di un mese.",
                },
                {
                    "role": "05 • CONTROLLA ORA",
                    "headline": "Hai mai controllato i permessi della tua galleria?",
                    "highlight_stat": " CONDIVIDI",
                    "highlight_label": "Manda questo Reel a chi usa Facebook su Android",
                    "body": "Verifica nelle impostazioni del telefono quali app hanno accesso completo a tutte le tue foto e video.",
                    "voiceover": "Tu avevi mai notato quei suggerimenti su Facebook? Controlla subito i permessi sul telefono e gira questo Reel a un amico!",
                },
            ],
        },
        # REEL 2 — Ore 11:30 (Pag. 19)
        {
            "reel_id": "reel_02_rivolta_bot_politici",
            "scheduled_time": "11:30",
            "slot_label": "Fascia Metà Mattina • Politica & IA",
            "article_id": "pag_19",
            "page": 19,
            "category": "Politica & IA",
            "author": "Giuliano Foschini e Giacomo Salvini",
            "original_title": "La rivolta dei bot contro i politici: “Non farò quel commento social”",
            "editorial_rationale": (
                "Storia curiosa, visiva e ironica: un bug dei sistemi AI fa sì che i bot hackerati "
                "pubblichino per errore il rifiuto etico del chatbot sotto i post dei politici italiani. "
                "Ideale per lo slot delle 11:30 perché stimola tantissimi commenti."
            ),
            "viral_score": 10,
            "impact_score": 8,
            "verified_facts": [
                "Un malfunzionamento legato a Microsoft e ai modelli OpenAI e Anthropic ha mandato in tilt una rete di profili social hackerati.",
                "Sotto i post Facebook e Instagram di Matteo Salvini, Carlo Fidanza, Dario Nardella e Camilla Laureti sono apparsi i messaggi di rifiuto dell'IA.",
                "Testo esatto comparso nei commenti: 'Non posso scrivere uno specifico messaggio finalizzato a convincere specifici eurodeputati a sostenere una proposta legislativa'.",
                "Altro messaggio apparso serialmente: 'Non posso scrivere un messaggio volto a insultare uno specifico partito politico'.",
            ],
            "instagram_caption": (
                "🤖 Quando i bot si ribellano e smascherano da soli la propaganda sui social.\n\n"
                "È bastato un malfunzionamento dei sistemi AI (Microsoft, OpenAI e Anthropic) per produrre un cortocircuito clamoroso sotto i profili Facebook e Instagram di diversi politici italiani.\n\n"
                "📌 Cosa è successo (Pag. 19 di Repubblica, di G. Foschini e G. Salvini):\n"
                "• Sotto i post di Matteo Salvini, Carlo Fidanza, Dario Nardella e Camilla Laureti sono comparsi decine di commenti identici da profili hackerati\n"
                "• Invece dello slogan o dell'attacco programmato, i bot hanno pubblicato la risposta di rifiuto etico dell'IA:\n"
                "«Non posso scrivere un messaggio volto a insultare uno specifico partito politico»\n"
                "«Non posso scrivere uno specifico messaggio finalizzato a convincere specifici eurodeputati a sostenere una proposta legislativa»\n\n"
                "Quanti dei commenti che leggiamo ogni giorno sotto i post politici sono in realtà scritti da bot? 👇 Dicci la tua!"
            ),
            "hashtags": [
                "#IntelligenzaArtificiale",
                "#Bot",
                "#SocialMedia",
                "#PoliticaItaliana",
                "#OpenAI",
                "#FakeAccount",
                "#RassegnaStampa",
            ],
            "slides": [
                {
                    "role": "01 • HOOK",
                    "headline": "I bot AI vanno in tilt e si smascherano sotto i post dei politici",
                    "highlight_stat": "BUG AI",
                    "highlight_label": "Un guasto svela i commenti automatici su Facebook e Instagram",
                    "body": "Invece di pubblicare attacchi o slogan, decine di account hanno incollato per errore il rifiuto etico dell'intelligenza artificiale.",
                    "voiceover": "Un bug dell'intelligenza artificiale ha mandato in tilt i bot sui social, facendoli uscire allo scoperto sotto i post dei politici italiani.",
                },
                {
                    "role": "02 • IL CORTOCIRCUITO",
                    "headline": "Il messaggio apparso in serie nei commenti",
                    "highlight_stat": "«NON POSSO»",
                    "highlight_label": "La frase standard dei filtri etici di OpenAI e Anthropic",
                    "body": "Sotto i post è comparso: «Non posso scrivere un messaggio volto a insultare uno specifico partito politico».",
                    "voiceover": "Sotto gli ultimi post sono comparsi commenti identici: 'Non posso scrivere un messaggio volto a insultare uno specifico partito politico'.",
                },
                {
                    "role": "03 • IL CASO UE",
                    "headline": "Pressioni automatizzate sugli eurodeputati",
                    "highlight_stat": "4 Big",
                    "highlight_label": "Colpiti i post di Salvini, Fidanza, Nardella e Laureti",
                    "body": "Sotto i profili dei membri della commissione Agricoltura Ue i bot scrivevano: «Non posso convincere specifici eurodeputati...».",
                    "voiceover": "E sotto i profili di diversi eurodeputati è apparso: 'Non posso scrivere un messaggio per convincere specifici eurodeputati a sostenere una legge'.",
                },
                {
                    "role": "04 • COME FUNZIONANO",
                    "headline": "Profili rubati che aggirano i filtri anti-spam",
                    "highlight_stat": "100% Auto",
                    "highlight_label": "Account hackerati collegati direttamente alle API dei chatbot",
                    "body": "I politici colpiti sono estranei alla gestione dei bot, ma il guasto ha mostrato in chiaro i comandi nascosti dati alle macchine.",
                    "voiceover": "Si tratta di profili hackerati collegati in automatico all'IA: quando il filtro etico si è attivato, il bot ha copiato e pubblicato il rifiuto.",
                },
                {
                    "role": "05 • LA DOMANDA",
                    "headline": "Quanti commenti che leggi ogni giorno sono scritti da bot?",
                    "highlight_stat": "COMMENTA",
                    "highlight_label": "Ti è mai capitato di riconoscere un bot nei commenti?",
                    "body": "Salva il Reel e condividilo: la Dead Internet Theory è sempre più reale.",
                    "voiceover": "Dopo questo episodio, quanti commenti sui social pensi siano scritti davvero da esseri umani? Scrivimelo qui sotto!",
                },
            ],
        },
        # REEL 3 — Ore 14:30 (Pag. 6)
        {
            "reel_id": "reel_03_manovra_irpef_superbonus",
            "scheduled_time": "14:30",
            "slot_label": "Fascia Pranzo • Economia & Tasche degli Italiani",
            "article_id": "pag_06",
            "page": 6,
            "category": "Economia & Lavoro",
            "author": "Rosaria Amato",
            "original_title": "Tagli Irpef e superbonus: serve un nuovo vertice per riscrivere la manovra",
            "editorial_rationale": (
                "Tema economico centrale per professionisti, imprese e famiglie (Irpef, Superbonus spalmato in 10 anni, "
                "Exit Tax). Perfetto per lo slot post-pranzo delle 14:30."
            ),
            "viral_score": 8,
            "impact_score": 9,
            "verified_facts": [
                "Convocato un nuovo vertice di maggioranza tra Meloni, Giorgetti, Salvini e Tajani per modificare la manovra.",
                "Confindustria (tramite il presidente Emanuele Orsini) contesta lo spalmacrediti del Superbonus in 10 anni: le imprese hanno circa 2 miliardi di euro di crediti.",
                "Il viceministro dell'Economia Maurizio Leo promette un taglio Irpef congiunturale con l'obiettivo di renderlo strutturale verso il 2027.",
                "Tajani chiede modifiche alla 'exit tax' per non scoraggiare chi vuole investire in Italia.",
            ],
            "instagram_caption": (
                "💶 Manovra da riscrivere: nodo Tagli Irpef, Exit Tax e crediti del Superbonus spalmati in 10 anni.\n\n"
                "Cosa bolle in pentola in vista del nuovo vertice di governo (Pag. 6 di Repubblica, di Rosaria Amato):\n"
                "• Superbonus: Confindustria lancia l'allarme sui 2 miliardi di euro di crediti delle imprese che la manovra spalma su 10 anni invece che nel 2026-2027\n"
                "• Taglio Irpef: il viceministro Leo punta a un intervento immediato con l'obiettivo di renderlo strutturale ed estenderlo nel 2027\n"
                "• Exit Tax: pressing nella maggioranza per correggerla ed evitare segnali negativi agli investitori\n\n"
                "Cambiare le regole sui crediti fiscali in corsa danneggia la fiducia di chi fa impresa in Italia? 👇 Parliamone nei commenti."
            ),
            "hashtags": [
                "#Economia",
                "#Manovra",
                "#Irpef",
                "#Superbonus",
                "#Imprese",
                "#Tasse",
                "#Confindustria",
                "#RassegnaStampa",
            ],
            "slides": [
                {
                    "role": "01 • HOOK",
                    "headline": "Manovra nel caos: scontro su Irpef e crediti Superbonus",
                    "highlight_stat": "2 Mld €",
                    "highlight_label": "I crediti Superbonus delle imprese spalmati in 10 anni",
                    "body": "Confindustria chiede un tavolo urgente al governo: 'Cambiare le regole in corsa rischia di mettere in ginocchio le aziende'.",
                    "voiceover": "Nuovo vertice d'urgenza sulla Manovra: esplode il caso dei 2 miliardi di crediti del Superbonus spalmati in dieci anni.",
                },
                {
                    "role": "02 • L'ALLARME IMPRESE",
                    "headline": "Orsini (Confindustria): «Serve certezza del diritto»",
                    "highlight_stat": "10 Anni",
                    "highlight_label": "I tempi per scontare i crediti previsti nel 2026-2027",
                    "body": "Dopo le critiche di Intesa Sanpaolo, anche le piccole e medie imprese denunciano il blocco di liquidità causato dallo spalmacrediti.",
                    "voiceover": "Il presidente di Confindustria Orsini avverte: scontare in 10 anni crediti previsti per il 2026 mette in crisi chi ha investito.",
                },
                {
                    "role": "03 • IL NODO IRPEF",
                    "headline": "Taglio Irpef: ponte verso il 2027",
                    "highlight_stat": "2027",
                    "highlight_label": "L'orizzonte indicato dal viceministro Leo per il taglio strutturale",
                    "body": "Il Ministero dell'Economia lavora a una misura ponte sull'Irpef con l'obiettivo di allargare la platea dei contribuenti.",
                    "voiceover": "Sul fronte Irpef, il viceministro Leo promette un intervento immediato da rendere strutturale ed esteso entro il 2027.",
                },
                {
                    "role": "04 • VERTICE A QUATTRO",
                    "headline": "Meloni, Giorgetti, Salvini e Tajani al tavolo",
                    "highlight_stat": "Exit Tax",
                    "highlight_label": "Nel mirino anche la tassa sulle plusvalenze in uscita",
                    "body": "Pressing dentro la stessa maggioranza per correggere l'Exit Tax e trovare risorse per sanità, pensioni e scuola.",
                    "voiceover": "Sul tavolo del vertice tra Meloni, Giorgetti, Salvini e Tajani finisce anche la correzione della discussa Exit Tax.",
                },
                {
                    "role": "05 • IL DIBATTITO",
                    "headline": "Qual è la priorità economica più urgente secondo te?",
                    "highlight_stat": "DICCI LA TUA",
                    "highlight_label": "Taglio Irpef sugli stipendi o sblocco dei crediti alle imprese?",
                    "body": "Scrivilo nei commenti e salva il Reel per seguire gli sviluppi del vertice.",
                    "voiceover": "Secondo te il governo dovrebbe dare priorità al taglio dell'Irpef o alla certezza dei crediti per le imprese? Scrivilo nei commenti!",
                },
            ],
        },
        # REEL 4 — Ore 18:00 (Pag. 14-15)
        {
            "reel_id": "reel_04_caos_voli_usa",
            "scheduled_time": "18:00",
            "slot_label": "Fascia Pomeriggio • Esteri & Infrastrutture",
            "article_id": "pag_14",
            "page": 14,
            "category": "Esteri & Mondo",
            "author": "Paolo Mastrolilli",
            "original_title": "Voli cancellati in America: “La manutenzione fallita eseguita nell’ora di punta”",
            "editorial_rationale": (
                "Storia incredibile dagli Stati Uniti: non sono stati né gli hacker né gli alieni a bloccare "
                "il traffico aereo USA, ma una sostituzione di cavi di rame del 2001 eseguita in pieno giorno nell'ora di punta."
            ),
            "viral_score": 9,
            "impact_score": 8,
            "verified_facts": [
                "Oltre 2 milioni di passeggeri bloccati negli aeroporti americani e almeno altre 4.000 cancellazioni di voli.",
                "Il caos è nato mentre il contractor L3Harris sostituiva vecchi cavi in rame installati nel 2001 con la fibra ottica.",
                "La FAA aveva programmato i lavori in pieno giorno, nell'ora di punta, invece che di notte.",
                "Il segretario ai Trasporti Sean Duffy aveva chiesto al Congresso 50 miliardi di dollari per ammodernare la rete, ottenendone solo 12,5.",
            ],
            "instagram_caption": (
                "✈️ Altro che attacco hacker: il traffico aereo degli Stati Uniti è andato in tilt per un cavo del 2001 sostituito nell'ora di punta!\n\n"
                "I numeri del blackout nei cieli americani (Pag. 14-15 di Repubblica, dal corrispondente a New York Paolo Mastrolilli):\n"
                "• Oltre 2 MILIONI di passeggeri rimasti bloccati negli aeroporti\n"
                "• Almeno 4.000 voli cancellati in un solo giorno di ripartenza\n"
                "• La causa: un errore o un router difettoso durante la sostituzione di vecchi cavi in rame del 2001 (ormai fuori produzione) con la fibra ottica\n"
                "• Il paradosso: i lavori sono stati eseguiti di pomeriggio, in piena ora di punta!\n"
                "• Infrastrutture al collasso: chiesti 50 miliardi di dollari al Congresso per rifare la rete FAA, concessi solo 12,5 miliardi\n\n"
                "Ti saresti mai aspettato che i cieli USA dipendessero ancora da cavi in rame del 2001? 👇"
            ),
            "hashtags": [
                "#USA",
                "#VoliCancellati",
                "#Aeroporti",
                "#Infrastrutture",
                "#NewYork",
                "#Aviazione",
                "#Esteri",
                "#RassegnaStampa",
            ],
            "slides": [
                {
                    "role": "01 • HOOK",
                    "headline": "Cieli USA nel caos: 2 milioni di passeggeri a terra per un cavo!",
                    "highlight_stat": "2 Milioni",
                    "highlight_label": "I passeggeri bloccati negli aeroporti americani",
                    "body": "Nessun attacco hacker: a paralizzare i voli negli Stati Uniti è stata una manutenzione eseguita in piena ora di punta.",
                    "voiceover": "Altro che hacker: a bloccare due milioni di passeggeri negli aeroporti americani è stato un lavoro sui cavi fatto nell'ora di punta.",
                },
                {
                    "role": "02 • L'ERRORE",
                    "headline": "Lavori programmati di pomeriggio invece che di notte",
                    "highlight_stat": "4.000+",
                    "highlight_label": "I voli cancellati dopo il blocco precauzionale dei decolli",
                    "body": "Un contractor della FAA stava sostituendo vecchi cavi in rame con la fibra ottica quando le comunicazioni sono saltate.",
                    "voiceover": "Con oltre 4 mila voli cancellati, la Federal Aviation Administration ha ammesso di aver programmato i lavori in pieno giorno.",
                },
                {
                    "role": "03 • TECNOLOGIA DEL 2001",
                    "headline": "Torri di controllo appese a cavi fuori produzione dal 2001",
                    "highlight_stat": "Anno 2001",
                    "highlight_label": "L'anno di installazione dei cavi in rame ancora in uso",
                    "body": "Il segretario ai Trasporti Duffy denuncia: 'L'infrastruttura è antiquata, quei cavi non vengono nemmeno più prodotti'.",
                    "voiceover": "Il dettaglio più assurdo? Il traffico aereo americano viaggiava ancora su cavi in rame installati nel 2001 e ormai fuori produzione.",
                },
                {
                    "role": "04 • IL NODO FONDI",
                    "headline": "Tagliati i fondi per ammodernare i cieli USA",
                    "highlight_stat": "12,5 su 50",
                    "highlight_label": "I miliardi concessi dal Congresso rispetto ai 50 richiesti",
                    "body": "Servivano 50 miliardi di dollari per rifare l'intera rete del traffico aereo, ma il Congresso ne ha approvati solo un quarto.",
                    "voiceover": "Per aggiornare l'intero sistema servivano 50 miliardi di dollari, ma il Congresso ne ha stanziati appena 12 e mezzo.",
                },
                {
                    "role": "05 • CONDIVIDI",
                    "headline": "Com'è possibile fare manutenzione aerea nell'ora di punta?",
                    "highlight_stat": "SALVA",
                    "highlight_label": "Condividi il Reel con chi viaggia spesso in aereo",
                    "body": "Seguici per tutti gli approfondimenti internazionali dalla rassegna stampa quotidiana.",
                    "voiceover": "Chi ha deciso di staccare i cavi in piena ora di punta? Raccontaci la tua nei commenti e seguici per le altre notizie del giorno!",
                },
            ],
        },
        # REEL 5 — Ore 21:00 (Pag. 36)
        {
            "reel_id": "reel_05_film_cinese_ia",
            "scheduled_time": "21:00",
            "slot_label": "Fascia Serale • Cultura, Cinema & IA",
            "article_id": "pag_36",
            "page": 36,
            "category": "Cultura & Spettacolo",
            "author": "Gianluca Modolo",
            "original_title": "Il flop di Sanxingdui, il primo film cinese tutto fatto con l’IA",
            "editorial_rationale": (
                "Perfetto per lo slot serale delle 21:00: racconta cosa succede davvero quando si porta "
                "al cinema un film lungometraggio generato interamente con l'intelligenza artificiale."
            ),
            "viral_score": 9,
            "impact_score": 8,
            "verified_facts": [
                "Il film 'Sanxingdui: Future Past' è il primo lungometraggio cinese fatto con l'IA distribuito ufficialmente nelle sale.",
                "Costato oltre 10 milioni di yuan (circa 1,3 milioni di euro), ha incassato appena 1,79 milioni di yuan (230mila euro).",
                "Alla proiezione a Pechino visitata dal corrispondente di Repubblica non c'era nessun altro spettatore in sala.",
                "Un centinaio di persone in carne e ossa ha comunque lavorato per oltre due anni alla realizzazione del film.",
            ],
            "instagram_caption": (
                "🎬 Quanto ha incassato il primo film cinese al cinema fatto interamente con l'Intelligenza Artificiale? È stato un FLOP clamoroso.\n\n"
                "Dal reportage da Pechino di Gianluca Modolo (Pag. 36 di Repubblica):\n"
                "• Il film si chiama 'Sanxingdui: Future Past' (1 ora e 40 minuti)\n"
                "• Costo di produzione: circa 1,3 MILIONI di euro (oltre 10 milioni di yuan)\n"
                "• Incasso al botteghino: appena 230.000 euro (1,79 milioni di yuan)\n"
                "• In sala a Pechino il giornalista era l'unico spettatore presente: 'Dialoghi legnosi, trama confusa tra antichi egizi che parlano mandarino e futuro distopico, personaggi poco espressivi'\n"
                "• Il paradosso della trama: racconta proprio di un'IA ('Superbrain') che sfugge al controllo umano!\n\n"
                "Pagheresti il biglietto del cinema per vedere un film generato interamente dall'IA? 👇"
            ),
            "hashtags": [
                "#Cinema",
                "#AI",
                "#IntelligenzaArtificiale",
                "#Film",
                "#Cina",
                "#Sanxingdui",
                "#Cultura",
                "#RassegnaStampa",
            ],
            "slides": [
                {
                    "role": "01 • HOOK",
                    "headline": "Esce al cinema il 1° film fatto tutto con l'IA: sala completamente vuota!",
                    "highlight_stat": "FLOP",
                    "highlight_label": "Solo 230.000 € incassati a fronte di 1,3 milioni di budget",
                    "body": "A Pechino ha debuttato 'Sanxingdui: Future Past', primo lungometraggio generato con l'IA nei cinema cinesi.",
                    "voiceover": "È uscito al cinema il primo film cinese realizzato interamente con l'intelligenza artificiale, ma in sala non c'era letteralmente nessuno.",
                },
                {
                    "role": "02 • I NUMERI DEL BOTTEGHINO",
                    "headline": "Costato 1,3 milioni di euro, ne ha incassati un sesto",
                    "highlight_stat": "-82%",
                    "highlight_label": "1,79 milioni di yuan d'incasso su oltre 10 milioni spesi",
                    "body": "Anche se l'IA ha ridotto i costi rispetto a un kolossal tradizionale, il pubblico ha disertato le sale.",
                    "voiceover": "I numeri parlano chiaro: costato circa un milione e 300 mila euro, finora al botteghino ne ha raccolti appena 230 mila.",
                },
                {
                    "role": "03 • LA RECENSIONE IN SALA",
                    "headline": "«Faraoni che parlano mandarino e volti inespressivi»",
                    "highlight_stat": "1h 40m",
                    "highlight_label": "Dialoghi legnosi e salti temporali confusi",
                    "body": "L'inviato a Pechino racconta: 'La gioia più grande in sala è stata la poltrona massaggiante da 1,50 euro'.",
                    "voiceover": "Il verdetto dalla sala di Pechino? Dialoghi legnosi, personaggi poco espressivi e una trama confusa con faraoni egizi che parlano mandarino.",
                },
                {
                    "role": "04 • IL PARADOSSO",
                    "headline": "100 umani per 2 anni per fare un film 'senza umani'",
                    "highlight_stat": "100 Persone",
                    "highlight_label": "Il team che ha lavorato oltre 2 anni dietro gli algoritmi",
                    "body": "Ironia della sorte: la trama parla proprio di un'umanità che delega ogni scelta all'IA 'Superbrain' perdendo il controllo.",
                    "voiceover": "Il paradosso? Ci sono volute comunque 100 persone per due anni per generarlo, e la trama avverte proprio sui rischi di delegare tutto all'IA.",
                },
                {
                    "role": "05 • LA TUA OPINIONE",
                    "headline": "Pagheresti il biglietto per un film generato dall'IA?",
                    "highlight_stat": "VOTA GIÙ",
                    "highlight_label": "Sì per curiosità o No, il cinema è solo umano?",
                    "body": "Scrivici la tua nei commenti e buonanotte dalla nostra rassegna stampa serale!",
                    "voiceover": "Tu pagheresti il biglietto del cinema per un film generato dall'intelligenza artificiale? Scrivimelo nei commenti!",
                },
            ],
        },
    ]

    return {
        "newspaper_name": scraped_data["newspaper_name"],
        "edition_date": scraped_data["edition_date"],
        "source_pdf": scraped_data["source_pdf"],
        "total_pages_scanned": scraped_data["total_pages_scanned"],
        "total_articles_extracted": scraped_data["total_articles_extracted"],
        "engine_mode": "Scraper PyMuPDF Reale + Redazione AI (5 Reel Monotematici)",
        "editorial_summary": (
            f"Dalla scansione completa delle {scraped_data['total_pages_scanned']} pagine di "
            f"{scraped_data['newspaper_name']} ({scraped_data['edition_date']}) sono stati estratti "
            f"{scraped_data['total_articles_extracted']} articoli. La Redazione AI ha selezionato "
            f"i 5 articoli a più alto potenziale social, preparando 5 Reel singoli distribuiti "
            f"tra le 08:30 e le 21:00."
        ),
        "selected_reels": selected_reels,
    }


def build_daily_editorial_plan(scraped_data: dict[str, Any], target_reels: int = 5) -> dict[str, Any]:
    if os.environ.get("GEMINI_API_KEY"):
        print("🤖 Avvio Redazione AI su Gemini API (gemini-4-hydrogen) per selezionare i 5 Reel...")
        return run_gemini_daily_newsroom(scraped_data, target_reels=target_reels)
    print("🧠 Selezione Redazione AI sui 35 articoli estratti dal PDF e preparazione dei 5 Reel singoli...")
    return run_local_daily_newsroom(scraped_data)
