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
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Errore nell'invio del messaggio Telegram: {e}")

def main():
    if not GEMINI_API_KEY or not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Errore critico: Mancano le chiavi segrete (Secrets) su GitHub.")
        return

    # 1. Configurazione di Google Gemini
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # 2. Aree geografiche mirate aggiornate con Trezzano
    zone_target = "Milano, Milano Cintura Sud, Hinterland di Milano, Rho, Pero, Opera, Pavia e Trezzano"

    # 3. Prompt dettagliato con le zone e il focus sulle aste giudiziarie (PVP) e mercato
    prompt = (
        f"Agisci come un analista immobiliare esperto focalizzato rigorosamente su queste aree: {zone_target}. "
        "Genera un report di mercato strutturato e professionale analizzando le tendenze, le opportunità di acquisto, "
        "i ribassi di prezzo e le aste giudiziarie (PVP - Portale Vendite Pubbliche) rilevanti per queste specifiche zone. "
        "Sii sintetico, chiaro e usa una formattazione pulita ottimizzata per Telegram."
    )

    try:
        response = model.generate_content(prompt)
        report_analizzato = response.text
    except Exception as e:
        report_analizzato = f"Errore durante la generazione del report con l'intelligenza artificiale: {e}"

    # 4. Invio del report mirato su Telegram
    testo_finale = f"🏠 *REPORT IMMOBILIARE MIRATO*\n📍 *Zone:* {zone_target}\n\n{report_analizzato}"
    manda_messaggio_telegram(testo_finale)

if __name__ == "__main__":
    main()
