import streamlit as st
import json
import os

# Configurazione della pagina in modalità wide per sfruttare tutto lo schermo
st.set_page_config(
    page_title="Radar Immobiliare & NPL - Dashboard", 
    page_icon="🏠", 
    layout="wide"
)

# --- STILE CSS PERSONALIZZATO PER PULIZIA VISIVA ---
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
    .deal-card {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# Titolo principale
st.title("🏠 Radar Immobiliare & NPL – Deal Sourcing Dashboard")
st.markdown("Monitoraggio automatico di ribassi, aste, UTP e opportunità di investimento immobiliare.")

json_path = "data/immobili.json"

if not os.path.exists(json_path):
    st.warning("⚠️ Nessun dato trovato in `data/immobili.json`. Esegui prima il bot di scraping.")
else:
    with open(json_path, "r", encoding="utf-8") as f:
        deals = json.load(f)
    
    if not deals:
        st.info("Il file JSON è attualmente vuoto.")
    else:
        # --- BARRA LATERALE: FILTRI DI RICERCA ---
        st.sidebar.header("🔍 Filtri di Ricerca")
        
        # Filtro Tipologia
        tipologie = ["Tutte"] + list(set(item.get('tipo', 'Generico') for item in deals))
        selected_tipologia = st.sidebar.selectbox("Tipologia", tipologie)
        
        # Filtro Zona
        zone = ["Tutte"] + list(set(item.get('zona', 'N/D') for item in deals))
        selected_zona = st.sidebar.selectbox("Zona", zone)
        
        # Applicazione filtri
        filtered_deals = deals
        if selected_tipologia != "Tutte":
            filtered_deals = [d for d in filtered_deals if d.get('tipo') == selected_tipologia]
        if selected_zona != "Tutte":
            filtered_deals = [d for d in filtered_deals if d.get('zona') == selected_zona]

        # --- PANNELLO METRICHE GENERALI ---
        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        
        tot_annunci = len(filtered_deals)
        prezzo_medio = sum(d.get('prezzo', 0) for d in filtered_deals) / tot_annunci if tot_annunci > 0 else 0
        margine_medio = sum(d.get('margine_mnp', 0) for d in filtered_deals) / tot_annunci if tot_annunci > 0 else 0
        
        m1.metric("Annunci Filtrati", tot_annunci)
        m2.metric("Prezzo Medio", f"€ {prezzo_medio:,.0f}")
        m3.metric("Margine MNP Medio", f"€ {margine_medio:,.0f}")
        m4.metric("Fonti Aggiornate", "GitHub Actions")
        
        st.markdown("---")
        st.subheader("📋 Elenco Opportunità Immobiliari")

        if not filtered_deals:
            st.info("Nessun immobile corrisponde ai filtri selezionati.")
        else:
            for item in filtered_deals:
                with st.container():
                    st.markdown(f"""
                        <div class="deal-card">
                            <h3>🏠 {item.get('titolo', 'Immobile')}</h3>
                            <p><b>📍 Indirizzo:</b> {item.get('indirizzo', 'N/D')} | <b>🌐 Portale:</b> {item.get('portale', 'N/D')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Tipologia:** {item.get('tipo', 'N/D')}")
                        st.write(f"**Zona:** {item.get('zona', 'N/D')}")
                        st.write(f"**Superficie:** {item.get('superficie_mq', 0)} m²")
                    with col2:
                        st.write(f"**Prezzo Richiesto:** € {item.get('prezzo', 0):,}")
                        st.write(f"**Prezzo al m²:** € {item.get('prezzo_mq', 0):,}")
                    with col3:
                        st.write(f"**Delta OMI:** `{item.get('delta_omi_percento', 0)}%`")
                        st.write(f"**Margine MNP:** `€ {item.get('margine_mnp', 0):,}`")
                    
                    link = item.get('link', '#')
                    st.markdown(f"🔗 **[Apri Scheda / Portale Ufficiale]({link})**")
                    st.markdown("---")
