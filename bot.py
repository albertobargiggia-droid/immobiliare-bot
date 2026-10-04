import os
import json
import requests
import google.generativeai as genai

def generate_deals_data():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY non impostata nelle variabili d'ambiente")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.8-flash")
    
    prompt = (
        "Agisci come un analista immobiliare senior. "
        "Genera un elenco di 4 opportunità immobiliari concrete in formato JSON puro nelle zone: "
        "Milano, Rho, Opera, Pavia, Trezzano sul Naviglio, Lacchiarella, Binasco, Siziano, Zibido San Giacomo, Pero, Rozzano, Giussago, Casarile, Noviglio, San Pietro Cusico, Moirago, Fizzonasco, Noviglio, Lainate, via Forlanini Milano, Scalo Romana Milano, Rogoredo, Salvanesco, Metanopoli Milano, San donato Milanese, Settimo Milanese, via Capecelatro Milano, San siro Milano, San Giuliano Milanese, Giovenzano, Borgarello, Arenzano, Santa corinna, Quinto De Stampi, Chiesa Rossa, Assago, Corsico, Buccinasco, Baggio, Milano cintura sud.\n"
        "Restituisci UNICAMENTE un oggetto JSON valido (senza markdown attorno se non il blocco json) con questa struttura esatta:\n"
        "[\n"
        "  {\n"
        "    \"titolo\": \"Trilocale da ristrutturare\",\n"
        "    \"indirizzo\": \"Via Magenta 14, Rho (MI)\",\n"
        "    \"zona\": \"Rho\",\n"
        "    \"portale\": \"Immobiliare.it\",\n"
        "    \"link\": \"https://www.immobiliare.it\",\n"
        "    \"tipo\": \"Residenziale\",\n"
        "    \"prezzo\": 63000,\n"
        "    \"superficie_mq\": 85,\n"
        "    \"prezzo_mq\": 741,\n"
        "    \"delta_omi_percento\": -59.9,\n"
        "    \"margine_mnp\": 69000,\n"
        "    \"data_segnalazione\": \"2026-10-04\"\n"
        "  }\n"
        "]"
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
    
    return json.loads(text)

def save_json(data):
    os.makedirs("data", exist_ok=True, mode=0o755)
    with open("data/immobili.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("File data/immobili.json salvato correttamente per Streamlit.")

def send_telegram_message(deals):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    
    if not token or not chat_id:
        raise ValueError("Token o Chat ID di Telegram mancanti")
        
    # Pulizia di sicurezza estrema del token da eventuali caratteri estranei
    for char in ["[", "]", "(", ")", "*", "_", "`", " "]:
        token = token.replace(char, "")
    
    # Se per errore nel secret c'è un URL intero, estrae solo la parte finale del token
    if "api.telegram.org" in token:
        token = token.split("bot")[-1].split("/")[0]

    # Costruzione URL pulita al 100% senza f-string rischiose
    url = "https://api.telegram.org/bot" + token + "/sendMessage"
    
    msg = "🎯 *Radar Immobiliare & NPL – Deal Sourcing Live*\n\n"
    for item in deals:
        msg += f"🏠 *{item.get('titolo')}*\n"
        msg += f"📍 `{item.get('indirizzo')}`\n"
        msg += f"🌐 Portale: *{item.get('portale')}*\n"
        msg += f"💰 Prezzo: €{item.get('prezzo'):,} ({item.get('prezzo_mq')} €/m²)\n"
        msg += f"📊 Delta OMI: `{item.get('delta_omi_percento')}%`\n"
        msg += f"🔗 [Apri Link Scheda]({item.get('link')})\n"
        msg += "----------------------------------------\n"
        
    payload = {
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    
    print("Invio notifica Telegram in corso...")
    response = requests.post(url, json=payload)
    response.raise_for_status()
    print("Notifica Telegram inviata con successo!")

if __name__ == "__main__":
    try:
        deals = generate_deals_data()
        save_json(deals)
        send_telegram_message(deals)
    except Exception as e:
        print(f"Errore critico: {e}")
        raise e
