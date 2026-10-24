
from datetime import date
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(
    title="NYC Taxi Demand API",
    description="API para consultar pronósticos de demanda de taxis por zona y fecha.",
    version="1.1.0",
)

BASE_DIR = Path(__file__).resolve().parent.parent

PLAN_PATH = BASE_DIR / "plan_operativo_taxis_actualizado_2024-02-01.csv"
EVALUACION_PATH = BASE_DIR / "evaluacion_pronosticos.csv"
SEGMENTACION_PATH = BASE_DIR / "segmentacion_zonas_taxi.csv"


@app.get("/")
def inicio():
    return {
        "mensaje": "NYC Taxi Demand API está funcionando",
        "documentacion": "/docs",
    }


@app.get("/info")
def informacion():
    return {
        "proyecto": "Pronóstico de demanda de taxis de NYC",
        "datos": "Viajes de enero y plan operativo de febrero de 2024",
        "modelo": "XGBoost y referencia semanal",
        "unidad_pronostico": "demanda por zona y hora",
        "endpoints": [
            "/",
            "/info",
            "/pronostico",
            "/segmentacion",
            "/evaluacion",
        ],
    }


@app.get("/pronostico")
def consultar_pronostico(
    zona_id: int | None = Query(
        default=None,
        ge=1,
        description="ID de la zona de recogida",
    ),
    fecha: date | None = Query(
        default=None,
        description="Fecha de consulta en formato YYYY-MM-DD",
    ),
    hora: int | None = Query(
        default=None,
        ge=0,
        le=23,
        description="Hora opcional del día, de 0 a 23",
    ),
    zona: int | None = Query(
        default=None,
        ge=1,
        description="Parámetro zona antiguo, mantenido por compatibilidad",
    ),
):
    # Permite utilizar tanto zona_id como el parámetro anterior zona.
    zona_consulta = zona_id if zona_id is not None else zona

    if zona_consulta is None:
        raise HTTPException(
            status_code=422,
            detail="Debes indicar zona_id. Ejemplo: ?zona_id=4&fecha=2024-01-25",
        )

    # Si no se proporciona fecha, se mantiene la consulta del plan operativo.
    fecha_consulta = fecha or date(2024, 2, 1)

    # Primero se intenta consultar la evaluación, que incluye demanda real.
    if EVALUACION_PATH.exists():
        evaluacion = pd.read_csv(EVALUACION_PATH)

        columnas_eval = {
            "hora",
            "PULocationID",
            "viajes",
            "lag_168",
            "prediccion_xgboost",
        }

        if columnas_eval.issubset(evaluacion.columns):
            evaluacion["hora"] = pd.to_datetime(
                evaluacion["hora"], errors="coerce"
            )

            datos_eval = evaluacion[
                (evaluacion["PULocationID"] == zona_consulta)
                & (evaluacion["hora"].dt.date == fecha_consulta)
            ].copy()

            if not datos_eval.empty:
                if hora is not None:
                    datos_eval = datos_eval[
                        datos_eval["hora"].dt.hour == hora
                    ]

                if datos_eval.empty:
                    raise HTTPException(
                        status_code=404,
                        detail="No hay resultados para esa zona, fecha y hora.",
                    )

                datos_eval = datos_eval.rename(
                    columns={
                        "viajes": "demanda_real",
                        "prediccion_xgboost": "pronostico_xgboost",
                        "lag_168": "referencia_semanal",
                    }
                )

                # El CSV actual no contiene límites p10 y p90.
                if "prediccion_p50" not in datos_eval.columns:
                    datos_eval["prediccion_p50"] = None

                datos_eval = datos_eval.astype(object).where(
                    pd.notna(datos_eval), None
                )

                return {
                    "zona_id": zona_consulta,
                    "fecha": fecha_consulta.isoformat(),
                    "fuente": "evaluacion_pronosticos.csv",
                    "total_resultados": len(datos_eval),
                    "pronosticos": datos_eval.to_dict(orient="records"),
                    "nota": (
                        "Incluye demanda real y predicciones de evaluación. "
                        "Los cuantiles p10 y p90 no están disponibles "
                        "en este archivo."
                    ),
                }

    # Si la fecha no está en evaluación, se busca en el plan operativo.
    if not PLAN_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail="No se encontró el archivo del plan operativo.",
        )

    plan = pd.read_csv(PLAN_PATH)
    plan["hora"] = pd.to_datetime(plan["hora"], errors="coerce")

    datos_plan = plan[
        (plan["PULocationID"] == zona_consulta)
        & (plan["hora"].dt.date == fecha_consulta)
    ].copy()

    if hora is not None:
        datos_plan = datos_plan[datos_plan["hora"].dt.hour == hora]

    if datos_plan.empty:
        raise HTTPException(
            status_code=404,
            detail=(
                "No hay resultados para esa zona, fecha y hora. "
                "La evaluación disponible cubre parte de enero y el "
                "plan operativo disponible corresponde al 1 de febrero "
                "de 2024."
            ),
        )

    datos_plan = datos_plan.astype(object).where(
        pd.notna(datos_plan), None
    )

    return {
        "zona_id": zona_consulta,
        "fecha": fecha_consulta.isoformat(),
        "fuente": "plan_operativo_taxis_actualizado_2024-02-01.csv",
        "total_resultados": len(datos_plan),
        "pronosticos": datos_plan.to_dict(orient="records"),
        "nota": (
            "Estos son los valores guardados en el plan operativo; "
            "no se genera un pronóstico nuevo al consultar la API."
        ),
    }


@app.get("/segmentacion")
def consultar_segmentacion(
    grupo: int | None = Query(
        default=None,
        description="Grupo de segmentación K-Means",
    ),
):
    if not SEGMENTACION_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail="No se encontró el archivo CSV de segmentación.",
        )

    df = pd.read_csv(SEGMENTACION_PATH)

    if grupo is not None:
        df = df[df["cluster"] == grupo]

    df = df.astype(object).where(pd.notna(df), None)

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron zonas para ese grupo.",
        )

    return {
        "total_resultados": len(df),
        "zonas": df.to_dict(orient="records"),
    }


@app.get("/evaluacion")
def consultar_evaluacion():
    if not EVALUACION_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail="No se encontró el archivo CSV de evaluación.",
        )

    df = pd.read_csv(EVALUACION_PATH)
    df = df.astype(object).where(pd.notna(df), None)

    return {
        "total_resultados": len(df),
        "evaluacion": df.to_dict(orient="records"),
    }
