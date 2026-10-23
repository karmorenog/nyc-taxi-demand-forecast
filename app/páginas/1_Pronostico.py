
import requests
import pandas as pd
import streamlit as st

st.title("🚕 Pronóstico de demanda")
st.write(
    "Consulta la demanda estimada de taxis por zona y hora "
    "a través de la API de FastAPI."
)

API_URL = "https://nyc-taxi-demand-forecast-a4be.onrender.com/pronostico"


@st.cache_data(ttl=60)
def cargar_datos_api():
    respuesta = requests.get(API_URL, timeout=30)
    respuesta.raise_for_status()
    datos = respuesta.json()["pronosticos"]
    return pd.DataFrame(datos)

try:
    df = cargar_datos_api()
except requests.exceptions.RequestException as error:
    st.error(
        "No fue posible consultar FastAPI. "
        "Verifica que la API esté ejecutándose en http://127.0.0.1:8000."
    )
    st.caption(f"Detalle técnico: {error}")
    st.stop()

if df.empty:
    st.warning("La API no devolvió pronósticos.")
    st.stop()

df["hora"] = pd.to_datetime(df["hora"])
df = df.sort_values(["PULocationID", "hora"])

st.success("Datos recibidos correctamente desde FastAPI.")

col1, col2, col3 = st.columns(3)
col1.metric("Zonas disponibles", df["PULocationID"].nunique())
col2.metric("Registros de pronóstico", len(df))
col3.metric(
    "Taxis recomendados en total",
    f'{int(df["taxis_recomendados"].sum()):,}'
)

st.divider()
st.subheader("Demanda por zona y hora")

zona = st.selectbox(
    "Selecciona una zona",
    sorted(df["PULocationID"].unique())
)

datos_zona = df[df["PULocationID"] == zona].sort_values("hora")

st.write(f"**Zona seleccionada:** {zona}")

grafica = datos_zona.copy()
grafica["hora"] = grafica["hora"].dt.strftime("%H:%M")
grafica = grafica.set_index("hora")[
    ["taxis_recomendados", "taxis_p50", "taxis_semana_anterior"]
]

st.line_chart(grafica)

st.subheader("Detalle del plan operativo")
st.dataframe(datos_zona, use_container_width=True, hide_index=True)

csv_exportar = datos_zona.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Descargar plan de la zona seleccionada",
    data=csv_exportar,
    file_name=f"plan_taxis_zona_{zona}.csv",
    mime="text/csv",
)

st.caption(
    "Fuente: endpoint /pronostico de FastAPI. "
    "Los valores corresponden al plan operativo disponible en la API."
)
