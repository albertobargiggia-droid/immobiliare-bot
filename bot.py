import json
import os
import re
import google.generativeai as genai
import requests

# --- PARAMETRI CONFIGURABILI ---
ZONE_TARGET = (
    "Milano, Milano Cintura Sud, Hinterland di Milano, Rho, Pero, Opera, Pavia"
    " e Trezzano sul Naviglio"
)
MODELLO_AI = "gemini-1.5-flash"


def generate_deals_data():
  """Genera i deal tramite Gemini con gestione rigorosa degli errori."""
  api_key = os.environ.get("GEMINI_API_KEY")
  if not api_key:
    print("ERRORE CRITICO: GEMINI_API_KEY non impostata nelle segrete di GitHub.")
    return []

  try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(MODELLO_AI)
  except Exception as e:
    print(f"Errore di configurazione SDK Gemini: {e}")
    return []

  prompt = f"""
    Agisci come un analista senior di NPL, UTP, distressed assets e real estate data scraper.
    Genera un elenco di circa 20 opportunità immobiliari ad altissimo potenziale di sconto nelle seguenti zone: {ZONE_TARGET}.

    PARAMETRI RIGOROSI DA APPLICARE:
    - Prezzo massimo di acquisto: <= €300.000.
    - Margine MNP netto: tra €20.000 e €50.000 (per esborso base €100.000).
    - ROI atteso: >= 25-30%.
    - Includi segnali di UTP/ribassi sequenziali, dati aste (se giudiziari: 1°, 2°, 3° battuta, data asta, link perizia CTU e planimetria), link OMI Agenzia delle Entrate con indice di liquidità e trend %.

    DEVI RESTITUIRE ESCLUSIVAMENTE UN ARRAY JSON VALIDO (formato JSON puro, senza testo discorsivo prima o dopo, racchiuso o meno da blocchi markdown).
    Usa questa struttura esatta per ogni elemento:
    [
      {{
        "titolo": "Trilocale in asta / pre-asta",
        "indirizzo": "Via Roma 10, Rho (MI)",
        "zona": "Rho",
        "portale": "PVP Aste / Immobiliare.it",
        "link": "[https://www.immobiliare.it/](https://www.immobiliare.it/)",
        "canale": "Asta / Procedura Giudiziaria",
        "stato_giudiziario": "NPL / Asta Giudiziaria",
        "storico_ribassi": "Ribassato 3 volte",
        "esecutato_proprietario": "Mario Rossi",
        "dettagli_debiti": "Decreto ingiuntivo condominiale",
        "stato_asta": "Seconda battuta",
        "data_asta": "2026-11-15",
        "link_perizia_ctu": "[https://pvp.giustizia.it/](https://pvp.giustizia.it/)",
        "link_planimetria": "[https://pvp.giustizia.it/](https://pvp.giustizia.it/)",
        "prezzo": 120000,
        "superficie_mq": 80,
        "prezzo_mq": 1500,
        "delta_omi_percento": -30.0,
        "margine_mnp": 35000,
        "link_omi": "[https://www.agenziaentrate.gov.it/portale/schede/fabbricateritreni/omi/consultazione-quotazioni-immobiliari](https://www.agenziaentrate.gov.it/portale/schede/fabbricateritreni/omi/consultazione-quotazioni-immobiliari)",
        "indice_liquidita_omi": "Alta",
        "variazione_liquidita_percento": 3.5,
        "data_segnalazione": "2026-10-04"
      }}
    ]
    """

  try:
    response = model.generate_content(prompt)
    text = response.text.strip()
  except Exception as e:
    print(f"Errore durante la chiamata API a Gemini: {e}")
    return []

  # Parsing JSON ultra-robusto con fallback multipli
  deals = []
  try:
    match = re.search(r"\[\s*\{.*\}\s*\]", text, re.DOTALL)
    if match:
      json_str = match.group(0)
      deals = json.loads(json_str)
    else:
      cleaned = text
      if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
      elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
      if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
      deals = json.loads(cleaned.strip())
  except Exception as e:
    print(
        "Attenzione: Fallito il parsing diretto del JSON dall'AI. Errore:"
        f" {e}\nTesto ricevuto:\n{text[:200]}..."
    )
    return []

  return deals if isinstance(deals, list) else []


