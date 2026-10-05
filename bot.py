import html
import json
import os
import requests

# Matrice completa di riferimento reale per tutte le località e quartieri target (Bilocali: Prezzi al mq)
ZONE_BENCHMARKS = {
    "Milano": {
        "omi_min": 2500,
        "omi_max": 4500,
        "da_ristrutturare_mq": 3200,
        "exit_price_mq": 4800,
    },
    "Milano 3": {
        "omi_min": 2200,
        "omi_max": 3200,
        "da_ristrutturare_mq": 2200,
        "exit_price_mq": 3300,
    },
    "Basiglio": {
        "omi_min": 2000,
        "omi_max": 3000,
        "da_ristrutturare_mq": 2000,
        "exit_price_mq": 3000,
    },
    "Pieve Emanuele": {
        "omi_min": 1400,
        "omi_max": 2100,
        "da_ristrutturare_mq": 1500,
        "exit_price_mq": 2300,
    },
    "Opera": {
        "omi_min": 1400,
        "omi_max": 1950,
        "da_ristrutturare_mq": 2000,
        "exit_price_mq": 2900,
    },
    "Locate Triulzi": {
        "omi_min": 1300,
        "omi_max": 2000,
        "da_ristrutturare_mq": 1400,
        "exit_price_mq": 2200,
    },
    "San Donato Milanese": {
        "omi_min": 2400,
        "omi_max": 3600,
        "da_ristrutturare_mq": 2600,
        "exit_price_mq": 3800,
    },
    "San Giuliano Milanese": {
        "omi_min": 1700,
        "omi_max": 2600,
        "da_ristrutturare_mq": 1900,
        "exit_price_mq": 2800,
    },
    "Salvanesco": {
        "omi_min": 1500,
        "omi_max": 2300,
        "da_ristrutturare_mq": 1700,
        "exit_price_mq": 2500,
    },
    "Rogoredo": {
        "omi_min": 2500,
        "omi_max": 3800,
        "da_ristrutturare_mq": 2800,
        "exit_price_mq": 4000,
    },
    "Via Forlanini": {
        "omi_min": 2200,
        "omi_max": 3600,
        "da_ristrutturare_mq": 2600,
        "exit_price_mq": 3800,
    },
    "Scalo Porta Romana": {
        "omi_min": 3500,
        "omi_max": 5800,
        "da_ristrutturare_mq": 4200,
        "exit_price_mq": 5800,
    },
    "Porta Romana": {
        "omi_min": 3500,
        "omi_max": 5800,
        "da_ristrutturare_mq": 4200,
        "exit_price_mq": 5800,
    },
    "Piazzale Lodi": {
        "omi_min": 3000,
        "omi_max": 4800,
        "da_ristrutturare_mq": 3500,
        "exit_price_mq": 4900,
    },
    "Bocconi": {
        "omi_min": 3600,
        "omi_max": 5500,
        "da_ristrutturare_mq": 4000,
        "exit_price_mq": 5600,
    },
    "Ticinese": {
        "omi_min": 3700,
        "omi_max": 5600,
        "da_ristrutturare_mq": 4100,
        "exit_price_mq": 5700,
    },
    "Navigli": {
        "omi_min": 3600,
        "omi_max": 5500,
        "da_ristrutturare_mq": 4000,
        "exit_price_mq": 5600,
    },
    "Viale Papiniano": {
        "omi_min": 3600,
        "omi_max": 5500,
        "da_ristrutturare_mq": 4000,
        "exit_price_mq": 5600,
    },
    "Via Capecelatro": {
        "omi_min": 2500,
        "omi_max": 3800,
        "da_ristrutturare_mq": 2800,
        "exit_price_mq": 4000,
    },
    "San Siro": {
        "omi_min": 2400,
        "omi_max": 3700,
        "da_ristrutturare_mq": 2700,
        "exit_price_mq": 3900,
    },
    "Porta Genova": {
        "omi_min": 3700,
        "omi_max": 5600,
        "da_ristrutturare_mq": 4100,
        "exit_price_mq": 5700,
    },
    "Corsico": {
        "omi_min": 1700,
        "omi_max": 2600,
        "da_ristrutturare_mq": 1900,
        "exit_price_mq": 2850,
    },
    "Trezzano sul Naviglio": {
        "omi_min": 1500,
        "omi_max": 2100,
        "da_ristrutturare_mq": 1900,
        "exit_price_mq": 2800,
    },
    "Buccinasco": {
        "omi_min": 2100,
        "omi_max": 3200,
        "da_ristrutturare_mq": 2400,
        "exit_price_mq": 3500,
    },
    "Assago": {
        "omi_min": 2000,
        "omi_max": 3100,
        "da_ristrutturare_mq": 2300,
        "exit_price_mq": 3400,
    },
    "Moirago": {
        "omi_min": 1500,
        "omi_max": 2300,
        "da_ristrutturare_mq": 1700,
        "exit_price_mq": 2500,
    },
    "Via Tabacchi": {
        "omi_min": 3400,
        "omi_max": 5200,
        "da_ristrutturare_mq": 3800,
        "exit_price_mq": 5300,
    },
    "Famagosta": {
        "omi_min": 2400,
        "omi_max": 3700,
        "da_ristrutturare_mq": 2700,
        "exit_price_mq": 3900,
    },
    "Piazza Napoli": {
        "omi_min": 3000,
        "omi_max": 4800,
        "da_ristrutturare_mq": 3500,
        "exit_price_mq": 4900,
    },
    "Barona": {
        "omi_min": 2300,
        "omi_max": 3600,
        "da_ristrutturare_mq": 2600,
        "exit_price_mq": 3800,
    },
    "Rozzano": {
        "omi_min": 1400,
        "omi_max": 1900,
        "da_ristrutturare_mq": 1750,
        "exit_price_mq": 2650,
    },
    "Zibido San Giacomo": {
        "omi_min": 1300,
        "omi_max": 2100,
        "da_ristrutturare_mq": 1500,
        "exit_price_mq": 2300,
    },
    "San Pietro Cusico": {
        "omi_min": 1200,
        "omi_max": 1950,
        "da_ristrutturare_mq": 1400,
        "exit_price_mq": 2150,
    },
    "Badile": {
        "omi_min": 1200,
        "omi_max": 1950,
        "da_ristrutturare_mq": 1400,
        "exit_price_mq": 2150,
    },
    "Binasco": {
        "omi_min": 1100,
        "omi_max": 1550,
        "da_ristrutturare_mq": 1350,
        "exit_price_mq": 2200,
    },
    "Noviglio": {
        "omi_min": 1200,
        "omi_max": 2000,
        "da_ristrutturare_mq": 1400,
        "exit_price_mq": 2200,
    },
    "Santa Corinna": {
        "omi_min": 1150,
        "omi_max": 1900,
        "da_ristrutturare_mq": 1350,
        "exit_price_mq": 2100,
    },
    "Vernate": {
        "omi_min": 1100,
        "omi_max": 1850,
        "da_ristrutturare_mq": 1300,
        "exit_price_mq": 2050,
    },
    "Casarile": {
        "omi_min": 1050,
        "omi_max": 1800,
        "da_ristrutturare_mq": 1250,
        "exit_price_mq": 2000,
    },
    "Lacchiarella": {
        "omi_min": 1200,
        "omi_max": 1650,
        "da_ristrutturare_mq": 1450,
        "exit_price_mq": 2350,
    },
    "Siziano": {
        "omi_min": 1050,
        "omi_max": 1500,
        "da_ristrutturare_mq": 1300,
        "exit_price_mq": 2100,
    },
    "Giussago": {
        "omi_min": 1050,
        "omi_max": 1800,
        "da_ristrutturare_mq": 1250,
        "exit_price_mq": 2000,
    },
    "Giovenzano": {
        "omi_min": 1000,
        "omi_max": 1750,
        "da_ristrutturare_mq": 1200,
        "exit_price_mq": 1950,
    },
    "Torriano": {
        "omi_min": 1000,
        "omi_max": 1750,
        "da_ristrutturare_mq": 1200,
        "exit_price_mq": 1950,
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
    "Settimo Milanese": {
        "omi_min": 1700,
        "omi_max": 2600,
        "da_ristrutturare_mq": 1950,
        "exit_price_mq": 2900,
    },
    "Cusago": {
        "omi_min": 1800,
        "omi_max": 2700,
        "da_ristrutturare_mq": 2000,
        "exit_price_mq": 3000,
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
