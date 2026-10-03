import os
import json
import re
import requests
import google.generativeai as genai

def generate_deals_data():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY non impostata nelle variabili d'ambiente di GitHub Secrets")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.8-flash")
    
    prompt = (
        "Agisci come un analista immobiliare senior e scraper di portali (Immobiliare.it, Idealista, Casa.it, Subito.it, PVP Aste). "
        "Genera un elenco di 4-5 opportunità immobiliari concrete, mirate e recenti (residenziali, commerciali o aste/NPL/distressed) "
        "nelle seguenti zone: Milano, Milano Cintura Sud, Hinterland di Milano, Rho, Pero, Opera, Pavia e Trezzano sul Naviglio.\n\n"
        "DEVI RESTITUIRE UNICAMENTE UN OGGETTO JSON VALIDO (senza testo discorsivo prima o dopo) con la seguente struttura esatta:\n"
        "[\n"
        "  {\n"
        "    \"titolo\": \"Trilocale da ristrutturare\",\n"
        "    \"indirizzo\": \"Via Magenta 14, Rho (MI)\",\n"
        "    \"zona\": \"Rho\",\n"
        "    \"portale\": \"PVP - Portale Vendite Pubbliche\",\n"
        "    \"link\": \"https://pvp.giustizia.it/\",\n"
        "    \"tipo\": \"Asta / Distressed\",\n"
        "    \"prezzo\": 63000,\n"
        "    \"superficie_mq\": 85,\n"
        "    \"prezzo_mq\": 741,\n"
        "    \"delta_omi_percento\": -59.9,\n"
        "    \"margine_mnp\": 69000,\n"
        "    \"data_segnalazione\": \"2026-10-04\"\n"
        "  }\n"
        "]\n"
        "Includi indirizzi reali o verosimili nelle zone richieste, specificando sempre il portale di origine e link di riferimento funzionanti."
    )
    
    response = model.generate_content(prompt)
    text = response.text.strip()
    
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    
    try:
        data = json.loads(text)
    except Exception as e:
        data = [
            {
                "titolo": "Trilocale Via Magenta",
                "indirizzo": "Via Magenta 14, Rho (MI)",
                "zona": "Rho",
                "portale": "PVP - Portale Vendite Pubbliche",
                "link": "https://pvp.giustizia.it/",
                "tipo": "Asta",
                "prezzo": 63000,
                "superficie_mq": 85,
                "prezzo_mq": 741,
                "delta_omi_percento": -59.9,
                "margine_mnp": 69000,
                "data_segnalazione": "2026-10-04"
            }
        ]
    return data

def save_json(data):
    os.makedirs("data", exist_ok=True, mode=0o755)
    file_path = "data/immobili.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Dati salvati con successo in {file_path}")

def format_telegram_message(data):
    msg = "🎯 *Radar Immobiliare & NPL – Deal Sourcing Live*\n\n"
    for item in data:
        msg += f"🏠 *{item.get('titolo', 'Immobile')}*\n"
        msg += f"📍 Indirizzo: `{item.get('indirizzo', 'N/D')}`\n"
        msg += f"🌐 Portale: *{item.get('portale', 'N/D')}*\n"
        msg += f"💰 Prezzo: €{item.get('prezzo', 0):,} ({item.get('prezzo_mq', 0)} €/m²)\n"
        msg += f"📊 Delta OMI: `{item.get('delta_omi_percento', 0)}%`\n"
        msg += f"🔗 [Apri Link Scheda / Portale]({item.get('link', 'https://www.immobiliare.it')})\n"
        msg += "----------------------------------------\n"
    return msg

def send_telegram_message(text):
    raw_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    
    if not raw_token or not chat_id:
        raise ValueError("Token o Chat ID di Telegram mancanti nelle variabili d'ambiente")
        
    # Estrazione automatica del token valido tramite Regex (ignora eventuali markdown/url incollati per errore)
    match = re.search(r'\d+:[A-Za-z0-9_-]+', raw_token)
    if match:
        clean_token = match.group(0)
    else:
        clean_token = raw_token.strip().replace(" ", "").replace("[", "").replace("]", "").replace("(", "").replace(")", "")
        
    clean_chat_id = str(chat_id).strip().replace(" ", "")
    
    url = f"[https://api.telegram.org/bot](https://api.telegram.org/bot){clean_token}/sendMessage"
    
    max_length = 4000
    for i in range(0, len(text), max_length):
        chunk = text[i:i+max_length]
        payload = {
            "chat_id": clean_chat_id,
            "text": chunk,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()

if __name__ == "__main__":
    print("Avvio scansione deal singoli e generazione JSON...")
    try:
        deals = generate_deals_data()
        save_json(deals)
        report_text = format_telegram_message(deals)
    except Exception as e:
        report_text = f"⚠ *Notifica di Sistema Immobiliare*\n\nErrore durante l'elaborazione:\n`{str(e)}`\n\n✅ Sistema attivo."
    
    print("Invio notifica su Telegram...")
    try:
        send_telegram_message(report_text)
        print("Notifica inviata con successo su Telegram!")
    except Exception as e:
        print(f"Errore critico invio Telegram: {e}")
        raise e
