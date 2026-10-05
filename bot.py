import html
import os
import requests


def send_telegram_alert(deal_title, deal_details):
  """Invia una notifica Telegram in modo sicuro e resiliente.

  Utilizza HTML escaping per evitare crash dovuti a caratteri speciali
  (punti, trattini, prezzi) e gestisce timeout ed eccezioni di rete.
  """
  token = os.environ.get("TELEGRAM_BOT_TOKEN")
  chat_id = os.environ.get("TELEGRAM_CHAT_ID")

  # Controllo preventivo: se mancano le credenziali, avvisa ma non blocca lo script
  if not token or not chat_id:
    print(
        "[AVVISO] TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID non configurati."
        " Notifica Telegram saltata."
    )
    return False

  # Sanitizzazione rigorosa dei testi con html.escape per evitare errori di sintassi
  safe_title = html.escape(str(deal_title))
  safe_details = html.escape(str(deal_details))

  # Costruzione del messaggio formattato in HTML sicuro
  message = (
      f"🚨 <b>Nuova Opportunità Immobiliare!</b>\n\n"
      f"🏠 <b>{safe_title}</b>\n"
      f"{safe_details}\n\n"
      f"👉 <i>Accedi alla dashboard Streamlit per i dettagli completi.</i>"
  )

  url = f"https://api.telegram.org/bot{token}/sendMessage"
  payload = {
      "chat_id": chat_id,
      "text": message,
      "parse_mode": "HTML",  # Molto più stabile del Markdown per i dati immobiliari
  }

  try:
    # Impostiamo un timeout di 10 secondi per evitare che lo script si blocchi indefinitamente
    response = requests.post(url, json=payload, timeout=10)

    # Verifica esplicita dello status code HTTP di Telegram
    if response.status_code != 200:
      print(
          f"[ERRORE TELEGRAM] Impossibile inviare la notifica. Codice"
          f" {response.status_code}: {response.text}"
      )
      return False

    print("[SUCCESSO] Notifica Telegram inviata correttamente!")
    return True

  except requests.exceptions.Timeout:
    print(
        "[ERRORE TELEGRAM] Timeout di connessione: Telegram non ha risposto in"
        " tempo."
    )
    return False
  except requests.exceptions.RequestException as e:
    print(
        f"[ERRORE TELEGRAM] Errore di rete durante l'invio:"
        f" {e.__class__.__name__}: {e}"
    )
    return False
  except Exception as e:
    print(f"[ERRORE TELEGRAM] Errore imprevisto:{e}")
    return False


# --- ESEMPIO DI UTILIZZO NEL TUO FLUSSO ---
if __name__ == "__main__":
  # Esempio di test rapido
  titolo_test = "Immobile Test - Via Milano, Rho"
  dettagli_test = (
      "Prezzo base: € 95.000\nSuperficie: 85 mq\nMargine MNP stimato: 24%"
  )

  print("Test invio notifica Telegram...")
  send_telegram_alert(titolo_test, dettagli_test)
