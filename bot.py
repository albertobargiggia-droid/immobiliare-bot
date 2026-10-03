import os
import requests
import google.generativeai as genai

# Recuperiamo le chiavi salvate in modo sicuro su GitHub
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def manda_messaggio_telegram(testo):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": testo,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

def main():
    # 1. Configurazione di Google Gemini
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # 2. Chiediamo a Gemini di generare un report di mercato immobiliare a Milano e aste
    prompt = (
        "Agisci come un analista immobiliare esperto a Milano. "
        "Genera un report giornaliero di esempio per il mercato immobiliare residenziale a Milano "
        "e per le aste giudiziarie (PVP), evidenziando 2 ipotetiche occasioni con ribassi di prezzo "
        "interessanti o immobili sottovalutati. Sii sintetico, professionale e usa una formattazione pulita per Telegram."
    )

    response = model.generate_content(prompt)
    report_analizzato = response.text

    # 3. Invio del report su Telegram
    testo_finale = f"🏠 *REPORT IMMOBILIARE GIORNALIERO (Milano)*\n\n{report_analizzato}"
    manda_messaggio_telegram(testo_finale)

if __name__ == "__main__":
    main()
