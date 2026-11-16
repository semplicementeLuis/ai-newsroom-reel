"""
Genera un PDF di esempio in stile quotidiano italiano ("IL QUOTIDIANO DEL FUTURO")
con layout multi-colonna e 4 articoli distinti per testare la pipeline.
"""

from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def wrap_text(c: canvas.Canvas, text: str, font_name: str, font_size: int, max_width: float) -> list[str]:
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if c.stringWidth(test_line, font_name, font_size) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines


def draw_article_block(
    c: canvas.Canvas,
    x: float,
    y_top: float,
    width: float,
    category: str,
    title: str,
    subtitle: str,
    body: str,
) -> float:
    y = y_top
    # Categoria (Occhiello)
    c.setFillColor(colors.HexColor("#B91C1C"))
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x, y, category.upper())
    y -= 13

    # Titolo
    c.setFillColor(colors.HexColor("#111827"))
    title_lines = wrap_text(c, title, "Times-Bold", 14, width)
    for line in title_lines:
        c.setFont("Times-Bold", 14)
        c.drawString(x, y, line)
        y -= 16

    # Sottotitolo
    y -= 2
    c.setFillColor(colors.HexColor("#374151"))
    sub_lines = wrap_text(c, subtitle, "Times-Italic", 10, width)
    for line in sub_lines:
        c.setFont("Times-Italic", 10)
        c.drawString(x, y, line)
        y -= 12

    y -= 6
    # Corpo
    c.setFillColor(colors.HexColor("#1F2937"))
    body_lines = wrap_text(c, body, "Times-Roman", 9.5, width)
    for line in body_lines:
        c.setFont("Times-Roman", 9.5)
        c.drawString(x, y, line)
        y -= 11.5

    return y


