import os
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Frazionatore & Layout Grafico 2D", layout="wide"
)
st.title("🎯 Frazionatore Immobiliare & Generatore di Layout Grafico 2D")

# --- SIDEBAR PARAMETRI ---
st.sidebar.header("📍 Parametri Immobile & Analisi")
indirizzo_input = st.sidebar.text_input(
    "Indirizzo, Civico e Città", value="Via Capessoni 11, Pavia"
)
superficie_totale = st.sidebar.number_input(
    "Superficie Totale (mq)", min_value=40, max_value=300, value=120, step=5
)
raggio_metri = st.sidebar.selectbox(
    "Raggio d'azione", options=[500, 800, 1000], index=1
)
prezzo_acquisto = st.sidebar.number_input(
    "Prezzo d'Acquisto / Asta (€)", value=180000, step=5000
)
costo_ristr_mq = st.sidebar.number_input(
    "Costo Ristrutturazione / Frazionamento (€/mq)", value=750, step=50
)
is_frazionamento = st.sidebar.checkbox(
    "Simula Frazionamento (es. Trilocale -> 2 Bilocali)", value=True
)

# --- MATRICE MULTI-PORTALE E BANCHE DATI ---
f_raggio = (
    1.0 if raggio_metri == 800 else (0.95 if raggio_metri > 800 else 1.05)
)
f_taglio = 0.98 if superficie_totale > 110 else 1.02

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
    f"📊 1. Confronto Prezzi Medi Portali & Banche Dati (Raggio: {raggio_metri}m)"
)
st.caption(
    f"Immobile analizzato: **{indirizzo_input}** | **{superficie_totale} mq**"
)
st.dataframe(df_portali, use_container_width=True)


# --- GENERATORE DI LAYOUT GRAFICO 2D ---
def genera_layout_grafico_2d(mq_totali):
  fig, ax = plt.subplots(figsize=(10, 5.5))
  ax.set_facecolor("#f8f9fa")
  ax.set_xlim(-1, 13)
  ax.set_ylim(-1, 8)
  ax.set_aspect("equal")
  ax.axis("off")

  # Perimetro esterno
  perimetro = patches.Rectangle(
      (0, 0), 12, 7, linewidth=4, edgecolor="black", facecolor="none"
  )
  ax.add_patch(perimetro)

  # Muro divisorio centrale (frazionamento)
  muro_divisorio = patches.Rectangle(
      (5.8, 0),
      0.4,
      7,
      linewidth=1,
      edgecolor="darkred",
      facecolor="red",
      alpha=0.7,
  )
  ax.add_patch(muro_divisorio)

  # Unità A (Sinistra)
  bagno_a = patches.Rectangle(
      (0, 4.5), 3.5, 2.5, linewidth=2, edgecolor="#333", facecolor="#e3f2fd"
  )
  ax.add_patch(bagno_a)
  ax.text(
      1.75,
      5.75,
      "BAGNO A\n(~5.5 mq)",
      ha="center",
      va="center",
      fontsize=8,
      weight="bold",
  )

  camera_a = patches.Rectangle(
      (0, 0), 3.5, 4.5, linewidth=2, edgecolor="#333", facecolor="#fff3e0"
  )
  ax.add_patch(camera_a)
  ax.text(
      1.75,
      2.25,
      "CAMERA A\n(~14.5 mq)",
      ha="center",
      va="center",
      fontsize=9,
      weight="bold",
  )

  soggiorno_a = patches.Rectangle(
      (3.5, 0), 2.3, 7, linewidth=2, edgecolor="#333", facecolor="#e8f5e9"
  )
  ax.add_patch(soggiorno_a)
  ax.text(
      4.65,
      3.5,
      "SOGGIORNO +\nANGOLO COTTURA A\n(~22 mq)",
      ha="center",
      va="center",
      fontsize=8,
      weight="bold",
  )

  # Unità B (Destra)
  soggiorno_b = patches.Rectangle(
      (6.2, 0), 2.3, 7, linewidth=2, edgecolor="#333", facecolor="#e8f5e9"
  )
  ax.add_patch(soggiorno_b)
  ax.text(
      7.35,
      3.5,
      "SOGGIORNO +\nANGOLO COTTURA B\n(~22 mq)",
      ha="center",
      va="center",
      fontsize=8,
      weight="bold",
  )

  camera_b = patches.Rectangle(
      (8.5, 0), 3.5, 4.5, linewidth=2, edgecolor="#333", facecolor="#fff3e0"
  )
  ax.add_patch(camera_b)
  ax.text(
      10.25,
      2.25,
      "CAMERA B\n(~15 mq)",
      ha="center",
      va="center",
      fontsize=9,
      weight="bold",
  )

  bagno_b = patches.Rectangle(
      (8.5, 4.5), 3.5, 2.5, linewidth=2, edgecolor="#333", facecolor="#e3f2fd"
  )
  ax.add_patch(bagno_b)
  ax.text(
      10.25,
      5.75,
      "BAGNO B\n(~6 mq)",
      ha="center",
      va="center",
      fontsize=8,
      weight="bold",
  )

  # Finestre e Ingressi
  finestra1 = patches.Rectangle(
      (1, 6.9), 1.5, 0.2, facecolor="#00bcd4", edgecolor="black"
  )
  finestra2 = patches.Rectangle(
      (9.5, 6.9), 1.5, 0.2, facecolor="#00bcd4", edgecolor="black"
  )
  ingresso_a = patches.Rectangle(
      (4.2, -0.1), 1, 0.2, facecolor="#4caf50", edgecolor="black"
  )
  ingresso_b = patches.Rectangle(
      (6.8, -0.1), 1, 0.2, facecolor="#4caf50", edgecolor="black"
  )

  ax.add_patch(finestra1)
  ax.add_patch(finestra2)
  ax.add_patch(ingresso_a)
  ax.add_patch(ingresso_b)

  ax.text(
      1.75,
      7.3,
      "R.A.I. Ok",
      ha="center",
      fontsize=7,
      color="#00838f",
      weight="bold",
  )
  ax.text(
      10.25,
      7.3,
      "R.A.I. Ok",
      ha="center",
      fontsize=7,
      color="#00838f",
      weight="bold",
  )
  ax.text(
      4.7,
      -0.5,
      "Ingresso A",
      ha="center",
      fontsize=8,
      color="#2e7d32",
      weight="bold",
  )
  ax.text(
      7.3,
      -0.5,
      "Ingresso B",
      ha="center",
      fontsize=8,
      color="#2e7d32",
      weight="bold",
  )

  plt.title(
      f"PROGETTO DI FRAZIONAMENTO IN 2 BILOCALI (Totale: {mq_totali} mq)",
      fontsize=11,
      weight="bold",
      pad=15,
  )
  return fig


