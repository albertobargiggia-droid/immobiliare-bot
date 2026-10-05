import json
import os
import subprocess
import streamlit as st

# Benchmark completi per tutte le località e quartieri target
ZONE_BENCHMARKS = {
    "Milano": {"exit_price_mq": 4800, "costo_ristrutturazione_mq": 600},
    "Milano 3": {"exit_price_mq": 3300, "costo_ristrutturazione_mq": 500},
    "Basiglio": {"exit_price_mq": 3000, "costo_ristrutturazione_mq": 500},
    "Pieve Emanuele": {"exit_price_mq": 2300, "costo_ristrutturazione_mq": 450},
    "Opera": {"exit_price_mq": 2900, "costo_ristrutturazione_mq": 500},
    "Locate Triulzi": {"exit_price_mq": 2200, "costo_ristrutturazione_mq": 450},
    "San Donato Milanese": {
        "exit_price_mq": 3800,
        "costo_ristrutturazione_mq": 600,
    },
    "San Giuliano Milanese": {
        "exit_price_mq": 2800,
        "costo_ristrutturazione_mq": 500,
    },
    "Salvanesco": {"exit_price_mq": 2500, "costo_ristrutturazione_mq": 450},
    "Rogoredo": {"exit_price_mq": 4000, "costo_ristrutturazione_mq": 600},
    "Via Forlanini": {"exit_price_mq": 3800, "costo_ristrutturazione_mq": 600},
    "Scalo Porta Romana": {
        "exit_price_mq": 5800,
        "costo_ristrutturazione_mq": 700,
    },
    "Porta Romana": {"exit_price_mq": 5800, "costo_ristrutturazione_mq": 700},
    "Piazzale Lodi": {"exit_price_mq": 4900, "costo_ristrutturazione_mq": 650},
    "Bocconi": {"exit_price_mq": 5600, "costo_ristrutturazione_mq": 700},
    "Ticinese": {"exit_price_mq": 5700, "costo_ristrutturazione_mq": 700},
    "Navigli": {"exit_price_mq": 5600, "costo_ristrutturazione_mq": 700},
    "Viale Papiniano": {"exit_price_mq": 5600, "costo_ristrutturazione_mq": 700},
    "Via Capecelatro": {"exit_price_mq": 4000, "costo_ristrutturazione_mq": 600},
    "San Siro": {"exit_price_mq": 3900, "costo_ristrutturazione_mq": 600},
    "Porta Genova": {"exit_price_mq": 5700, "costo_ristrutturazione_mq": 700},
    "Corsico": {"exit_price_mq": 2850, "costo_ristrutturazione_mq": 500},
    "Trezzano sul Naviglio": {
        "exit_price_mq": 2800,
        "costo_ristrutturazione_mq": 500,
    },
    "Buccinasco": {"exit_price_mq": 3500, "costo_ristrutturazione_mq": 550},
    "Assago": {"exit_price_mq": 3400, "costo_ristrutturazione_mq": 550},
    "Moirago": {"exit_price_mq": 2500, "costo_ristrutturazione_mq": 450},
    "Via Tabacchi": {"exit_price_mq": 5300, "costo_ristrutturazione_mq": 650},
    "Famagosta": {"exit_price_mq": 3900, "costo_ristrutturazione_mq": 600},
    "Piazza Napoli": {"exit_price_mq": 4900, "costo_ristrutturazione_mq": 650},
    "Barona": {"exit_price_mq": 3800, "costo_ristrutturazione_mq": 600},
    "Rozzano": {"exit_price_mq": 2650, "costo_ristrutturazione_mq": 500},
    "Zibido San Giacomo": {
        "exit_price_mq": 2300,
        "costo_ristrutturazione_mq": 450,
    },
    "San Pietro Cusico": {
        "exit_price_mq": 2150,
        "costo_ristrutturazione_mq": 450,
    },
    "Badile": {"exit_price_mq": 2150, "costo_ristrutturazione_mq": 450},
    "Binasco": {"exit_price_mq": 2200, "costo_ristrutturazione_mq": 450},
    "Noviglio": {"exit_price_mq": 2200, "costo_ristrutturazione_mq": 450},
    "Santa Corinna": {"exit_price_mq": 2100, "costo_ristrutturazione_mq": 450},
    "Vernate": {"exit_price_mq": 2050, "costo_ristrutturazione_mq": 450},
    "Casarile": {"exit_price_mq": 2000, "costo_ristrutturazione_mq": 450},
    "Lacchiarella": {"exit_price_mq": 2350, "costo_ristrutturazione_mq": 450},
    "Siziano": {"exit_price_mq": 2100, "costo_ristrutturazione_mq": 450},
    "Giussago": {"exit_price_mq": 2000, "costo_ristrutturazione_mq": 450},
    "Giovenzano": {"exit_price_mq": 1950, "costo_ristrutturazione_mq": 450},
    "Torriano": {"exit_price_mq": 1950, "costo_ristrutturazione_mq": 450},
    "Pavia": {"exit_price_mq": 2450, "costo_ristrutturazione_mq": 450},
    "Arenzano": {"exit_price_mq": 3300, "costo_ristrutturazione_mq": 550},
    "Settimo Milanese": {
        "exit_price_mq": 2900,
        "costo_ristrutturazione_mq": 500,
    },
    "Cusago": {"exit_price_mq": 3000, "costo_ristrutturazione_mq": 500},
}

