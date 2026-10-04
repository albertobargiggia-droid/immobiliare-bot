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
  """Genera i deal tramite Gemini con coordinate, link mirati e gestione errori."""
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
    - Includi coordinate geografiche realistiche (latitudine e longitudine) per l'indirizzo indicato.
    - Includi un campo "colore_mappa" basato sul margine: "green" se margine >= 40000, "orange" se tra 30000 e 39999, "red" se < 30000.
    - IMPORTANTE per il campo "link": genera un URL di ricerca mirato e plausibile del portale di riferimento (es. Immobiliare.it o PVP Aste) pre-filtrato per la zona e la tipologia, in modo da indirizzare direttamente l'utente ai risultati coerenti.
    - Includi segnali di UTP/ribassi sequenziali, dati aste (se giudiziari: 1°, 2°, 3° battuta, data asta, link perizia CTU e planimetria), link OMI Agenzia delle Entrate con indice di liquidità e trend %.

    DEVI RESTITUIRE ESCLUSIVAMENTE UN ARRAY JSON VALIDO (formato JSON puro, senza testo discorsivo prima o dopo, racchiuso o meno da blocchi markdown).
    Usa questa struttura esatta per ogni elemento:
    [
      {{
        "titolo": "Trilocale in asta / pre-asta",
        "indirizzo": "Via Roma 10, Rho (MI)",
        "zona": "Rho",
        "portale": "PVP Aste / Immobiliare.it",
        "link": "https://www.immobiliare.it/vendita-case/rho/?criterio=rilevanza",
        "canale": "Asta / Procedura Giudiziaria",
        "stato_giudiziario": "NPL / Asta Giudiziaria",
        "storico_ribassi": "Ribassato 3 volte",
        "esecutato_proprietario": "Mario Rossi",
        "dettagli_debiti": "Decreto ingiuntivo condominiale",
        "stato_asta": "Seconda battuta",
        "data_asta": "2026-11-15",
        "link_perizia_ctu": "https://pvp.giustizia.it/",
        "link_planimetria": "https://pvp.giustizia.it/",
        "prezzo": 120000,
        "superficie_mq": 80,
        "prezzo_mq": 1500,
        "delta_omi_percento": -30.0,
        "margine_mnp": 35000,
        "lat": 45.5212,
        "lon": 9.0321,
        "colore_mappa": "orange",
        "link_omi": "https://www.agenziaentrate.gov.it/portale/schede/fabbricateritreni/omi/consultazione-quotazioni-immobiliari",
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
    print(f"Attenzione: Fallito il parsing diretto del JSON dall'AI. Errore: {e}")
    return []

  return deals if isinstance(deals, list) else []


def save_json_persistent(new_deals):
  """Salvataggio sicuro: aggiorna i dati preservando i preferiti, la mappa e i link."""
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
      print(f"Nota: Storico precedente non leggibile. Verrà rigenerato. {e}")
      existing_deals = []

  existing_dict = {
      item.get("indirizzo"): item for item in existing_deals if item.get("indirizzo")
  }

  final_deals = []
  updated_count = 0
  added_count = 0

  for new_deal in new_deals:
    addr = new_deal.get("indirizzo")
    if addr and addr in existing_dict:
      old_deal = existing_dict[addr]
      new_deal["preferito"] = old_deal.get("preferito", False)
      final_deals.append(new_deal)
      del existing_dict[addr]
      updated_count += 1
    else:
      new_deal["preferito"] = False
      final_deals.append(new_deal)
      added_count += 1

  for addr, old_deal in existing_dict.items():
    final_deals.append(old_deal)

  try:
    with open(file_path, "w", encoding="utf-8") as f:
      json.dump(final_deals, f, ensure_ascii=False, indent=2)
    print(
        f"Database aggiornato: {added_count} nuovi, {updated_count} aggiornati."
        f" Totale in archivio: {len(final_deals)} immobili."
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
    msg += f"🔗 [Apri Ricerca Mirata]({item.get('link', '#')})\n"
    msg += "----------------------------------------\n"

  payload = {
      "chat_id": chat_id.strip().replace(" ", ""),
      "text": msg,
      "parse_mode": "Markdown",
      "disable_web_page_preview": True,
  }

  try:
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
  except Exception as e:
    print(f"Avviso non bloccante Telegram: {e}")


if __name__ == "__main__":
  print("=== AVVIO SCRIPT ANALISI IMMOBILIARE ===")
  try:
    deals = generate_deals_data()
    save_json_persistent(deals)
    send_telegram_message(deals)
    print("=== ESECUZIONE COMPLETATA CON SUCCESSCO ===")
  except Exception as e:
    print(f"ERRORE CRITICO INTERCETTATO NEL MAIN: {e}")
    raise e
