import html
import json
import os
import requests

# Matrice completa di riferimento reale per tutte le zone e quartieri target (Bilocali: Prezzi al mq)
ZONE_BENCHMARKS = {
    "Milano (Generale)": {
        "omi_min": 2500,
        "omi_max": 4500,
        "da_ristrutturare_mq": 3200,
        "exit_price_mq": 4800,
    },
    "Porta Romana / Scalo Porta Romana": {
        "omi_min": 3500,
        "omi_max": 5800,
        "da_ristrutturare_mq": 4200,
        "exit_price_mq": 5800,
    },
    "Viale Forlanini": {
        "omi_min": 2200,
        "omi_max": 3600,
        "da_ristrutturare_mq": 2600,
        "exit_price_mq": 3800,
    },
    "Milano Cintura Sud": {
        "omi_min": 2200,
        "omi_max": 3400,
        "da_ristrutturare_mq": 2800,
        "exit_price_mq": 4100,
    },
    "Hinterland di Milano": {
        "omi_min": 1500,
        "omi_max": 2200,
        "da_ristrutturare_mq": 1900,
        "exit_price_mq": 2850,
    },
    "Rho": {
        "omi_min": 1300,
        "omi_max": 1850,
        "da_ristrutturare_mq": 1800,
        "exit_price_mq": 2700,
    },
    "Pero": {
        "omi_min": 1600,
        "omi_max": 2300,
        "da_ristrutturare_mq": 2100,
        "exit_price_mq": 3150,
    },
    "Trezzano sul Naviglio": {
        "omi_min": 1500,
        "omi_max": 2100,
        "da_ristrutturare_mq": 1900,
        "exit_price_mq": 2800,
    },
    "Opera": {
        "omi_min": 1400,
        "omi_max": 1950,
        "da_ristrutturare_mq": 2000,
        "exit_price_mq": 2900,
    },
    "Rozzano": {
        "omi_min": 1400,
        "omi_max": 1900,
        "da_ristrutturare_mq": 1750,
        "exit_price_mq": 2650,
    },
    "Lacchiarella": {
        "omi_min": 1200,
        "omi_max": 1650,
        "da_ristrutturare_mq": 1450,
        "exit_price_mq": 2350,
    },
    "Binasco": {
        "omi_min": 1100,
        "omi_max": 1550,
        "da_ristrutturare_mq": 1350,
        "exit_price_mq": 2200,
    },
    "Sizziano": {
        "omi_min": 1050,
        "omi_max": 1500,
        "da_ristrutturare_mq": 1300,
        "exit_price_mq": 2100,
    },
    "Pavia": {
        "omi_min": 1150,
        "omi_max": 1700,
        "da_ristrutturare_mq": 1500,
        "exit_price_mq": 2450,
    },
    "Arenzano": {
        "omi_min": 1800,
        "omi_max": 3000,
        "da_ristrutturare_mq": 2200,
        "exit_price_mq": 3300,
    },
}


def send_telegram_summary(deals):
  token = os.environ.get("TELEGRAM_BOT_TOKEN")
  chat_id = os.environ.get("TELEGRAM_CHAT_ID")
  streamlit_url = os.environ.get(
      "STREAMLIT_URL", "https://share.streamlit.io/"
  )

  if not token or not chat_id:
    print("[AVVISO] Token o Chat ID Telegram mancanti.")
    return False

  if not deals:
    print("[AVVISO] Nessun immobile nel database.")
    return False

  count = len(deals)
  summary_lines = [
      "🚨 <b>Pipeline Immobili - Sistema Ibrido</b>",
      f"Monitorate <b>{count} opportunità</b> attive.\n",
  ]

  for d in deals[:5]:
    t = html.escape(str(d.get("titolo", "Immobile")))
    z = html.escape(str(d.get("zona", "Altra zona")))
    p = d.get("prezzo", 0)
    sup = d.get("superficie_mq", 60)

    bench = ZONE_BENCHMARKS.get(z, {"exit_price_mq": 2500})
    est_exit = sup * bench["exit_price_mq"]
    costo_ristrutturazione = sup * 500
    margine_stimato = est_exit - p - costo_ristrutturazione

    link = html.escape(str(d.get("link", streamlit_url)))

    summary_lines.append(
        f"• <b><a href='{link}'>{t}</a></b> ({z})\n  Prezzo: €{p:,} | Margine"
        f" MNP stimato: €{margine_stimato:,}"
    )

  if count > 5:
    summary_lines.append(f"\n<i>...e altri {count - 5} immobili in lista.</i>")

  summary_lines.append(
      f"\n👉 <b><a href='{streamlit_url}'>Accedi alla dashboard"
      " Streamlit</a></b> per gestire la pipeline."
  )
  message = "\n".join(summary_lines)

  url = f"https://api.telegram.org/bot{token}/sendMessage"
  payload = {
      "chat_id": chat_id,
      "text": message,
      "parse_mode": "HTML",
      "disable_web_page_preview": True,
  }

  try:
    response = requests.post(url, json=payload, timeout=10)
    if response.status_code != 200:
      print(f"[ERRORE TELEGRAM] Codice {response.status_code}: {response.text}")
      return False
    print("[SUCCESSO] Notifica Telegram inviata correttamente!")
    return True
  except Exception as e:
    print(f"[ERRORE TELEGRAM] Errore di rete: {e}")
    return False


def load_deals():
  file_path = "data/immobili.json"
  if os.path.exists(file_path):
    try:
      with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
    except Exception as e:
      print(f"Errore lettura JSON: {e}")
  return []


if __name__ == "__main__":
  deals = load_deals()
  send_telegram_summary(deals)
