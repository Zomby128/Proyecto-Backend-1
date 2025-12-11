import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text

class DatabaseManager:
    def __init__(self, db_name="inegi_segmentacion.db"):
        self.db_name = db_name
        self.conn = None
        self.engine = None
    
    def connect(self):
        """Establece conexión a la base de datos SQLite"""
        self.conn = sqlite3.connect(self.db_name)
        self.engine = create_engine(f'sqlite:///{self.db_name}')
        return self.conn
    
    def create_tables(self):
        """Crea las tablas normalizadas"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Tabla: actividades_economicas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS actividades_economicas (
            id_actividad INTEGER PRIMARY KEY,
            codigo_act TEXT,
            nombre_act TEXT
        )
        ''')
        
        # Tabla: municipios
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS municipios (
            id_municipio INTEGER PRIMARY KEY,
            municipio TEXT,
            estado TEXT
        )
        ''')
        
        # Tabla: georreferencias
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS georreferencias (
            id_geo INTEGER PRIMARY KEY,
            latitud REAL,
            longitud REAL
        )
        ''')
        
        # Tabla: unidades_economicas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS unidades_economicas (
            id_unidad INTEGER PRIMARY KEY,
            razon_social TEXT,
            per_ocu TEXT,
            empleados_max INTEGER,
            tamano_empresa TEXT,
            telefono TEXT,
            correo_electronico TEXT,
            sitio_web TEXT,
            fecha_registro TEXT,
            id_actividad INTEGER,
            id_municipio INTEGER,
            id_geo INTEGER,
            FOREIGN KEY (id_actividad) REFERENCES actividades_economicas(id_actividad),
            FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio),
            FOREIGN KEY (id_geo) REFERENCES georreferencias(id_geo)
        )
        ''')
        
        conn.commit()
    
    def save_dataframe(self, df, table_name):
        """Guarda un DataFrame en la base de datos"""
        if self.engine is None:
            self.connect()
        
        df.to_sql(table_name, self.engine, 
                 if_exists='replace', index=False)
        print(f"💾 {table_name}: {len(df)} registros guardados")
    
    def query(self, sql, params=None):
        """Ejecuta una consulta SQL y retorna DataFrame"""
        if self.conn is None:
            self.connect()
        
        if params:
            return pd.read_sql_query(sql, self.conn, params=params)
        return pd.read_sql_query(sql, self.conn)
    
    def get_all_data(self):
        """Obtiene todos los datos combinados"""
        query = """
        SELECT 
            ue.*,
            m.municipio,
            m.estado,
            ae.nombre_act,
            g.latitud,
            g.longitud
        FROM unidades_economicas ue
        LEFT JOIN municipios m ON ue.id_municipio = m.id_municipio
        LEFT JOIN actividades_economicas ae ON ue.id_actividad = ae.id_actividad
        LEFT JOIN georreferencias g ON ue.id_geo = g.id_geo
        """
        
        return self.query(query)
    
    def get_summary(self):
        """Obtiene estadísticas resumidas"""
        queries = {
            'total_empresas': "SELECT COUNT(*) as count FROM unidades_economicas",
            'distribucion_tamano': "SELECT tamano_empresa, COUNT(*) as count FROM unidades_economicas GROUP BY tamano_empresa",
            'top_municipios': """
                SELECT m.municipio, COUNT(*) as count 
                FROM unidades_economicas ue
                JOIN municipios m ON ue.id_municipio = m.id_municipio
                GROUP BY m.municipio 
                ORDER BY count DESC 
                LIMIT 10
            """,
            'total_empleados': "SELECT SUM(empleados_max) as total FROM unidades_economicas"
        }
        
        results = {}
        for key, query in queries.items():
            df = self.query(query)
            results[key] = df
        
        return results
    
    def close(self):
        """Cierra la conexión"""
        if self.conn:
            self.conn.close()