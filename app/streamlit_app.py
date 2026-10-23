from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="NYC Taxi Demand",
    page_icon="🚕",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent.parent
PAGES_DIR = Path(__file__).resolve().parent / "páginas"


pagina_pronostico = st.Page(
    str(PAGES_DIR / "1_Pronostico.py"),
    title="Pronóstico",
    icon="🚕",
    default=True,
)

pagina_segmentacion = st.Page(
    str(PAGES_DIR / "2_Segmentacion.py"),
    title="Segmentación",
    icon="📊",
)

pagina_decision = st.Page(
    str(PAGES_DIR / "3_Decision.py"),
    title="Decisión",
    icon="🎯",
)

pagina_model_card = st.Page(
    str(PAGES_DIR / "4_Model_Card.py"),
    title="Model Card",
    icon="📋",
)

navegacion = st.navigation(
    [
        pagina_pronostico,
        pagina_segmentacion,
        pagina_decision,
        pagina_model_card,
    ]
)

navegacion.run()
