 # Taxis NYC: Pronóstico de Demanda, Segmentación y Toma de Decisiones

## 1. Descripción del proyecto

Este proyecto consiste en el desarrollo de una herramienta de análisis y apoyo a la toma de decisiones para la planificación de taxis amarillos en la ciudad de Nueva York.

La solución utiliza datos históricos de viajes de enero de 2024 para analizar la demanda por zona de recogida y hora del día. Integra técnicas de aprendizaje automático, análisis de series de tiempo y segmentación de zonas para proporcionar información útil sobre la demanda esperada, sus niveles de incertidumbre y las decisiones operativas relacionadas con la asignación de taxis.

El proyecto está compuesto por una API desarrollada con FastAPI y una aplicación interactiva desarrollada con Streamlit.

## 2. Objetivos del proyecto

- Analizar los patrones históricos de demanda de taxis por zona y hora.
- Desarrollar un modelo para pronosticar la cantidad de viajes por hora.
- Estimar la incertidumbre de los pronósticos mediante diferentes cuantiles.
- Comparar el desempeño del modelo con una referencia basada en la demanda de la semana anterior.
- Segmentar las zonas de recogida según sus características históricas de demanda.
- Generar recomendaciones para apoyar la asignación de taxis y la planificación operativa.
- Documentar el desempeño, las limitaciones y los usos apropiados del modelo.

## 3. Datos utilizados

El análisis utiliza datos históricos de viajes de taxis amarillos de Nueva York correspondientes a enero de 2024, publicados por la NYC Taxi & Limousine Commission (NYC TLC).

Los viajes se agrupan por hora y por zona de recogida utilizando el identificador `PULocationID`. Las horas sin viajes se consideran registros con demanda igual a cero para mantener una serie temporal completa.

A partir de los datos históricos se construyen variables relacionadas con el calendario y la demanda de periodos anteriores, como los rezagos de 24, 48 y 168 horas.

Fuentes de datos originales:

- [Datos de viajes de taxis amarillos de enero de 2024](https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet)
- [Catálogo de zonas de taxis de Nueva York](https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv)

## 4. Tecnologías utilizadas

- **Python:** desarrollo y procesamiento de datos.
- **Pandas y NumPy:** limpieza, transformación y análisis de datos.
- **XGBoost:** desarrollo del modelo de pronóstico.
- **Scikit-learn:** técnicas de segmentación y análisis de componentes principales, según su implementación en los notebooks.
- **FastAPI:** creación de la API para consultar los resultados del pronóstico.
- **Streamlit:** desarrollo de la interfaz interactiva.
- **Jupyter Notebook:** preparación de datos, experimentación y evaluación.
- **GitHub:** control de versiones y almacenamiento del código.
- **Render y Streamlit Community Cloud:** plataformas previstas para publicar la API y la aplicación, respectivamente.

## 5. Estructura del proyecto

### API

La carpeta `api/` contiene los componentes del servicio de pronóstico.

- `api/main.py`: implementación de los endpoints y la lógica de consulta de la API.
- `api/requirements.txt`: dependencias necesarias para ejecutar la API.

### Aplicación interactiva

La carpeta `app/` contiene la aplicación desarrollada con Streamlit.

- `app/streamlit_app.py`: punto de entrada de la aplicación y navegación entre las páginas.
- `app/páginas/1_Pronostico.py`: interfaz para consultar y analizar el pronóstico de demanda.
- `app/páginas/2_Segmentacion.py`: análisis de los grupos de zonas según sus características de demanda.
- `app/páginas/3_Decision.py`: herramienta de apoyo para decidir cuántos taxis asignar según los criterios implementados.
- `app/páginas/4_Model_Card.py`: presentación de las métricas, el desempeño y las limitaciones del modelo.

### Notebooks de preparación y análisis

- `Org preparacion.ipynb`: notebook original de preparación y análisis.
- `preparacion_limpio.ipynb`: versión de trabajo para la preparación, evaluación y documentación de los resultados.

### Archivos de datos y resultados

- `plan_operativo_taxis_actualizado_2024-02-01.csv`: versión actualizada de los datos del plan operativo.
- `evaluacion_pronosticos.csv`: resultados de la evaluación de los pronósticos.
- `segmentacion_zonas_taxi.csv`: resultados de la segmentación de zonas.
- `recomendacion_zonas_taxi.csv`: recomendaciones generadas para apoyar las decisiones operativas.
- `model_card.txt`: documentación técnica del modelo, sus resultados y sus limitaciones.

## 6. Funcionalidades de la aplicación

### 6.1 Pronóstico de demanda

Permite consultar la demanda estimada de viajes por zona de recogida y hora. El análisis contempla diferentes cuantiles para representar la incertidumbre y facilitar la interpretación de los posibles niveles de demanda.