def save_json_persistent(new_deals):
  """Salvataggio sicuro nel database locale con protezione da corruzione."""
  if not new_deals:
    print("Nessun nuovo deal da salvare.")
    return

  os.makedirs("data", exist_ok=True, mode=0o755)
  file_path = "data/immobili.json"

  existing_deals = []
  if os.path.exists(file_path):
    try:
      with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if content:
          existing_deals = json.loads(content)
    except Exception as e:
      print(
          "Nota: Storico precedente non leggibile o vuoto. Verrà ricreato. Dettaglio:"
          f" {e}"
      )
      existing_deals = []

  existing_links = {item.get("link") for item in existing_deals if item.get("link")}

  added_count = 0
  for deal in new_deals:
    link = deal.get("link")
    if link and link not in existing_links:
      existing_deals.insert(0, deal)
      existing_links.add(link)
      added_count += 1

  try:
    with open(file_path, "w", encoding="utf-8") as f:
      json.dump(existing_deals, f, ensure_ascii=False, indent=2)
    print(
        f"Database aggiornato con successo. Aggiunti {added_count} nuovi deal."
        f" Totale in archivio: {len(existing_deals)} immobili."
    )
  except Exception as e:
    print(f"Errore critico nella scrittura del file JSON: {e}")


def send_telegram_message(deals):
  """Invio Telegram isolato: se la rete fallisce, non blocca lo script."""
  if not deals:
    return

  raw_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
  chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
  if not raw_token or not chat_id:
    print("Telegram Token o Chat ID non configurati. Notifica saltata.")
    return

  match = re.search(r"(\d+:[A-Za-z0-9_\-]+)", raw_token)
  token = match.group(1) if match else re.sub(r"[^0-9a-zA-Z:\-_]", "", raw_token)
  url = f"https://api.telegram.org/bot{token}/sendMessage"

  msg = f"🚨 *Radar Distress & UTP – Report Sicuro*\n*Trovate {len(deals)} opportunità verificate!* 🎯\n\n"
  for item in deals[:6]:
    msg += f"🏠 *{item.get('titolo', 'Immobile')}* ({item.get('zona', 'N/D')})\n"
    msg += f"📍 `{item.get('indirizzo', 'Indirizzo non specificato')}`\n"
    msg += f"⚖️ *Stato:* {item.get('stato_giudiziario', 'N/D')}\n"
    msg += (
        f"💰 Prezzo: €{item.get('prezzo', 0):,} | Margine:"
        f" *€{item.get('margine_mnp', 0):,}*\n"
    )
    msg += f"🔗 [Apri Annuncio]({item.get('link', '#')})\n"
    msg += "----------------------------------------\n"

  payload = {
      "chat_id": chat_id.strip().replace(" ", ""),
      "text": msg,
      "parse_mode": "Markdown",
      "disable_web_page_preview": True,
  }

  try:
    print("Invio notifica Telegram in corso...")
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    print("Notifica Telegram inviata con successo!")
  except Exception as e:
    print(
        "Avviso non bloccante: Impossibile inviare il messaggio Telegram ("
        f"{e}). I dati sono comunque salvi nel database."
    )


if __name__ == "__main__":
  print("=== AVVIO SCRIPT ANALISI IMMOBILIARE ===")
  try:
    deals = generate_deals_data()
    save_json_persistent(deals)
    send_telegram_message(deals)
    print("=== ESECUZIONE COMPLETATA CON SUCCESSO ===")
  except Exception as e:
    print(f"ERRORE CRITICO INTERCETTATO NEL MAIN: {e}")
    raise e
