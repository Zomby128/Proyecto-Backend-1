import numpy as np
from shapely.geometry import Point, Polygon
import geopandas as gpd

def filtrar_por_poligono(df, coordenadas_poligono):
    """
    Filtra empresas dentro de un polígono
    coordenadas_poligono: lista de tuples [(lon1, lat1), (lon2, lat2), ...]
    """
    poligono = Polygon(coordenadas_poligono)
    
    empresas_dentro = []
    for idx, row in df.iterrows():
        punto = Point(row['longitud'], row['latitud'])
        if poligono.contains(punto):
            empresas_dentro.append(row)
    
    return pd.DataFrame(empresas_dentro)

def filtrar_por_circulo(df, centro_lat, centro_lon, radio_km):
    """
    Filtra empresas dentro de un círculo
    centro_lat, centro_lon: coordenadas del centro
    radio_km: radio en kilómetros
    """
    empresas_dentro = []
    
    for idx, row in df.iterrows():
        distancia = haversine_distance(
            centro_lat, centro_lon,
            row['latitud'], row['longitud']
        )
        
        if distancia <= radio_km:
            empresas_dentro.append(row)
    
    return pd.DataFrame(empresas_dentro)

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calcula distancia en km entre dos puntos usando fórmula de Haversine
    """
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Radio de la Tierra en km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

def calcular_densidad_empresarial(df, area_km2):
    """
    Calcula densidad empresarial (empresas por km²)
    """
    if area_km2 > 0:
        return len(df) / area_km2
    return 0

def analizar_concentracion_zona(df):
    """
    Analiza concentración en una zona específica
    """
    if len(df) == 0:
        return {
            'total_empresas': 0,
            'tipo_dominante': 'N/A',
            'porcentaje_dominante': 0,
            'densidad': 0
        }
    
    # Distribución por tamaño
    distribucion = df['tamano_empresa'].value_counts()
    
    if not distribucion.empty:
        tipo_dominante = distribucion.index[0]
        porcentaje_dominante = (distribucion.iloc[0] / len(df)) * 100
    else:
        tipo_dominante = 'N/A'
        porcentaje_dominante = 0
    
    # Total empleados
    total_empleados = df['empleados_max'].sum() if 'empleados_max' in df.columns else 0
    
    # Sectores principales
    sectores_principales = df['nombre_actividad'].value_counts().head(3).to_dict()
    
    return {
        'total_empresas': len(df),
        'tipo_dominante': tipo_dominante,
        'porcentaje_dominante': porcentaje_dominante,
        'total_empleados': total_empleados,
        'sectores_principales': sectores_principales,
        'empleados_promedio': total_empleados / len(df) if len(df) > 0 else 0
    }