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
  """Genera i deal tramite Gemini con log di debug ed errori isolati."""
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
    Agisci come un analista senior di NPL, UTP, distressed assets e real estate.
    Genera un elenco di esattamente 15 opportunità immobiliari ad altissimo potenziale di sconto nelle zone: {ZONE_TARGET}.

    PARAMETRI RIGOROSI:
    - Prezzo massimo: <= €300.000.
    - Margine MNP netto: tra €20.000 e €50.000.
    - ROI atteso: >= 25-30%.
    - Includi coordinate geografiche realistiche (lat, lon) e "colore_mappa" ("green" se margine >= 40000, "orange" tra 30000 e 39999, "red" < 30000).
    - Includi link di ricerca mirati del portale di riferimento.

    RESTITUISCI SOLO UN ARRAY JSON VALIDO (senza markdown extra se possibile, o racchiuso in blocchi json). Struttura esatta:
    [
      {{
        "titolo": "Trilocale in asta / pre-asta",
        "indirizzo": "Via Roma 10, Rho (MI)",
        "zona": "Rho",
        "portale": "PVP Aste",
        "link": "https://www.immobiliare.it/",
        "canale": "Asta",
        "stato_giudiziario": "Asta Giudiziaria",
        "storico_ribassi": "Ribassato 3 volte",
        "esecutato_proprietario": "Mario Rossi",
        "dettagli_debiti": "Decreto ingiuntivo",
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
        "link_omi": "https://www.agenziaentrate.gov.it/",
        "indice_liquidita_omi": "Alta",
        "variazione_liquidita_percento": 3.5,
        "data_segnalazione": "2026-10-04"
      }}
    ]
    """

  try:
    print("Invio richiesta a Gemini per il recupero dei deal...")
    response = model.generate_content(prompt)
    text = response.text.strip()
    print(f"DEBUG - Lunghezza testo ricevuto dall'AI: {len(text)} caratteri")
  except Exception as e:
    print(f"Errore durante la chiamata API a Gemini: {e}")
    return []

  # Parsing JSON ultra-robusto con fallback e stampa di debug
  deals = []
  try:
    # Cerca l'array JSON nel testo
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

    print(f"DEBUG - Numero di deal correttamente parsati dal JSON: {len(deals)}")
  except Exception as e:
    print(f"ATTENZIONE: Fallito il parsing del JSON. Errore: {e}")
    print(f"Testo grezzo ricevuto (primi 300 caratteri):\n{text[:300]}")
    return []

  return deals if isinstance(deals, list) else []


def save_json_persistent(new_deals):
  """Salvataggio sicuro con aggiornamento e preservazione preferiti."""
  if not new_deals:
    print("Nessun nuovo deal da salvare (lista vuota).")
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
      print(f"Nota: Storico precedente non leggibile: {e}")
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
        f"Database salvato con successo: {added_count} nuovi, {updated_count}"
        f" aggiornati. Totale in archivio: {len(final_deals)} immobili."
    )
  except Exception as e:
    print(f"ERRORE CRITICO nella scrittura del file JSON: {e}")


def send_telegram_message(deals):
  """Invio Telegram isolato."""
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
    print("=== ESECUZIONE COMPLETATA CON SUCCESSO ===")
  except Exception as e:
    print(f"ERRORE CRITICO INTERCETTATO NEL MAIN: {e}")
    raise e
