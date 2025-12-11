Objective

El objetivo de este proyecto es desarrollar una herramienta backend para la segmentación de mercado, utilizando datos abiertos del INEGI (DENUE), con el fin de clasificar unidades económicas por sector, tamaño y ubicación geográfica, y detectar patrones de concentración empresarial.

La herramienta busca apoyar la toma de decisiones estratégicas relacionadas con inversión, expansión de negocios y análisis territorial, sin realizar predicciones ni análisis financieros.

Goals

Clasificar las unidades económicas por:

Actividad económica (código INEGI).

Tamaño de empresa.

Ubicación geográfica (municipio y coordenadas).

Identificar patrones de concentración empresarial por zona.

Detectar zonas con alta competencia y zonas con baja competencia.

Visualizar la distribución geográfica de empresas mediante mapas y métricas.

Proporcionar información útil para estrategias de inversión o expansión comercial.

Sentar las bases para una futura evolución a soluciones B2B.

Non-Goals

No se pretende predecir el comportamiento futuro del mercado.

No se incluyen análisis financieros (ventas, ingresos o utilidades).

No se realizan encuestas ni validaciones de campo.

No se maneja información personal o confidencial.

No se busca reemplazar estudios oficiales del INEGI.

No se implementa un modelo de inteligencia artificial predictivo.

Background

El Directorio Estadístico Nacional de Unidades Económicas (DENUE) del INEGI proporciona información detallada de los establecimientos activos en México, incluyendo:

Razón social

Actividad económica

Ubicación geográfica

Personal ocupado

Tipo de unidad económica

Sin embargo, estos datos se distribuyen comúnmente en formatos planos, con información redundante y repetitiva (municipios, giros, direcciones), lo que dificulta su análisis eficiente y afecta la calidad de las consultas.

Para resolver este problema, el proyecto implementa un proceso de normalización de datos (1FN, 2FN y 3FN), reorganizando la información en un modelo relacional que mejora la integridad, eficiencia y escalabilidad del análisis.

Overview

El proyecto consiste en un sistema backend de análisis de mercado que:

Lee datos desde un archivo Excel del DENUE.

Limpia, transforma y elimina duplicados.

Normaliza la información en múltiples entidades relacionadas.

Clasifica las empresas por tamaño según el personal ocupado.

Realiza análisis de concentración empresarial mediante técnicas de clustering.

Permite la visualización de resultados en mapas y gráficas.

Clasificación de tamaño de empresa
Tamaño	Empleados
Micro	1–10
Pequeña	11–50
Mediana	51–250
Grande	251+
Detailed Design
Arquitectura General

Entrada de datos

Archivo Excel (.xlsx)

Procesamiento

Python

pandas

GeoPandas

scikit-learn

Backend

FastAPI

Visualización

Streamlit

Folium

Kepler.gl

Normalización de Datos

El archivo original se divide en las siguientes entidades principales:

Actividades_Economicas

id_actividad (PK)

codigo_act

nombre_act

Municipios

id_municipio (PK)

municipio

estado

Georreferencias

id_geo (PK)

latitud

longitud

Unidades_Economicas

id_unidad (PK)

razon_social

per_ocu

tamano_empresa

id_actividad (FK)

id_geo (FK)

Este diseño cumple con:

✅ Primera Forma Normal (1FN)

✅ Segunda Forma Normal (2FN)

✅ Tercera Forma Normal (3FN)

Solution 1
Frontend

Streamlit

Filtros por municipio, giro y tamaño de empresa.

Mapas interactivos.

Gráficas dinámicas.

Backend

FastAPI como API principal.

Procesamiento de datos con pandas.

Clasificación de tamaño de empresa.

Análisis de concentración empresarial usando DBSCAN.

Solution 2
Frontend

Kepler.gl

Mapas de calor.

Visualización avanzada de densidad territorial.

Exploración geoespacial interactiva.

Backend

FastAPI + GeoPandas.

Servicios para consulta por zona, giro y tamaño.

Preparado para escalabilidad futura.

Considerations

Los datos dependen de la actualización del DENUE.

La precisión del análisis depende de la calidad de la georreferenciación.

El sistema no sustituye estudios estadísticos oficiales.

Puede ampliarse a:

Dashboards empresariales.

Plataformas B2B.

Integración con bases de datos relacionales.

Metrics

Las métricas utilizadas para validar el sistema incluyen:

Número de empresas por municipio.

Distribución por tamaño de empresa.

Concentración empresarial por zona.

Sectores dominantes por región.

Identificación de zonas con baja competencia.
