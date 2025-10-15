# Proyecto-Backend-1
# Segmentacion de Mercado
Link:

Author(s): Adolfo Alejandro Granados Cosio.

Status: Borrador.

Last Updated: 2025-10-14

## Contents
- Goals:
1. Clasificar las unidades económicas por sector, tamaño y ubicación geográfica utilizando los datos del INEGI.
2. Identificar patrones de concentración empresarial, mostrando en qué zonas hay más, menos o diversidad de empresas según su actividad económica.
3. Detectar oportunidades de negocio o zonas con baja competencia para determinados giros comerciales.
4. Proporcionar información útil para estrategias sobre decisiones de inversión o expansión de negocios.
   
- Non-Goals:
No se busca predecir comportamiento futuro del mercado (no es un modelo predictivo).
No se incluirán análisis financieros detallados (ventas, ingresos, utilidades).
No se realizará validación de campo ni encuestas directas a empresas.
No se incluirá información personal ni confidencial de los negocios.
No se busca reemplazar estudios estadísticos del INEGI, sino complementarlos con análisis segmentado y visual.
Se puede mejorar a que ayude a hacer B2B.

- Background:
El Directorio Estadístico Nacional de Unidades Económicas (DENUE) del INEGI proporciona información detallada de los establecimientos activos en México, incluyendo su razón social, actividad económica, ubicación, tamaño y tipo de unidad.
Sin embargo, los datos originales se encuentran en un formato plano y redundante, lo que dificulta los análisis específicos.

Mediante un proceso de normalización (1FN, 2FN, 3FN) se reestructuran las tablas en un modelo relacional más eficiente, eliminando duplicados y separando entidades como:
- Actividades_Económicas
- Unidades_Económicas
- Direcciones
- Contactos
- Georreferencias
- Municipios / Localidades
Esto permite realizar consultas y visualizaciones precisas.

- Overview
El proyecto busca crear una herramienta de análisis de mercado basada en datos normalizados del INEGI, capaz de:
1. Aplicar filtros por actividad económica (codigo_act), tamaño (per_ocu), y ubicación (municipio, latitud, longitud).

Clasificar empresas según su tamaño:
- Micro: 1–10 empleados
- Pequeña: 11–50
- Mediana: 51–250
- Grande: 251+

Visualizar los resultados en un mapa o gráfico de densidad, para identificar:
- Áreas con alta o baja concentración empresarial.
- Sectores dominantes por región.
- Distribución geográfica de empresas por tamaño.

- Detailed Design
  - Solution 1
    - Frontend
    - Backend
  - Solution 2
    - Frontend
    - Backend
- Considerations
- Metrics

## Links
- [A link](#)
- [Another link](#)

## Objective
_What and why are we doing this?_

_Include context for people that are unfamiliar with the project._

_Keep it short, elaborate below in **Background, Overview and Detailed Design**_

_Add screenshots / mocks where necessary_

## Goals
- Goals
## Non-Goals
- Non-Goals

## Background
_What is the context of the project?_

_Include resources like other design docs if needed._

_Don’t write about your design or requirements here._

## Overview
_High-level overview of your proposal._

_This section should be understandable by new employees on your team that is not related to the project._

_Put details in the next section._

## Detailed Design
_Use diagrams where necessary._

_Tools like [Excalidraw](https://excalidraw.com) are good resources for this._

_Cover major changes:_

 _- What are the new functions that you will write?_

 _- Why do you need new components?_

 _- Is there any code that can be reusable?_

_Don’t elaborate deeply on the implementation details._

## Solution 1
### Frontend
_Frontend…_
### Backend
_Backend…_

## Solution 2
### Frontend
_Frontend…_
### Backend
_Backend…_

## Considerations
_Concerns / trade-offs / tech debt_

## Metrics
_What data do you need to validate before launching this feature?_