### 6.2 Segmentación de zonas

Utiliza técnicas de aprendizaje no supervisado para identificar grupos de zonas con características de demanda similares.

La segmentación desarrollada con K-Means utiliza dos grupos principales:

- **Alta demanda:** zonas con mayores niveles históricos de viajes.
- **Demanda baja o moderada:** zonas con menores niveles históricos de viajes.

### 6.3 Toma de decisiones

Proporciona información y recomendaciones para apoyar la asignación de taxis según la demanda esperada y los criterios operativos definidos en el proyecto.

### 6.4 Ficha del modelo

Presenta las métricas de evaluación, la comparación con una referencia sencilla, el análisis de incertidumbre y las limitaciones identificadas.

## 7. Evaluación del modelo

El modelo principal utiliza XGBoost y se evalúa con datos del 25 al 31 de enero de 2024.

Los resultados registrados en la ficha del modelo son:

| Modelo o referencia | MAE | RMSE |
| --- | ---: | ---: |
| XGBoost | 11.9188 | 21.9749 |
| Referencia: semana anterior | 11.7621 | 21.7108 |

El MAE representa el error absoluto medio y el RMSE penaliza en mayor medida los errores grandes. En ambas métricas, un valor menor indica un mejor desempeño.

En la evaluación realizada, la referencia basada en la semana anterior obtiene resultados ligeramente mejores que XGBoost. Por lo tanto, no se demuestra una mejora del modelo principal frente a esta referencia sencilla.

La cobertura observada del intervalo entre los cuantiles p10 y p90 es del 74.56 %, por debajo del objetivo aproximado del 80 %. Además, la cobertura varía entre los grupos de zonas, por lo que es necesario continuar evaluando y calibrando los intervalos de incertidumbre.

## 8. Ejecución del proyecto

### Aplicación Streamlit

Desde la carpeta raíz del repositorio, instala las dependencias correspondientes y ejecuta:

```bash
streamlit run app/streamlit_app.py
```

### API FastAPI

Las dependencias de la API se encuentran en `api/requirements.txt`.

Para ejecutarla localmente, accede a la carpeta `api/`, instala las dependencias y ejecuta:

```bash
uvicorn main:app --reload
```

La documentación interactiva de FastAPI estará disponible en `http://localhost:8000/docs` cuando el servicio se encuentre funcionando localmente.

**Nota:** los comandos y las dependencias deben coincidir con la configuración actual del repositorio.

## 9. Limitaciones y uso responsable

Los resultados dependen de los datos históricos disponibles y de las características incluidas en el modelo. El periodo de evaluación corresponde a enero de 2024, por lo que el desempeño no garantiza la misma precisión en periodos posteriores.

La comparación realizada no demuestra que XGBoost supere la referencia basada en la semana anterior. Asimismo, los intervalos de incertidumbre requieren evaluación adicional, especialmente en las zonas de alta demanda.

Las predicciones deben utilizarse como apoyo para la planificación y no como garantía de la demanda futura. Antes de utilizar el sistema en operaciones reales, se recomienda validar su desempeño con datos más recientes y revisar periódicamente sus resultados.

## 10. Funciones avanzadas de Streamlit
El proyecto utiliza las siguientes funciones avanzadas para mejorar la experiencia del usuario:

- Función	Uso en el proyecto

st.navigation y st.Page	Organizar la aplicación en cuatro páginas.
@st.fragment	Actualizar la sección de recomendación sin recargar toda la página.
@st.dialog	Mostrar una ventana emergente con explicaciones o ayuda.
st.plotly_chart(on_select="rerun")	Permitir seleccionar zonas directamente en un gráfico interactivo.
st.column_config	Mejorar la presentación de las tablas.
@st.cache_data	Evitar repetir innecesariamente consultas a la API.
st.secrets	Guardar la dirección de la API fuera del código.
st.query_params	Recordar la zona y la fecha seleccionadas en el enlace.
st.status y st.toast	Mostrar el estado de una operación y avisos al usuario.

## 11. Enlaces del proyecto

- **Repositorio de GitHub:** https://github.com/karmorenog/nyc-taxi-demand-forecast
- - **Aplicación Streamlit:** https://nyc-taxi-demand-forecast-jnk.streamlit.app/Model_Card
- **Documentación de la API:** https://nyc-taxi-demand-forecast-a4be.onrender.com/docs?utm_source

## 12. Autores

**Integrantes:**
•	Josué Ezequiel Mozo García
•	Natalya Georgina Molina Álvarez
•	Karla Marina Moreno González


**Proyecto académico:** Taxis NYC — Pronóstico de Demanda, Segmentación y Toma de Decisiones.
