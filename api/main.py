
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(
    title="NYC Taxi Demand API",
    description="API para consultar el plan de demanda de taxis por zona y hora.",
    version="1.0.0",
)

# El CSV está en la carpeta principal del proyecto.
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "plan_operativo_taxis_actualizado_2024-02-01.csv"


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
        "datos": "Viajes de enero de 2024",
        "modelo": "XGBoost y plan operativo",
        "unidad_pronostico": "viajes por zona y hora",
    }


@app.get("/pronostico")
def consultar_pronostico(
    zona: int | None = Query(default=None, description="ID de la zona de recogida"),
    hora: int | None = Query(default=None, ge=0, le=23, description="Hora del día, de 0 a 23"),
):
    if not CSV_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail="No se encontró el archivo CSV del plan operativo.",
        )

    df = pd.read_csv(CSV_PATH)

    if zona is not None:
        df = df[df["PULocationID"] == zona]

    if hora is not None:
        df = df[df["hora"] == hora]

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron resultados para esos filtros.",
        )

    return {
        "total_resultados": len(df),
        "pronosticos": df.to_dict(orient="records"),
    }


SEGMENTACION_PATH = BASE_DIR / "segmentacion_zonas_taxi.csv"


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
    df = df.astype(object).where(pd.notna(df), None)


    if grupo is not None:
        df = df[df["cluster"] == grupo]

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron zonas para ese grupo.",
        )

    return {
        "total_resultados": len(df),
        "zonas": df.to_dict(orient="records"),
    }




EVALUACION_PATH = BASE_DIR / "evaluacion_pronosticos.csv"


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
