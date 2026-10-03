import json
import os
import pandas as pd
import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Radar Immobiliare AI", page_icon="🏡", layout="wide"
)

st.title("🏡 Radar Immobiliare & NPL - Dashboard")
st.markdown(
    "Monitoraggio automatico di ribassi, aste, UTP e NPL elaborato tramite intelligenza artificiale."
)


# Funzione per caricare i dati (supporta JSON o CSV salvati dal tuo scraper)
@st.cache_data(ttl=600)  # Aggiorna la cache ogni 10 minuti
def load_data():
    # Percorso del file dati generato dal tuo scraper su GitHub
    data_path = "data/immobili.json"  # Modifica il percorso se salvi in un altro file o formato (es. csv)

    if os.path.exists(data_path):
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Errore nella lettura del file dati: {e}")
            return []
    return []


data = load_data()

if not data:
    st.info(
        "Nessun dato trovato. Assicurati che lo scraper abbia eseguito almeno un salvataggio nel percorso corretto (es. `data/immobili.json`)."
    )
else:
    # Convertiamo in DataFrame Pandas per facilitare i filtri
    df = pd.DataFrame(data)

    # --- BARRA LATERALE: FILTRI ---
    st.sidebar.header("🔍 Filtri di Ricerca")

    # Filtro Tipologia (Aste, UTP, NPL, Ribassi, ecc.)
    if "tipo" in df.columns:
        tipologie = ["Tutte"] + list(df["tipo"].unique())
        selected_tipo = st.sidebar.selectbox("Tipologia", tipologie)
        if selected_tipo != "Tutte":
            df = df[df["tipo"] == selected_tipo]

    # Filtro Testuale (Zona o Parole chiave)
    search_query = st.sidebar.text_input("Cerca per zona o titolo")
    if search_query and "titolo" in df.columns:
        df = df[
            df["titolo"].str.contains(search_query, case=False, na=False)
            | df.get("zona", pd.Series([False] * len(df)))
            .astype(str)
            .str.contains(search_query, case=False, na=False)
        ]

    # --- METRICHE PRINCIPALI ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Annunci Filtrati", len(df))
    if "prezzo" in df.columns:
        # Pulisci e calcola il prezzo medio se numerico
        try:
            prezzo_medio = df["prezzo"].astype(float).mean()
            col2.metric("Prezzo Medio", f"€ {prezzo_medio:,.0f}")
        except:
            col2.metric("Prezzo Medio", "N/D")
    col3.metric(
        "Fonti Aggiornate", "GitHub Actions"
    )  # o data dell'ultimo aggiornamento

    st.markdown("---")

    # --- VISUALIZZAZIONE DATI ---
    st.subheader("📋 Elenco Opportunità Immobiliari")

    for index, row in df.iterrows():
        titolo = row.get("titolo", "Immobile senza titolo")
        prezzo = row.get("prezzo", "N/D")
        tipo = row.get("tipo", "Generico")
        ribasso = row.get("ribasso", "N/D")
        analisi = row.get(
            "analisi",
            "Nessuna analisi IA disponibile per questo immobile.",
        )
        link = row.get("link", "#")
        data_rilevazione = row.get("data", "N/D")

        with st.expander(
            f"📌 [{tipo}] {titolo} — Prezzo: € {prezzo} (Ribasso/Stima: {ribasso})"
        ):
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown(f"**Analisi Gemini AI:**\n{analisi}")
                st.write(f"📅 Rilevato il: {data_rilevazione}")
            with c2:
                if link and link != "#":
                    st.markdown(
                        f"[🔗 Apri Link Originale dell'Annuncio]({link})",
                        unsafe_allow_html=True,
                    )
                else:
                    st.write("Link non disponibile")

            # Se hai uno storico dei prezzi per singolo immobile puoi mostrarlo qui sotto
            if "storico" in row and row["storico"]:
                st.markdown("---")
                st.write("**Storico variazioni prezzo:**")
                st.line_chart(pd.DataFrame(row["storico"]))
