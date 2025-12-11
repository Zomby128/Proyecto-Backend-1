# 📊 Segmentación de Mercado con Datos del INEGI

Proyecto desarrollado para la materia **Desarrollo Backend I** del  
**Tecnológico Nacional de México – Instituto Tecnológico de Ensenada**.

---

## 📌 Descripción General

Este proyecto consiste en el desarrollo de una herramienta de **segmentación de mercado** utilizando datos del INEGI (DENUE), con el objetivo de analizar la distribución, concentración y características de las unidades económicas a nivel geográfico.

El sistema permite clasificar empresas por:
- Actividad económica
- Tamaño de empresa
- Ubicación geográfica

La información se visualiza mediante **mapas interactivos y métricas**, permitiendo detectar zonas con alta o baja competencia empresarial sin realizar predicciones ni análisis financieros.

---

## 🎯 Objetivo

Desarrollar un sistema backend que procese, normalice y analice datos económicos del INEGI para apoyar la identificación de oportunidades de inversión o expansión comercial mediante análisis territorial.

---

## ✅ Alcances

- Lectura y procesamiento de datos desde archivo Excel
- Limpieza y normalización de la información
- Clasificación del tamaño de las empresas
- Análisis de concentración empresarial por áreas geográficas
- Visualización interactiva mediante mapas y gráficas
- Filtros por municipio y tamaño de empresa

---

## 🚫 Fuera de Alcance

- Predicciones del mercado
- Análisis financieros (ventas, ingresos, utilidades)
- Información personal o confidencial
- Modelos de inteligencia artificial predictivos
- Sustitución de estudios oficiales del INEGI

---

## 🏗️ Arquitectura del Proyecto

```text
Proyecto/
│
├── dashboard_cell.py        # Dashboard principal (Streamlit)
├── procesamiento.py         # Limpieza y normalización de datos
├── src/
│   └── database.py          # Manejo de conexión y consultas
│
├── data/
│   └── db-ens-bc.xlsx       # Datos del INEGI
│
├── requirements.txt
└── README.md
