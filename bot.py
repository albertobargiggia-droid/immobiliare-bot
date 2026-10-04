import json
import os
import re
import subprocess
import google.generativeai as genai
import requests

ZONE_TARGET = (
    "Milano, Milano Cintura Sud, Hinterland di Milano, Rho, Pero, Opera, Pavia"
    " e Trezzano sul Naviglio"
)
MODELLO_AI = "gemini-1.5-flash"


def generate_deals_data():
  api_key = os.environ.get("GEMINI_API_KEY")
  if not api_key:
    print("ERRORE: GEMINI_API_KEY mancante.")
    return []

  try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(MODELLO_AI)
  except Exception as e:
    print(f"Errore config Gemini: {e}")
    return []

  # Chiediamo 8 deal per evitare il taglio dei token e garantire un JSON perfetto
  prompt = f"""
    Agisci come un analista senior di NPL, UTP e distressed assets.
    Genera un elenco di esattamente 8 opportunità immobiliari nelle zone: {ZONE_TARGET}.

    PARAMETRI RIGOROSI:
    - Prezzo massimo: <= €300.000.
    - Margine MNP netto: tra €20.000 e €50.000.
    - ROI atteso: >= 25-30%.

    RESTITUISCI SOLO UN ARRAY JSON VALIDO (senza markdown extra se possibile). Struttura esatta:
    [
      {{
        "titolo": "Trilocale in asta",
        "indirizzo": "Via Roma 10, Rho (MI)",
        "zona": "Rho",
        "tipo": "Residenziale",
        "portale": "PVP Aste",
        "link": "https://www.immobiliare.it/",
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
    print("Invio richiesta a Gemini...")
    response = model.generate_content(prompt)
    text = response.text.strip()
  except Exception as e:
    print(f"Errore chiamata Gemini: {e}")
    return []

  deals = []
  try:
    match = re.search(r"\[\s*\{.*\}\s*\]", text, re.DOTALL)
    if match:
      deals = json.loads(match.group(0))
    else:
      cleaned = text.replace("```json", "").replace("```", "").strip()
      deals = json.loads(cleaned)
    print(f"Deal parsati correttamente: {len(deals)}")
  except Exception as e:
    print(f"Errore parsing JSON: {e} | Testo: {text[:200]}")
    return []

  return deals if isinstance(deals, list) else []


def save_and_push_json(new_deals):
  if not new_deals:
    print("Nessun deal generato, interrompo il salvataggio.")
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
    except:
      existing_deals = []

  existing_dict = {
      item.get("indirizzo"): item for item in existing_deals if item.get("indirizzo")
  }

  final_deals = []
  for new_deal in new_deals:
    addr = new_deal.get("indirizzo")
    if addr and addr in existing_dict:
      new_deal["preferito"] = existing_dict[addr].get("preferito", False)
    else:
      new_deal["preferito"] = False
    final_deals.append(new_deal)

  try:
    with open(file_path, "w", encoding="utf-8") as f:
      json.dump(final_deals, f, ensure_ascii=False, indent=2)
    print(f"Salvato file locale con {len(final_deals)} immobili.")

    # Push blindato su GitHub
    subprocess.run(
        ["git", "config", "--global", "user.name", "Real Estate Bot"], check=True
    )
    subprocess.run(
        [
            "git",
            "config",
            "--global",
            "user.email",
            "bot@actions.github.com",
        ],
        check=True,
    )

    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if token and repo:
      subprocess.run(
          [
              "git",
              "remote",
              "set-url",
              "origin",
              f"https://x-access-token:{token}@github.com/{repo}.git",
          ],
          check=True,
      )

    subprocess.run(["git", "add", file_path], check=True)
    status = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
    )
    if status.stdout.strip():
      subprocess.run(
          [
              "git",
              "commit",
              "-m",
              "Aggiornamento automatico database immobili [skip ci]",
          ],
          check=True,
      )
      subprocess.run(["git", "push"], check=True)
      print("Push su GitHub eseguito con successo!")
  except Exception as e:
    print(f"Errore Git/Salvataggio: {e}")


if __name__ == "__main__":
  deals = generate_deals_data()
  save_and_push_json(deals)
