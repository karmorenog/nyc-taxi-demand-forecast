
import pandas as pd
import numpy as np
import requests
import streamlit as st
from sklearn.metrics import mean_absolute_error, mean_squared_error

API_URL = "http://127.0.0.1:8000/evaluacion"

st.title("📋 Model Card")
st.write(
    "Documentación del modelo de pronóstico de demanda de taxis en Nueva York."
)

# --------------------------------------------------
# 1. Objetivo del modelo
# --------------------------------------------------
st.subheader("1. Objetivo del modelo")
st.write(
    "Estimar la demanda de taxis por zona y hora para apoyar "
    "la planificación operativa y la asignación de vehículos."
)

# --------------------------------------------------
# 2. Datos utilizados
# --------------------------------------------------
st.subheader("2. Datos utilizados")
st.markdown("""
- Datos históricos de viajes de taxis.
- Variables temporales para identificar patrones de demanda.
- Características de las zonas para la segmentación.
- Evaluación temporal con datos reales del conjunto de prueba.
""")

# --------------------------------------------------
# 3. Evaluación del modelo desde FastAPI
# --------------------------------------------------
st.subheader("3. Evaluación del modelo")


@st.cache_data(ttl=60)
def cargar_evaluacion_api():
    respuesta = requests.get(API_URL, timeout=60)
    respuesta.raise_for_status()
    return pd.DataFrame(respuesta.json()["evaluacion"])


try:
    evaluacion = cargar_evaluacion_api()
except requests.exceptions.RequestException as error:
    st.error("No fue posible consultar la evaluación desde FastAPI.")
    st.caption(f"Detalle técnico: {error}")
    st.stop()

columnas = ["viajes", "prediccion_xgboost", "lag_168"]
faltantes = [col for col in columnas if col not in evaluacion.columns]

if faltantes:
    st.error("Faltan columnas necesarias: " + ", ".join(faltantes))
    st.stop()

evaluacion[columnas] = evaluacion[columnas].apply(
    pd.to_numeric, errors="coerce"
)
datos = evaluacion[columnas].dropna()

if datos.empty:
    st.error("No hay observaciones completas para evaluar el modelo.")
    st.stop()

y_real = datos["viajes"]
pred_xgb = datos["prediccion_xgboost"].clip(lower=0)
pred_base = datos["lag_168"].clip(lower=0)

mae_xgb = mean_absolute_error(y_real, pred_xgb)
rmse_xgb = np.sqrt(mean_squared_error(y_real, pred_xgb))

mae_base = mean_absolute_error(y_real, pred_base)
rmse_base = np.sqrt(mean_squared_error(y_real, pred_base))

st.success(
    f"Evaluación recibida desde FastAPI: {len(datos):,} observaciones."
)

col1, col2 = st.columns(2)

with col1:
    st.markdown("**XGBoost**")
    st.metric("MAE", f"{mae_xgb:.2f}")
    st.metric("RMSE", f"{rmse_xgb:.2f}")

with col2:
    st.markdown("**Referencia semanal (lag_168)**")
    st.metric("MAE", f"{mae_base:.2f}")
    st.metric("RMSE", f"{rmse_base:.2f}")

comparacion = pd.DataFrame({
    "Modelo": ["XGBoost", "Referencia semanal"],
    "MAE": [mae_xgb, mae_base],
    "RMSE": [rmse_xgb, rmse_base],
})

st.dataframe(
    comparacion.style.format({
        "MAE": "{:.2f}",
        "RMSE": "{:.2f}",
    }),
    use_container_width=True,
    hide_index=True,
)

if mae_xgb < mae_base and rmse_xgb < rmse_base:
    st.success(
        "XGBoost obtiene menor error que la referencia semanal en ambas métricas."
    )
elif mae_xgb > mae_base and rmse_xgb > rmse_base:
    st.warning(
        "La referencia semanal obtiene menor error que XGBoost en ambas métricas."
    )
else:
    st.info(
        "Los resultados son mixtos o equivalentes. Compara ambas métricas."
    )

st.caption(
    "MAE representa el error absoluto medio. RMSE penaliza más los errores "
    "de mayor magnitud. En ambas métricas, un valor menor indica mejor desempeño."
)

# --------------------------------------------------
# 4. Incertidumbre
# --------------------------------------------------
st.subheader("4. Incertidumbre")
st.write(
    "En la evaluación previa, el intervalo p10–p90 cubrió aproximadamente "
    "el 74.56% de los valores reales, por debajo del objetivo del 80%."
)
st.warning(
    "Esta cobertura procede de un análisis previo. El endpoint actual no "
    "incluye los límites p10 y p90, por lo que no se recalcula aquí."
)

# --------------------------------------------------
# 5. Evaluación económica
# --------------------------------------------------
st.subheader("5. Evaluación económica")

st.markdown("""
Supuestos utilizados en la simulación:

- **$40** por pasajero perdido.
- **$10** por taxi sin utilizar.
""")

st.write(
    "En la simulación actual, la referencia semanal presenta un costo "
    "estimado menor que XGBoost. El resultado depende de los costos "
    "configurados y de la regla utilizada para convertir predicciones "
    "en taxis disponibles."
)

st.caption(
    "Los costos son simulados, no costos operativos observados. "
    "La comparación económica completa está en la página Decisión."
)

# --------------------------------------------------
# 6. Limitaciones y uso responsable
# --------------------------------------------------
st.subheader("6. Limitaciones y uso responsable")

st.markdown("""
- Los patrones históricos pueden cambiar con el tiempo.
- Los errores pueden variar entre zonas.
- Las predicciones son estimaciones, no garantías de demanda.
- El modelo no supera necesariamente una referencia sencilla.
- La cobertura del intervalo de incertidumbre puede ser inferior al objetivo.
- Los costos simulados dependen de los supuestos utilizados.
- Se recomienda revisar los resultados antes de tomar decisiones operativas.
""")

st.caption("Fuente de los datos de evaluación: endpoint /evaluacion de FastAPI.")
