import numpy as np
from math import radians, sin, cos, sqrt, atan2
from shapely.geometry import Point, Polygon
import pandas as pd

def clasificar_tamano_inegi(per_ocu_str):
    """
    Clasifica el tamaño basado en la descripción de INEGI
    Ejemplo: "0 a 5 personas" -> "Micro"
    """
    if pd.isna(per_ocu_str):
        return "Sin información"
    
    per_ocu_str = str(per_ocu_str).lower()
    
    if "0 a 5" in per_ocu_str or "1 a 5" in per_ocu_str:
        return "Micro"
    elif "6 a 10" in per_ocu_str:
        return "Micro"
    elif "11 a 30" in per_ocu_str:
        return "Pequeña"
    elif "31 a 50" in per_ocu_str:
        return "Pequeña"
    elif "51 a 100" in per_ocu_str:
        return "Mediana"
    elif "101 a 250" in per_ocu_str:
        return "Mediana"
    elif "251" in per_ocu_str or "más" in per_ocu_str:
        return "Grande"
    else:
        return "Otro"

def extraer_empleados_max(rango):
    """Extrae el número máximo de empleados del rango"""
    if pd.isna(rango):
        return 0
    
    texto = str(rango)
    numeros = [int(s) for s in texto.split() if s.isdigit()]
    
    if numeros:
        return max(numeros)
    return 0

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calcula distancia en km entre dos puntos usando fórmula de Haversine
    """
    R = 6371  # Radio de la Tierra en km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

def filtrar_por_poligono(df, coordenadas_poligono):
    """
    Filtra empresas dentro de un polígono
    coordenadas_poligono: lista de tuples [(lon1, lat1), (lon2, lat2), ...]
    """
    if not coordenadas_poligono or len(coordenadas_poligono) < 3:
        return pd.DataFrame()
    
    poligono = Polygon(coordenadas_poligono)
    
    empresas_dentro = []
    for idx, row in df.iterrows():
        if pd.notna(row['latitud']) and pd.notna(row['longitud']):
            punto = Point(row['longitud'], row['latitud'])
            if poligono.contains(punto):
                empresas_dentro.append(row)
    
    return pd.DataFrame(empresas_dentro)

def filtrar_por_circulo(df, centro_lat, centro_lon, radio_km):
    """
    Filtra empresas dentro de un círculo
    """
    empresas_dentro = []
    
    for idx, row in df.iterrows():
        if pd.notna(row['latitud']) and pd.notna(row['longitud']):
            distancia = haversine_distance(
                centro_lat, centro_lon,
                row['latitud'], row['longitud']
            )
            
            if distancia <= radio_km:
                empresas_dentro.append(row)
    
    return pd.DataFrame(empresas_dentro)

def analizar_concentracion(df_area):
    """
    Analiza concentración en un área específica
    """
    if len(df_area) == 0:
        return {
            'total_empresas': 0,
            'tipo_dominante': 'N/A',
            'porcentaje_dominante': 0,
            'densidad': 0,
            'sectores_principales': {},
            'total_empleados': 0,
            'empleados_promedio': 0
        }
    
    # Distribución por tamaño
    if 'tamano_empresa' in df_area.columns:
        distribucion = df_area['tamano_empresa'].value_counts()
        
        if not distribucion.empty:
            tipo_dominante = distribucion.index[0]
            porcentaje_dominante = (distribucion.iloc[0] / len(df_area)) * 100
        else:
            tipo_dominante = 'N/A'
            porcentaje_dominante = 0
    else:
        tipo_dominante = 'N/A'
        porcentaje_dominante = 0
    
    # Total empleados
    total_empleados = df_area['empleados_max'].sum() if 'empleados_max' in df_area.columns else 0
    
    # Sectores principales
    if 'nombre_act' in df_area.columns:
        sectores_principales = df_area['nombre_act'].value_counts().head(3).to_dict()
    else:
        sectores_principales = {}
    
    return {
        'total_empresas': len(df_area),
        'tipo_dominante': tipo_dominante,
        'porcentaje_dominante': porcentaje_dominante,
        'total_empleados': total_empleados,
        'sectores_principales': sectores_principales,
        'empleados_promedio': total_empleados / len(df_area) if len(df_area) > 0 else 0
    }