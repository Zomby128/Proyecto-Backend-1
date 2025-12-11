import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import plotly.graph_objects as go

class MarketAnalyzer:
    def __init__(self, df):
        self.df = df
    
    def get_summary(self):
        """Obtiene resumen general"""
        summary = {
            'total_empresas': len(self.df),
            'total_empleados': int(self.df['empleados_max'].sum()) if 'empleados_max' in self.df.columns else 0,
            'municipios_unicos': self.df['municipio'].nunique() if 'municipio' in self.df.columns else 0,
            'sectores_unicos': self.df['nombre_act'].nunique() if 'nombre_act' in self.df.columns else 0
        }
        
        if 'tamano_empresa' in self.df.columns:
            summary['distribucion_tamano'] = self.df['tamano_empresa'].value_counts().to_dict()
        
        if 'municipio' in self.df.columns:
            summary['top_municipios'] = self.df['municipio'].value_counts().head(5).to_dict()
        
        return summary
    
    def analyze_concentration_dbscan(self, eps=0.1, min_samples=10):
        """Analiza concentración usando DBSCAN"""
        if len(self.df) < min_samples:
            return {'clusters': 0, 'puntos_aislados': len(self.df)}
        
        # Filtrar coordenadas válidas
        coords = self.df[['latitud', 'longitud']].dropna().values
        
        if len(coords) < min_samples:
            return {'clusters': 0, 'puntos_aislados': len(coords)}
        
        # Escalar coordenadas
        scaler = StandardScaler()
        coords_scaled = scaler.fit_transform(coords)
        
        # Aplicar DBSCAN
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        clusters = dbscan.fit_predict(coords_scaled)
        
        n_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
        n_ruido = list(clusters).count(-1)
        
        return {
            'clusters': n_clusters,
            'puntos_aislados': n_ruido,
            'total_puntos': len(coords),
            'labels': clusters
        }
    
    def generate_reports(self, output_dir="reportes"):
        """Genera reportes en diferentes formatos"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Reporte por municipio
        if 'municipio' in self.df.columns:
            reporte_municipio = self.df.groupby('municipio').agg({
                'razon_social': 'count',
                'empleados_max': 'sum'
            }).reset_index()
            reporte_municipio.columns = ['Municipio', 'Cantidad_Empresas', 'Total_Empleados']
            reporte_municipio.to_csv(f"{output_dir}/reporte_municipios.csv", index=False)
        
        # Reporte por tamaño
        if 'tamano_empresa' in self.df.columns:
            reporte_tamano = self.df['tamano_empresa'].value_counts().reset_index()
            reporte_tamano.columns = ['Tamaño_Empresa', 'Cantidad']
            reporte_tamano.to_csv(f"{output_dir}/reporte_tamanos.csv", index=False)
        
        print(f"📁 Reportes guardados en: {output_dir}/")