st.set_page_config(
    page_title="Pipeline Flipping Immobiliare", layout="wide"
)
st.title("🏗️ Gestione Deal & Inserimento Ibrido")

file_path = "data/immobili.json"


def load_data():
  if os.path.exists(file_path):
    try:
      with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      pass
  return []


deals = load_data()

# --- MODULO DI INSERIMENTO RAPIDO DA MOBILE ---
with st.expander(
    "➕ Incolla Nuovo Annuncio (Metodo Ibrido)", expanded=True
):
  with st.form("form_inserimento_deal"):
    col1, col2 = st.columns(2)
    with col1:
      titolo = st.text_input(
          "Titolo / Tipologia", "Bilocale in Asta / UTP da ristrutturare"
      )
      zona = st.selectbox("Zona Target", list(ZONE_BENCHMARKS.keys()))
      indirizzo = st.text_input(
          "Indirizzo esatto", "Via Ripamonti / Corso Lodi, Milano"
      )
    with col2:
      prezzo = st.number_input(
          "Prezzo Base / Richiesto (€)", value=120000, step=1000
      )
      superficie = st.number_input("Superficie (mq)", value=60, step=1)
      link = st.text_input(
          "Link Reale dell'Annuncio (Copia dal browser)",
          "https://pvp.giustizia.it/...",
      )

    submitted = st.form_submit_button(
        "Calcola Margine e Salva in Pipeline"
    )

    if submitted:
      bench = ZONE_BENCHMARKS.get(
          zona, {"exit_price_mq": 2500, "costo_ristrutturazione_mq": 500}
      )
      est_exit = superficie * bench["exit_price_mq"]
      costo_ristr = superficie * bench["costo_ristrutturazione_mq"]
      margine_mnp = est_exit - prezzo - costo_ristr
      roi_stimato = (margine_mnp / (prezzo + costo_ristr)) * 100

      nuovo_deal = {
          "titolo": titolo,
          "indirizzo": indirizzo,
          "zona": zona,
          "link": link,
          "prezzo": prezzo,
          "superficie_mq": superficie,
          "margine_mnp": int(margine_mnp),
      }

      deals.insert(0, nuovo_deal)
      os.makedirs("data", exist_ok=True)
      with open(file_path, "w", encoding="utf-8") as f:
        json.dump(deals, f, ensure_ascii=False, indent=2)

      # Sincronizzazione automatica con GitHub
      try:
        token = os.environ.get("GITHUB_TOKEN") or st.secrets.get(
            "GITHUB_TOKEN", ""
        )
        repo = os.environ.get("GITHUB_REPOSITORY") or st.secrets.get(
            "GITHUB_REPOSITORY", ""
        )
        if token and repo:
          subprocess.run(["git", "config", "--global", "user.name", "Bot"])
          subprocess.run([
              "git",
              "config",
              "--global",
              "user.email",
              "bot@actions.com",
          ])
          subprocess.run([
              "git",
              "remote",
              "set-url",
              "origin",
              f"https://x-access-token:{token}@github.com/{repo}.git",
          ])
          subprocess.run(["git", "add", file_path])
          subprocess.run([
              "git",
              "commit",
              "-m",
              "Aggiunto nuovo deal via Streamlit [skip ci]",
          ])
          subprocess.run(["git", "push"])
          st.success(
              f"✅ Salvato e sincronizzato! Margine MNP stimato: €{int(margine_mnp):,} |"
              f" ROI: {roi_stimato:.1f}%"
          )
        else:
          st.success(
              f"✅ Salvato localmente! Margine MNP stimato: €{int(margine_mnp):,}"
              f" | ROI: {roi_stimato:.1f}%"
          )
      except Exception as e:
        st.success(
            f"✅ Salvato localmente (Git Push non attivo: {e}). Margine MNP:"
            f" €{int(margine_mnp):,}"
        )

# --- VISUALIZZAZIONE LISTA ATTUALE ---
st.subheader("📋 Pipeline Opportunità Monitorate")
if deals:
  for i, d in enumerate(deals):
    with st.container():
      st.markdown(
          f"### {i+1}. {d.get('titolo')} — `{d.get('zona')}`"
      )
      st.write(
          f"📍 **Indirizzo:** {d.get('indirizzo')} | 💰 **Prezzo:**"
          f" €{d.get('prezzo'):,} | 📐 **Sup:** {d.get('superficie_mq')} mq | 📈"
          f" **Margine MNP:** €{d.get('margine_mnp'):,}"
      )
      st.markdown(
          f"🔗 **[Apri Link Ufficiale dell'Annuncio]({d.get('link')})**"
      )
      st.divider()
else:
  st.info("Nessun immobile in pipeline. Incollane uno nuovo dal form sopra!")
