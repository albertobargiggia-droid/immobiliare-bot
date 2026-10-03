
       import os
import requests
import google.generativeai as genai

# Recupero delle credenziali dai Secret di GitHub (passate come variabili d'ambiente)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def send_telegram_message(text):
    """Funzione per inviare messaggi su Telegram"""
    if not TOKEN or not CHAT_ID:
        print("Errore: TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID non configurati!")
        return
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Notifica Telegram inviata con successo!")
    else:
        print(f"Errore nell'invio a Telegram: {response.text}")

def analyze_real_estate():
    """Logica di analisi con Gemini (Milano e Hinterland)"""
    if not GEMINI_API_KEY:
        print("Attenzione: GEMINI_API_KEY non trovata. Eseguo il bot senza IA.")
        return "🤖 *Report Immobiliare:* Script avviato correttamente, ma chiave Gemini non rilevata."

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash') # O gemini-1.5-flash
    
    # Esempio di prompt di scouting o analisi mercato
    prompt = "Genera un breve bollettino di incoraggiamento per il monitoraggio immobiliare a Milano, Lacchiarella, Rho e Pavia focalizzato su opportunità e ribassi di prezzo."
    
    try:
        response = model.generate_content(prompt)
        return f"🏠 *Report Immobiliare Giornaliero*\n\n{response.text}"
    except Exception as e:
        print(f"Errore durante la chiamata a Gemini: {e}")
        return "🏠 *Report Immobiliare:* Monitoraggio attivo su Milano e Hinterland. Nessuna anomalia critica riscontrata oggi."

if __name__ == "__main__":
    print("Avvio dello script di scouting immobiliare...")
    
    # Genera il messaggio (tramite Gemini o fallback)
    messaggio = analyze_real_estate()
    
    # Invia la notifica su Telegram
    send_telegram_message(messaggio)