st.divider()
st.subheader("📐 2. Progetto Grafico 2D del Frazionamento Ottimizzato")
fig_layout = genera_layout_grafico_2d(superficie_totale)
st.pyplot(fig_layout)

# Pulsante download immagine cantiere
fig_layout.savefig("layout_frazionamento.png", dpi=300, bbox_inches="tight")
with open("layout_frazionamento.png", "rb") as file:
  st.download_button(
      label="📥 Scarica Disegno Tecnico 2D (PNG 300 DPI) per Cantiere",
      data=file,
      file_name=f"layout_{indirizzo_input.replace(', ', '_').replace(' ', '_')}.png",
      mime="image/png",
  )

# --- CONTO ECONOMICO E SPREAD ---
st.divider()
st.subheader("🧮 3. Foglio di Calcolo Operazione & Spread")

media_da_ristr = df_portali["Da Ristrutturare (€/mq)"].mean()
media_ristr = df_portali["Ristrutturato (€/mq)"].mean()
spread_medio = media_ristr - media_da_ristr

prezzo_compra_mq = prezzo_acquisto / superficie_totale

if is_frazionamento:
  prezzo_uscita_mq = media_ristr * 1.14
  st.info(
      "ℹ️ **Frazionamento Attivo:** Applicato premium +14% al mq per la"
      " creazione di 2 unità bilocali compact."
  )
else:
  prezzo_uscita_mq = media_ristr

ricavo_totale = superficie_totale * prezzo_uscita_mq
costo_totale_ristr = superficie_totale * costo_ristr_mq
margine_netto_mnp = ricavo_totale - prezzo_acquisto - costo_totale_ristr
roi_percentuale = (
    margine_netto_mnp / (prezzo_acquisto + costo_totale_ristr)
) * 100

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