def create_sample_newspaper(output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output_path), pagesize=A4)
    width, height = A4  # 595.27 x 841.89

    # Testata del Quotidiano
    c.setFillColor(colors.HexColor("#0F172A"))
    c.setFont("Times-Bold", 28)
    c.drawCentredString(width / 2, height - 50, "IL QUOTIDIANO DEL MATTINO")

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#475569"))
    c.drawCentredString(
        width / 2,
        height - 66,
        "Edizione Nazionale • Lunedì 16 Novembre 2026 • Anno XXIV N. 318 • Pagina 1",
    )

    c.setStrokeColor(colors.HexColor("#0F172A"))
    c.setLineWidth(1.5)
    c.line(36, height - 74, width - 36, height - 74)
    c.setLineWidth(0.5)
    c.line(36, height - 77, width - 36, height - 77)

    margin = 36
    col_gap = 18
    col_width = (width - 2 * margin - col_gap) / 2

    # --- ARTICOLO 1 (Colonna Sinistra, Alto) ---
    y_left = height - 98
    y_left = draw_article_block(
        c,
        margin,
        y_left,
        col_width,
        category="ENERGIA & TECNOLOGIA",
        title="Batterie al sodio: parte in Italia la prima gigafactory senza litio",
        subtitle="Costi ridotti del 40% e zero dipendenza da terre rare: produzione al via nel 2027 con 1.200 nuovi posti di lavoro.",
        body=(
            "Una svolta industriale per la transizione energetica europea parte dal polo tecnologico "
            "di Torino. Il consorzio europeo VoltItalia ha annunciato ieri un investimento da 680 milioni "
            "di euro per convertire un ex stabilimento metalmeccanico nella prima gigafactory del Sud Europa "
            "interamente dedicata alle batterie agli ioni di sodio. A differenza degli attuali accumulatori "
            "al litio-ferro-fosfato, la nuova chimica utilizza sale industriale abbondante e a basso costo, "
            "eliminando del tutto cobalto, nichel e litio. Secondo i dati diffusi dal Politecnico, le celle "
            "di seconda generazione raggiungono una densità energetica di 165 Wh/kg, ideale per le citycar "
            "elettriche sotto i 18.000 euro e per lo stoccaggio delle reti solari ed eoliche. Il costo per "
            "kilowattora scenderà del 40% rispetto alle equivalenti celle al litio, mentre i tempi di ricarica "
            "rapida dal 10 all'80% restano sotto i 18 minuti anche a temperature rigide fino a -20 gradi. "
            "Il piano prevede l'assunzione di 1.200 tra ingegneri e tecnici specializzati entro il terzo "
            "trimestre del 2027, con una capacità iniziale di 12 GWh all'anno."
        ),
    )

    # Separatore orizzontale colonna sinistra
    y_left -= 12
    c.setStrokeColor(colors.HexColor("#CBD5E1"))
    c.line(margin, y_left, margin + col_width, y_left)
    y_left -= 18

    # --- ARTICOLO 2 (Colonna Sinistra, Basso) ---
    draw_article_block(
        c,
        margin,
        y_left,
        col_width,
        category="LAVORO & SOCIETÀ",
        title="Settimana corta di 4 giorni: in 180 aziende italiane produttività su del 14%",
        subtitle="Il bilancio dopo 12 mesi di sperimentazione a parità di stipendio: crolla l'assenteismo (-38%).",
        body=(
            "A un anno dall'avvio del più ampio programma sperimentale sulla settimana lavorativa di "
            "quattro giorni in Italia, l'Osservatorio del Lavoro dell'Università Statale di Milano ha "
            "pubblicato i risultati su un campione di 180 imprese manifatturiere e digitali per un totale "
            "di 24.500 dipendenti. Con la formula 100-80-100 (100% della retribuzione, 80% delle ore "
            "lavorate, 100% degli obiettivi mantenuti), il 91% delle aziende partecipanti ha deciso di "
            "rendere strutturale la misura. L'indice di produttività oraria è cresciuto in media del 14%, "
            "trainato dalla drastica riduzione delle riunioni improduttive (-45% del tempo speso in call) "
            "e dall'adozione di strumenti di automazione documentale. Inoltre le giornate di assenza per "
            "malattia o stress sono diminuite del 38% e le dimissioni volontarie sono scese ai minimi storici."
        ),
    )

    # Linea verticale tra le colonne
    c.setStrokeColor(colors.HexColor("#CBD5E1"))
    c.line(width / 2, height - 90, width / 2, 55)

    # --- ARTICOLO 3 (Colonna Destra, Alto) ---
    x_right = margin + col_width + col_gap
    y_right = height - 98
    y_right = draw_article_block(
        c,
        x_right,
        y_right,
        col_width,
        category="MEDICINA & IA",
        title="Diagnosi precoce della retina: un algoritmo individua il rischio cardiaco in 3 secondi",
        subtitle="Testato su 90.000 pazienti in 12 ospedali pubblici: precisione del 93% senza esami invasivi.",
        body=(
            "Basta una semplice fotografia del fondo oculare, eseguita in ambulatorio in meno di tre "
            "secondi, per stimare con cinque anni di anticipo il rischio di infarto o ictus. È il risultato "
            "dello studio multicentrico CardioSight coordinato dall'Istituto Superiore di Sanità insieme "
            "a dodici policlinici italiani. Analizzando la micro-vascolarizzazione della retina attraverso "
            "una rete neurale ad alta risoluzione, il sistema individua alterazioni invisibili all'occhio "
            "umano correlate all'ipertensione silente e alla rigidità arteriosa. Su 90.000 pazienti "
            "monitorati, il modello ha raggiunto un'accuratezza predittiva del 93%, superando i tradizionali "
            "calcolatori basati solo su colesterolo ed età. Da gennaio lo screening rapido sarà integrato "
            "gratuitamente nelle visite oculistiche di routine per gli over 50."
        ),
    )

    # Separatore orizzontale colonna destra
    y_right -= 12
    c.setStrokeColor(colors.HexColor("#CBD5E1"))
    c.line(x_right, y_right, x_right + col_width, y_right)
    y_right -= 18

    # --- ARTICOLO 4 (Colonna Destra, Basso) ---
    draw_article_block(
        c,
        x_right,
        y_right,
        col_width,
        category=" TRASPORTI & CITTÀ",
        title="Alta velocità notturna: nuovi treni letto collegheranno Milano, Roma e Palermo",
        subtitle="Biglietti da 49 euro e cabine singole insonorizzate: debutto previsto con l'orario invernale.",
        body=(
            "Ritorna in veste tecnologica il treno notturno a lunga percorrenza. Presentati ieri i nuovi "
            "convogli dotati di cabine singole e doppie con insonorizzazione attiva, connessione satellitare "
            "ad alta velocità e attraversamento rapido dello Stretto. Partendo da Milano alle 21:30 si "
            "arriverà nel centro di Palermo alle 8:45 del mattino successivo. L'obiettivo è sottrarre "
            "almeno 450.000 passeggeri all'anno alle tratte aeree nazionali più trafficate, tagliando le "
            "emissioni di CO2 per viaggiatore dell'82%."
        ),
    )

    # Footer
    c.setStrokeColor(colors.HexColor("#0F172A"))
    c.line(margin, 42, width - margin, 42)
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#64748B"))
    c.drawString(margin, 28, "IL QUOTIDIANO DEL MATTINO - Redazione Centrale")
    c.drawRightString(width - margin, 28, "Edizione PDF per rassegna stampa automatica")

    c.showPage()
    c.save()
    return output_path


if __name__ == "__main__":
    out = create_sample_newspaper(Path(__file__).parent / "input" / "quotidiano_esempio.pdf")
    print(f"Creato PDF di esempio: {out}")
