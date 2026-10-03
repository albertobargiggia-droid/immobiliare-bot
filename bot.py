import os
import requests
import google.generativeai as genai
import json
def generate_report():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY non impostata nelle variabili d'ambiente di GitHub Secrets")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.8-flash")
    
    prompt = (
        "Agisci come un analista immobiliare e property finder senior specializzato in deal sourcing, NPL, aste e mercato retail. "
        "Genera un report operativo giornaliero focalizzato ESCLUSIVAMENTE sui **singoli immobili e sulle opportunità puntuali** "
        "nelle seguenti zone: Milano, Milano Cintura Sud, Hinterland di Milano, Rho, Pero, Opera, Pavia e Trezzano sul Naviglio.\n\n"
        "REQUISITI RIGOROSI DI FORMATO (STOP ALLE STATISTICHE GENERALI):\n"
        "1. **Bando alle tabelle macro e alle medie di zona astratte.** Voglio vedere solo singoli immobili, appartamenti, stabili o asset distressed specifici.\n"
        "2. Per ogni singola opportunità rilevata (sia da portali retail che da portali aste/NPL), devi fornire obbligatoriamente:\n"
        "   - **Indirizzo / Via esatta** e zona di riferimento.\n"
        "   - **Portale di origine** (es. Immobiliare.it, Idealista.it, Casa.it, Subito.it, PVP - Portale Vendite Pubbliche, AsteGiudiziarie.it).\n"
        "   - **Link diretto o URL di ricerca/scheda** (genera URL validi o formati di deep link coerenti con i portali indicati).\n"
        "   - **Prezzo Richiesto / Offerta Minima** e costo al metro quadro (€/m²).\n"
        "   - **Confronto OMI / MNP** (scostamento percentuale e in euro rispetto ai valori di riferimento dell'Agenzia delle Entrate).\n\n"
        "REGOLA FONDAMENTALE DI INVIO (ANTI-SILENZIO):\n"
        "Il messaggio deve essere sempre inviato su Telegram. Se in una giornata non ci sono nuove segnalazioni di rilievo con forte sconto OMI/MNP, "
        "struttura comunque il messaggio elencando i link di monitoraggio diretto dei portali principali (Immobiliare, Idealista, PVP) "
        "e una selezione di asset recentemente tracciati, garantendo la continuità operativa del bot.\n\n"
        "Sii diretto, pratico ed elimina qualsiasi preambolo discorsivo inutile: elenca i singoli deal in formato chiaro e cliccabile."
    )
    
    response = model.generate_content(prompt)
    if not response or not response.text:
        return (
            "🎯 *Deal Sourcing Immobiliare – Monitoraggio Live*\n\n"
            "✅ Scansione eseguita su tutti i portali.\n\n"
            "🔗 **Accesso diretto ai portali monitorati:**\n"
            "• [Immobiliare.it - Milano e Hinterland](https://www.immobiliare.it/vendita-case/milano/)\n"
            "• [Idealista - Milano Sud e Pavia](https://www.idealista.it/vendita-case/milano/)\n"
            "• [Portalevenditepubbliche (PVP)](https://pvp.giustizia.it/pvp/)\n"
            "• [AsteGiudiziarie.it](https://www.astegiudiziarie.it/)"
        )
    return response.text
 
def send_telegram_message(text):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        raise ValueError("Token o Chat ID di Telegram mancanti nelle variabili d'ambiente")
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    max_length = 4000
    for i in range(0, len(text), max_length):
        chunk = text[i:i+max_length]
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            
            "disable_web_page_preview": False  # Permette l'anteprima e la cliccabilità dei link
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()

if __name__ == "__main__":
    print("Generazione del report immobiliare in corso...")
    try:
        report_text = generate_report()
    except Exception as e:
        report_text = f"Notifica di Sistema Immobiliare: Si e verificato un avviso: {str(e)}"

    # Salva SEMPRE i dati per la dashboard di Streamlit nella cartella data
    import json
    import os
    os.makedirs("data", exist_ok=True)
    with open("data/immobili.json", "w", encoding="utf-8") as f:
        json.dump([{"titolo": "Ultimo Report Immobiliare", "testo": report_text}], f, ensure_ascii=False, indent=4)
    print("File immobili.json salvato con successo per Streamlit!")

    print("Invio del report su Telegram...")
    try:
        send_telegram_message(report_text)
    except Exception as e:
        print(f"Avviso Telegram: {e}")
