
import requests
import pandas as pd
import streamlit as st

st.title("📊 Segmentación de zonas")
st.write(
    "Explora los grupos identificados mediante K-Means "
    "y compara sus características de demanda."
)

API_URL = "https://nyc-taxi-demand-forecast-a4be.onrender.com/segmentacion"


@st.cache_data(ttl=60)
def cargar_segmentacion():
    respuesta = requests.get(API_URL, timeout=30)
    respuesta.raise_for_status()
    return pd.DataFrame(respuesta.json()["zonas"])


try:
    df = cargar_segmentacion()
except requests.exceptions.RequestException as error:
    st.error(
        "No fue posible consultar la segmentación en FastAPI. "
        "Verifica que la API esté ejecutándose."
    )
    st.caption(f"Detalle técnico: {error}")
    st.stop()

if df.empty:
    st.warning("La API no devolvió datos de segmentación.")
    st.stop()

df["cluster"] = pd.to_numeric(df["cluster"], errors="coerce")
df["promedio_hora"] = pd.to_numeric(
    df["promedio_hora"], errors="coerce"
)
df["total_viajes"] = pd.to_numeric(
    df["total_viajes"], errors="coerce"
)
df["PC1"] = pd.to_numeric(df["PC1"], errors="coerce")
df["PC2"] = pd.to_numeric(df["PC2"], errors="coerce")

grupos = sorted(df["cluster"].dropna().unique())

if not grupos:
    st.error("No se encontraron grupos válidos en los datos.")
    st.stop()

grupo = st.selectbox(
    "Selecciona un grupo",
    grupos,
    format_func=lambda x: f"Grupo {int(x)}",
)

datos = df[df["cluster"] == grupo].copy()

if grupo == 0:
    st.info(
        "Grupo 0: zonas de alta demanda. "
        "Estas zonas pueden requerir mayor disponibilidad de taxis."
    )
else:
    st.info(
        "Este grupo reúne zonas con características de demanda "
        "similares. Ajusta la disponibilidad de taxis según "
        "los resultados observados."
    )

col1, col2 = st.columns(2)

col1.metric("Zonas en el grupo", len(datos))
col2.metric(
    "Promedio de viajes por hora",
    f'{datos["promedio_hora"].mean():,.1f}'
)

st.subheader("Zonas del grupo")

columnas_tabla = [
    "PULocationID",
    "Zone",
    "Borough",
    "total_viajes",
    "promedio_hora",
    "cluster",
]

st.dataframe(
    datos[columnas_tabla].sort_values(
        "total_viajes", ascending=False, na_position="last"
    ),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Visualización PCA")
st.caption(
    "Cada punto representa una zona. PC1 y PC2 son las "
    "dos componentes principales del análisis."
)

datos_pca = df.dropna(subset=["PC1", "PC2", "cluster"]).copy()

if not datos_pca.empty:
    st.scatter_chart(
        datos_pca,
        x="PC1",
        y="PC2",
        color="cluster",
        size="promedio_hora",
    )
else:
    st.warning("No hay suficientes datos para mostrar la gráfica PCA.")

st.caption("Fuente: endpoint /segmentacion de FastAPI.")
