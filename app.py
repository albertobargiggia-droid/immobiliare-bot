import json
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Valutatore Micro-Zona & Frazionamenti", layout="wide"
)
st.title("🎯 Valutatore Micro-Zona Dinamico & Foglio di Calcolo Flipping")

# --- LETTURA PARAMETRI DA URL (PASSATI DA TELEGRAM) O DEFAULT ---
query_params = st.query_params
default_indirizzo = query_params.get("indirizzo", "Via Ripamonti 88, Milano")
default_mq = int(query_params.get("mq", 120))
default_raggio = int(query_params.get("raggio", 800))
default_prezzo = float(query_params.get("prezzo", 220000))

# --- SIDEBAR / FINESTRA DI MODIFICA PARAMETRI ---
st.sidebar.header("📍 Parametri Immobile & Analisi")
indirizzo_civico = st.sidebar.text_input(
    "Indirizzo Civico e Città", value=default_indirizzo
)

col_r1, col_r2 = st.sidebar.columns(2)
with col_r1:
  superficie_mq = st.number_input(
      "Superficie (mq)",
      min_value=50,
      max_value=250,
      value=default_mq,
      step=5,
      help="Modificabile liberamente (es. Trilocale 120 mq)",
  )
with col_r2:
  raggio_metri = st.selectbox(
      "Raggio d'azione", options=[500, 800, 1000], index=[500, 800, 1000].index(default_raggio) if default_raggio in [500, 800, 1000] else 1
  )

prezzo_compra = st.sidebar.number_input(
    "Prezzo d'Acquisto / Asta (€)", value=default_prezzo, step=5000
)
costo_ristr_mq = st.sidebar.number_input(
    "Costo Ristrutturazione (€/mq)", value=600, step=50
)
is_frazionamento = st.sidebar.checkbox(
    "Simula Frazionamento (es. Trilocale -> 2 Bilocali)", value=False
)

# --- MATRICE MULTI-PORTALE E DATI COMPARATIVI ---
st.subheader(
    f"📊 Confronto Valori Medi Portali & Banche Dati (Raggio: {raggio_metri}m)"
)
st.caption(f"Immobile analizzato: **{indirizzo_civico}** | **{superficie_mq} mq**")

# Simulatore di benchmark calibrato su raggio e mq
f_raggio = 1.0 if raggio_metri == 800 else (0.95 if raggio_metri > 800 else 1.05)
f_taglio = 0.98 if superficie_mq > 110 else 1.02

base_da_ristr = int(2300 * f_raggio * f_taglio)
base_ristr = int(3850 * f_raggio)

data_portali = {
    "Fonte / Piattaforma": [
        "Immobiliare.it",
        "Idealista.it",
        "Casa.it",
        "Subito.it",
        "OMI Agenzia Entrate",
        "Borsino Immobiliare",
    ],
    "Da Ristrutturare (€/mq)": [
        int(base_da_ristr * 1.02),
        int(base_da_ristr * 0.98),
        int(base_da_ristr * 1.00),
        int(base_da_ristr * 0.95),
        int(base_da_ristr * 0.85),
        int(base_da_ristr * 0.99),
    ],
    "Ristrutturato (€/mq)": [
        int(base_ristr * 1.03),
        int(base_ristr * 1.01),
        int(base_ristr * 0.99),
        int(base_ristr * 0.96),
        int(base_ristr * 0.90),
        int(base_ristr * 1.00),
    ],
}

df_portali = pd.DataFrame(data_portali)
df_portali["Spread (€/mq)"] = (
    df_portali["Ristrutturato (€/mq)"] - df_portali["Da Ristrutturare (€/mq)"]
)

st.dataframe(df_portali, use_container_width=True)

# --- FOGLIO DI CALCOLO OPERATIVO & SEMAFORI ---
st.divider()
st.subheader("🧮 Foglio di Calcolo & Valutazione Spread")

media_da_ristr_mercato = df_portali["Da Ristrutturare (€/mq)"].mean()
media_ristr_mercato = df_portali["Ristrutturato (€/mq)"].mean()
spread_medio = media_ristr_mercato - media_da_ristr_mercato

prezzo_compra_mq = prezzo_compra / superficie_mq

if is_frazionamento:
  prezzo_uscita_mq = media_ristr_mercato * 1.12
  st.info(
      "ℹ️ **Frazionamento Attivo:** Applicato premium +12% sul prezzo di"
      " vendita al mq per la creazione di unità più piccole."
  )
else:
  prezzo_uscita_mq = media_ristr_mercato

ricavo_totale = superficie_mq * prezzo_uscita_mq
costo_totale_ristr = superficie_mq * costo_ristr_mq
margine_netto_mnp = ricavo_totale - prezzo_compra - costo_totale_ristr
roi_percentuale = (
    margine_netto_mnp / (prezzo_compra + costo_totale_ristr)
) * 100

# Semafori Spread
if spread_medio > 1200:
  semaforo_box = "🌟 **SPREAD ORO / ECCEZIONALE** (> 1.200 €/mq)"
  st_color = st.success
elif spread_medio >= 800:
  semaforo_box = "🟢 **SPREAD VERDE / BUONO** (≥ 800 €/mq)"
  st_color = st.success
elif 500 <= spread_medio < 800:
  semaforo_box = "🟡 **SPREAD GIALLO / AL LIMITE** (500 - 799 €/mq)"
  st_color = st.warning
else:
  semaforo_box = "🔴 **SPREAD ROSSO / NON BUONO** (< 500 €/mq)"
  st_color = st.error

c1, c2, c3, c4 = st.columns(4)
c1.metric("Prezzo Acquisto / mq", f"€{int(prezzo_compra_mq):,} /mq")
c2.metric("Spread Medio al mq", f"€{int(spread_medio):,} /mq")
c3.metric("Margine Netto (MNP)", f"€{int(margine_netto_mnp):,}")
c4.metric("ROI Stimato", f"{roi_percentuale:.1f}%")

st_color(f"### ESITO OPERAZIONE: {semaforo_box}")
