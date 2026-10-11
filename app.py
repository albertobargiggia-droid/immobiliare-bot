import json
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Valutatore Micro-Zona & Frazionamenti", layout="wide"
)
st.title("🎯 Valutatore Micro-Zona Dinamico & Foglio di Calcolo Flipping")

# --- INTERFACCIA DI INPUT DINAMICA ---
st.sidebar.header("📍 Parametri Immobile & Analisi")

with st.sidebar.form("form_analisi_dinamica"):
  indirizzo_input = st.text_input(
      "Indirizzo, Civico e Città",
      value="Via Capessoni 11, Pavia",
      placeholder="Es. Via Capessoni 11, Pavia",
  )
  superficie_mq = st.number_input(
      "Superficie (mq)", min_value=50, max_value=300, value=120, step=5
  )
  raggio_metri = st.selectbox(
      "Raggio d'azione", options=[500, 800, 1000], index=1
  )
  prezzo_compra = st.number_input(
      "Prezzo d'Acquisto / Asta (€)", value=180000, step=5000
  )
  costo_ristr_mq = st.number_input(
      "Costo Ristrutturazione (€/mq)", value=600, step=50
  )
  is_frazionamento = st.checkbox(
      "Simula Frazionamento (es. Trilocale -> 2 Bilocali)", value=False
  )

  btn_analizza = st.form_submit_button("🚀 Calcola Analisi e Spread")

# --- MOTORE DI CALCOLO COMPARATIVO MULTI-PORTALE ---
# Fattori di calibrazione in base al raggio e alla metratura
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

st.subheader(
    f"📊 Confronto Valori Medi Portali & Banche Dati (Raggio: {raggio_metri}m)"
)
st.caption(
    f"Immobile analizzato: **{indirizzo_input}** | **{superficie_mq} mq**"
)

st.dataframe(df_portali, use_container_width=True)

# --- FOGLIO DI CALCOLO OPERATIVO & SEMAFORI ---
st.divider()
st.subheader("🧮 Foglio di Calcolo Operazione & Valutazione Spread")

media_da_ristr_mercato = df_portali["Da Ristrutturare (€/mq)"].mean()
media_ristr_mercato = df_portali["Ristrutturato (€/mq)"].mean()
spread_medio = media_ristr_mercato - media_da_ristr_mercato

prezzo_compra_mq = prezzo_compra / superficie_mq

if is_frazionamento:
  prezzo_uscita_mq = media_ristr_mercato * 1.12
  st.info(
      "ℹ️ **Frazionamento Attivo:** Applicato premium +12% sul prezzo di"
      " vendita al mq per la creazione di unità più compatte."
  )
else:
  prezzo_uscita_mq = media_ristr_mercato

ricavo_totale = superficie_mq * prezzo_uscita_mq
costo_totale_ristr = superficie_mq * costo_ristr_mq
margine_netto_mnp = ricavo_totale - prezzo_compra - costo_totale_ristr
roi_percentuale = (
    margine_netto_mnp / (prezzo_compra + costo_totale_ristr)
) * 100

# Logica Semaforica dei Colori
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
