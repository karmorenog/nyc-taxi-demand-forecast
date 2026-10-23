
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

st.title("🎯 Decisión operativa")
st.write(
    "Define los costos operativos para comparar estrategias "
    "según la demanda observada."
)

EVALUACION_URL = "https://nyc-taxi-demand-forecast-a4be.onrender.com/evaluacion"
PRONOSTICO_URL = "https://nyc-taxi-demand-forecast-a4be.onrender.com/pronostico"


st.subheader("1. Parámetros de costos")

col1, col2 = st.columns(2)

with col1:
    costo_pasajero = st.number_input(
        "Costo por pasajero perdido ($)",
        min_value=0.0,
        value=40.0,
        step=5.0,
    )

with col2:
    costo_taxi = st.number_input(
        "Costo por taxi sin utilizar ($)",
        min_value=0.0,
        value=10.0,
        step=5.0,
    )

total_costos = costo_pasajero + costo_taxi

if total_costos > 0:
    cuantil = costo_pasajero / total_costos
    st.metric("Cuantil óptimo recomendado", f"{cuantil:.0%}")
    st.caption(
        "El cuantil equilibra el costo de perder pasajeros "
        "con el costo de tener taxis sin utilizar."
    )
else:
    st.warning(
        "Ingresa al menos uno de los dos costos con valor mayor que cero."
    )

st.divider()
st.subheader("2. Comparación de estrategias con datos reales")

@st.cache_data(ttl=60)
def cargar_evaluacion_api():
    respuesta = requests.get(EVALUACION_URL, timeout=60)
    respuesta.raise_for_status()
    return pd.DataFrame(respuesta.json()["evaluacion"])


try:
    evaluacion = cargar_evaluacion_api()
except requests.exceptions.RequestException as error:
    st.error("No fue posible consultar la evaluación en FastAPI.")
    st.caption(f"Detalle técnico: {error}")
    st.stop()

columnas = ["viajes", "prediccion_xgboost", "lag_168"]
faltantes = [c for c in columnas if c not in evaluacion.columns]

if faltantes:
    st.error("Faltan columnas en la evaluación: " + ", ".join(faltantes))
    st.stop()

evaluacion[columnas] = evaluacion[columnas].apply(
    pd.to_numeric, errors="coerce"
)
evaluacion = evaluacion.dropna(subset=columnas)

if evaluacion.empty:
    st.error("No hay observaciones válidas para comparar.")
    st.stop()

st.success(
    f"Evaluación recibida desde FastAPI: {len(evaluacion):,} observaciones."
)

st.write(
    "Comparamos las estrategias con la demanda observada en el período "
    "de prueba. El costo incluye pasajeros potencialmente perdidos "
    "y taxis sin utilizar."
)
st.caption(
    "Supuesto de simulación: cada unidad de demanda representa un pasajero "
    "potencial y cada unidad asignada representa un taxi disponible. "
    "Los costos son estimaciones, no costos operativos observados."
)


def calcular_costo(demanda, taxis, costo_perdido, costo_idle):
    demanda = pd.Series(demanda).clip(lower=0)
    taxis = pd.Series(taxis).clip(lower=0)

    pasajeros_perdidos = (demanda - taxis).clip(lower=0)
    taxis_sin_utilizar = (taxis - demanda).clip(lower=0)

    total = (
        pasajeros_perdidos.sum() * costo_perdido
        + taxis_sin_utilizar.sum() * costo_idle
    )

    return {
        "Pasajeros perdidos": int(pasajeros_perdidos.sum()),
        "Taxis sin utilizar": int(taxis_sin_utilizar.sum()),
        "Costo total estimado ($)": total,
    }


demanda_real = evaluacion["viajes"]

estrategias = {
    "XGBoost": evaluacion["prediccion_xgboost"].clip(lower=0),
    "Semana anterior": evaluacion["lag_168"].clip(lower=0),
}

filas = []

for nombre, prediccion in estrategias.items():
    taxis_asignados = prediccion.apply(lambda x: int(__import__("math").ceil(x)))
    resultado = calcular_costo(
        demanda_real,
        taxis_asignados,
        costo_pasajero,
        costo_taxi,
    )
    filas.append({"Estrategia": nombre, **resultado})

comparacion = pd.DataFrame(filas)

st.dataframe(
    comparacion.style.format(
        {
            "Pasajeros perdidos": "{:,.0f}",
            "Taxis sin utilizar": "{:,.0f}",
            "Costo total estimado ($)": "${:,.2f}",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

st.bar_chart(
    comparacion.set_index("Estrategia")[["Costo total estimado ($)"]]
)

st.caption(
    "Las predicciones se redondean hacia arriba para simular unidades "
    "enteras de taxis. Ambas estrategias se comparan sobre las mismas "
    "observaciones."
)

st.divider()
st.subheader("3. Exportación del plan operativo")

BASE_DIR = Path(__file__).resolve().parents[2]

@st.cache_data(ttl=60)
def cargar_plan_api():
    respuesta = requests.get(PRONOSTICO_URL, timeout=60)
    respuesta.raise_for_status()
    return pd.DataFrame(respuesta.json()["pronosticos"])


try:
    plan = cargar_plan_api()
except requests.exceptions.RequestException as error:
    st.error("No fue posible consultar el plan operativo en FastAPI.")
    st.caption(f"Detalle técnico: {error}")
    st.stop()

if not plan.empty:
    zona = st.selectbox(
        "Selecciona una zona para exportar",
        sorted(plan["PULocationID"].unique()),
        key="zona_exportacion",
    )

    plan_zona = plan[plan["PULocationID"] == zona].copy()

    st.dataframe(
        plan_zona,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Descargar plan operativo en CSV",
        data=plan_zona.to_csv(index=False).encode("utf-8"),
        file_name=f"plan_operativo_zona_{zona}.csv",
        mime="text/csv",
    )
else:
    st.warning("La API no devolvió datos del plan operativo.")
