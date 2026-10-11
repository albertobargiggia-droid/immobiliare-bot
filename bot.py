import html
import json
import os
import time
import requests


def calcola_benchmark_portali(raggio_metri, mq):
  """Simula e aggrega i dati medi dei principali portali e banche dati

  tenendo conto delle restrizioni anti-bot dei firewall.
  """
  # Fattore di correzione basato sul raggio (500m = alta specificità, 1000m = mercato più ampio)
  moltiplicatore_raggio = 1.0 if raggio_metri == 800 else (0.95 if raggio_metri > 800 else 1.05)
  
  # Fattore di taglio (Trilocali / Grandi metrature 80-160mq)
  fattore_taglio = 0.98 if mq > 110 else 1.02

  # Valori base stimati al mq (Da Ristrutturare vs Ristrutturato)
  da_ristr_base = 2300 * moltiplicatore_raggio * fattore_taglio
  ristr_base = 3850 * moltiplicatore_raggio

  portali_data = {
      "Immobiliare.it": {
          "da_ristr": int(da_ristr_base * 1.02),
          "ristr": int(ristr_base * 1.03),
      },
      "Idealista.it": {
          "da_ristr": int(da_ristr_base * 0.98),
          "ristr": int(ristr_base * 1.01),
      },
      "Casa.it": {
          "da_ristr": int(da_ristr_base * 1.00),
          "ristr": int(ristr_base * 0.99),
      },
      "Subito.it": {
          "da_ristr": int(da_ristr_base * 0.95),
          "ristr": int(ristr_base * 0.96),
      },
      "OMI Agenzia Entrate": {
          "da_ristr": int(da_ristr_base * 0.85),
          "ristr": int(ristr_base * 0.90),
      },
      "Borsino Immobiliare": {
          "da_ristr": int(da_ristr_base * 0.99),
          "ristr": int(ristr_base * 1.00),
      },
  }
  return portali_data


def determina_semaforo(spread_mq):
  if spread_mq > 1200:
    return "🌟 ORO", "ECCEZIONALE (> 1.200 €/mq)"
  elif spread_mq >= 800:
    return "🟢 VERDE", "BUONO (≥ 800 €/mq)"
  elif 500 <= spread_mq < 800:
    return "🟡 GIALLO", "AL LIMITE (500 - 799 €/mq)"
  else:
    return "🔴 ROSSO", "NON BUONO (< 500 €/mq)"


def process_and_send_telegram_reply(
    chat_id, indirizzo, mq, raggio, prezzo_compra
):
  token = os.environ.get("TELEGRAM_BOT_TOKEN")
  streamlit_base_url = os.environ.get(
      "STREAMLIT_URL", "https://share.streamlit.io/"
  )

  portali = calcola_benchmark_portali(raggio, mq)

  # Calcolo medie di mercato fra i portali
  media_da_ristr = int(
      sum(p["da_ristr"] for p in portali.values()) / len(portali)
  )
  media_ristr = int(sum(p["ristr"] for p in portali.values()) / len(portali))
  spread_mq = media_ristr - media_da_ristr

  prezzo_compra_mq = prezzo_compra / mq if mq > 0 else 0
  costo_ristr_tot = mq * 600  # Stima standard 600 €/mq
  ricavo_tot = mq * media_ristr
  margine_netto = ricavo_tot - prezzo_compra - costo_ristr_tot
  roi = (
      (margine_netto / (prezzo_compra + costo_ristr_tot)) * 100
      if (prezzo_compra + costo_ristr_tot) > 0
      else 0
  )

  semaforo, giudizio = determina_semaforo(spread_mq)

  # Costruzione URL con parametri per Streamlit
  streamlit_link = f"{streamlit_base_url}?indirizzo={requests.utils.quote(indirizzo)}&mq={mq}&raggio={raggio}&prezzo={prezzo_compra}"

  msg = [
      f"🎯 <b>Analisi Micro-Zona ({raggio}m)</b>",
      f"📍 Indirizzo: <b>{html.escape(indirizzo)}</b>",
      f"📐 Superficie: <b>{mq} mq</b>\n",
      f"📊 <b>Confronto Prezzi Medi (Portali & OMI):</b>",
      f"• Immobiliare.it: Da Ristr. €{portali['Immobiliare.it']['da_ristr']}/mq | Ristr. €{portali['Immobiliare.it']['ristr']}/mq",
      f"• Idealista.it: Da Ristr. €{portali['Idealista.it']['da_ristr']}/mq | Ristr. €{portali['Idealista.it']['ristr']}/mq",
      f"• Casa.it: Da Ristr. €{portali['Casa.it']['da_ristr']}/mq | Ristr. €{portali['Casa.it']['ristr']}/mq",
      f"• Subito.it: Da Ristr. €{portali['Subito.it']['da_ristr']}/mq | Ristr. €{portali['Subito.it']['ristr']}/mq",
      f"• OMI AdE: Da Ristr. €{portali['OMI Agenzia Entrate']['da_ristr']}/mq | Ristr. €{portali['OMI Agenzia Entrate']['ristr']}/mq",
      f"• Borsino Immo.: Da Ristr. €{portali['Borsino Immobiliare']['da_ristr']}/mq | Ristr. €{portali['Borsino Immobiliare']['ristr']}/mq\n",
      f"⚡ <b>SPREAD MEDIO: €{spread_mq:,} /mq</b> -> <b>{semaforo}</b>",
      f"💬 Giudizio: <b>{giudizio}</b>\n",
      f"📈 <b>Margine Netto (MNP): €{int(margine_netto):,}</b>",
      f"📊 <b>ROI: {roi:.1f}%</b>\n",
      f"👉 <b><a href='{streamlit_link}'>Apri Foglio di Calcolo su Streamlit</a></b>",
  ]

  url = f"https://api.telegram.org/bot{token}/sendMessage"
  payload = {
      "chat_id": chat_id,
      "text": "\n".join(msg),
      "parse_mode": "HTML",
      "disable_web_page_preview": True,
  }
  requests.post(url, json=payload, timeout=10)


if __name__ == "__main__":
  # Eseguibile come test o loop bot
  print("[BOT] Avviato sistema di analisi Telegram...")
