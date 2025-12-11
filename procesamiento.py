import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
from src.database import DatabaseManager
from src.geo_utils import clasificar_tamano_inegi, extraer_empleados_max

def procesar_archivo_excel(archivo_path):
    """
    Procesa el archivo Excel con 3 hojas diferentes
    """
    print(f"📂 Leyendo archivo: {archivo_path}")
    
    try:
        # Leer nombres de las hojas
        xl = pd.ExcelFile(archivo_path)
        print(f"📋 Hojas encontradas: {xl.sheet_names}")
        
        # 1. Leer cada hoja
        print("\n📊 Cargando hoja 1 (actividades)...")
        df_actividades = pd.read_excel(archivo_path, sheet_name=0)
        print(f"   Columnas: {list(df_actividades.columns)}")
        print(f"   Registros: {len(df_actividades)}")
        print(f"   Primeras filas:")
        print(df_actividades.head())
        
        print("\n📊 Cargando hoja 2 (municipios)...")
        df_municipios_raw = pd.read_excel(archivo_path, sheet_name=1)
        print(f"   Columnas: {list(df_municipios_raw.columns)}")
        print(f"   Registros: {len(df_municipios_raw)}")
        print(f"   Primeras filas:")
        print(df_municipios_raw.head())
        
        print("\n📊 Cargando hoja 3 (coordenadas)...")
        df_geo_raw = pd.read_excel(archivo_path, sheet_name=2)
        print(f"   Columnas: {list(df_geo_raw.columns)}")
        print(f"   Registros: {len(df_geo_raw)}")
        print(f"   Primeras filas:")
        print(df_geo_raw.head())
        
        # 2. Verificar que todas las hojas tengan la misma cantidad de registros
        if len(df_actividades) == len(df_municipios_raw) == len(df_geo_raw):
            print(f"\n✅ Todas las hojas tienen {len(df_actividades)} registros (coinciden)")
        else:
            print(f"\n⚠️  Advertencia: Las hojas tienen diferente número de registros")
            print(f"   Hoja 1: {len(df_actividades)} registros")
            print(f"   Hoja 2: {len(df_municipios_raw)} registros")
            print(f"   Hoja 3: {len(df_geo_raw)} registros")
        
        # 3. Combinar los DataFrames usando el ID como clave
        print("\n🔄 Combinando datos de las 3 hojas...")
        
        # Crear un DataFrame base con el ID
        df_base = df_actividades.copy()
        
        # Añadir datos de municipios (hoja 2)
        # Asumimos que las filas están en el mismo orden
        df_base['codigo_municipio'] = df_municipios_raw['eye_mun'].values if 'eye_mun' in df_municipios_raw.columns else None
        df_base['municipio'] = df_municipios_raw['municipio'].values if 'municipio' in df_municipios_raw.columns else None
        df_base['estado'] = df_municipios_raw['entidad'].values if 'entidad' in df_municipios_raw.columns else None
        
        # Añadir datos geográficos (hoja 3)
        df_base['telefono'] = df_geo_raw['telefono'].values if 'telefono' in df_geo_raw.columns else None
        df_base['correo_electronico'] = df_geo_raw['correoelec'].values if 'correoelec' in df_geo_raw.columns else None
        df_base['sitio_web'] = df_geo_raw['www'].values if 'www' in df_geo_raw.columns else None
        df_base['latitud'] = df_geo_raw['latitud'].values if 'latitud' in df_geo_raw.columns else None
        df_base['longitud'] = df_geo_raw['longitud'].values if 'longitud' in df_geo_raw.columns else None
        df_base['fecha_registro'] = df_geo_raw['fecha_alta'].values if 'fecha_alta' in df_geo_raw.columns else None
        
        # 4. Clasificar tamaño de empresa
        print("\n🏢 Clasificando tamaños de empresa...")
        if 'per_ocu' in df_base.columns:
            df_base['tamano_empresa'] = df_base['per_ocu'].apply(clasificar_tamano_inegi)
            df_base['empleados_max'] = df_base['per_ocu'].apply(extraer_empleados_max)
            
            # Mostrar distribución
            distribucion = df_base['tamano_empresa'].value_counts()
            print("   Distribución por tamaño:")
            for tamano, cantidad in distribucion.items():
                porcentaje = (cantidad / len(df_base)) * 100
                print(f"     - {tamano}: {cantidad:,} ({porcentaje:.1f}%)")
        
        # 5. Normalizar datos
        print("\n🔄 Normalizando datos en tablas separadas...")
        
        # 5.1 Actividades económicas
        print("   Procesando actividades económicas...")
        actividades = df_base[['codigo_act', 'nombre_act']].drop_duplicates()
        actividades = actividades.reset_index(drop=True)
        actividades['id_actividad'] = range(1, len(actividades) + 1)
        print(f"     {len(actividades)} actividades únicas")
        
        # 5.2 Municipios
        print("   Procesando municipios...")
        municipios = df_base[['municipio', 'estado']].drop_duplicates()
        municipios = municipios.reset_index(drop=True)
        municipios['id_municipio'] = range(1, len(municipios) + 1)
        print(f"     {len(municipios)} municipios únicos")
        
        # Mostrar algunos municipios
        print("     Ejemplo de municipios:")
        for idx, row in municipios.head(5).iterrows():
            print(f"       - {row['municipio']}, {row['estado']}")
        
        # 5.3 Georreferencias
        print("   Procesando coordenadas geográficas...")
        # Filtrar y convertir coordenadas
        df_coords = df_base[['latitud', 'longitud']].copy()
        df_coords['latitud'] = pd.to_numeric(df_coords['latitud'], errors='coerce')
        df_coords['longitud'] = pd.to_numeric(df_coords['longitud'], errors='coerce')
        df_coords = df_coords.dropna()
        
        if len(df_coords) > 0:
            georreferencias = df_coords.drop_duplicates()
            georreferencias = georreferencias.reset_index(drop=True)
            georreferencias['id_geo'] = range(1, len(georreferencias) + 1)
            print(f"     {len(georreferencias)} ubicaciones únicas")
            
            # Mostrar rango de coordenadas
            print(f"     Latitud: {georreferencias['latitud'].min():.4f} a {georreferencias['latitud'].max():.4f}")
            print(f"     Longitud: {georreferencias['longitud'].min():.4f} a {georreferencias['longitud'].max():.4f}")
        else:
            georreferencias = pd.DataFrame(columns=['latitud', 'longitud', 'id_geo'])
            print("     ⚠️  No hay coordenadas válidas")
        
        # 6. Crear diccionarios para mapeo
        print("\n🔗 Creando relaciones entre tablas...")
        
        # Diccionario de actividades
        act_dict = dict(zip(
            actividades['codigo_act'].astype(str) + "_" + actividades['nombre_act'],
            actividades['id_actividad']
        ))
        
        # Diccionario de municipios
        mun_dict = dict(zip(
            municipios['municipio'] + "_" + municipios['estado'],
            municipios['id_municipio']
        ))
        
        # Diccionario de georreferencias (si hay datos)
        geo_dict = {}
        if len(georreferencias) > 0:
            for idx, row in georreferencias.iterrows():
                key = f"{row['latitud']:.6f}_{row['longitud']:.6f}"
                geo_dict[key] = row['id_geo']
        
        # 7. Asignar IDs foráneos al DataFrame principal
        print("   Asignando IDs foráneos...")
        
        # Actividades
        df_base['id_actividad'] = df_base.apply(
            lambda x: act_dict.get(
                str(x.get('codigo_act', '')) + "_" + str(x.get('nombre_act', '')), 
                None
            ), axis=1
        )
        
        # Municipios
        df_base['id_municipio'] = df_base.apply(
            lambda x: mun_dict.get(
                str(x.get('municipio', '')) + "_" + str(x.get('estado', '')), 
                None
            ), axis=1
        )
        
        # Georreferencias
        def obtener_id_geo(lat, lon):
            if pd.isna(lat) or pd.isna(lon):
                return None
            try:
                key = f"{float(lat):.6f}_{float(lon):.6f}"
                return geo_dict.get(key, None)
            except:
                return None
        
        df_base['id_geo'] = df_base.apply(
            lambda x: obtener_id_geo(x.get('latitud'), x.get('longitud')), 
            axis=1
        )
        
        # 8. Crear ID único para cada unidad económica
        df_base['id_unidad'] = range(1, len(df_base) + 1)
        
        # 9. Preparar tabla de unidades económicas
        print("\n📋 Preparando tabla de unidades económicas...")
        columnas_unidades = [
            'id_unidad', 'id', 'per_ocu', 'empleados_max', 'tamano_empresa',
            'telefono', 'correo_electronico', 'sitio_web', 'fecha_registro',
            'id_actividad', 'id_municipio', 'id_geo'
        ]
        
        # Filtrar columnas existentes
        columnas_existentes = [col for col in columnas_unidades if col in df_base.columns]
        unidades_economicas = df_base[columnas_existentes].copy()
        
        # Renombrar columnas
        unidades_economicas = unidades_economicas.rename(columns={
            'id': 'razon_social',
            'per_ocu': 'rango_empleados'
        })
        
        # Si 'razon_social' no tiene datos, usar ID
        if 'razon_social' in unidades_economicas.columns:
            if unidades_economicas['razon_social'].isnull().all():
                unidades_economicas['razon_social'] = 'Empresa ' + unidades_economicas['id_unidad'].astype(str)
        
        print(f"✅ Datos combinados: {len(df_base)} registros totales")
        print(f"   Unidades económicas: {len(unidades_economicas)}")
        print(f"   Actividades únicas: {len(actividades)}")
        print(f"   Municipios únicos: {len(municipios)}")
        print(f"   Ubicaciones geográficas: {len(georreferencias)}")
        
        return {
            'actividades': actividades.rename(columns={'codigo_act': 'codigo_actividad', 
                                                     'nombre_act': 'nombre_actividad'}),
            'municipios': municipios,
            'georreferencias': georreferencias,
            'unidades_economicas': unidades_economicas
        }
        
    except Exception as e:
        print(f"❌ Error al procesar archivo: {e}")
        import traceback
        traceback.print_exc()
        return None

def generar_analisis_basico(datos_normalizados):
    """Genera análisis básico"""
    print("\n📊 Generando análisis básico...")
    
    unidades = datos_normalizados['unidades_economicas']
    
    print("\n📋 RESUMEN FINAL:")
    print(f"   Total empresas: {len(unidades):,}")
    
    if 'empleados_max' in unidades.columns:
        total_emp = unidades['empleados_max'].sum()
        print(f"   Total empleados estimados: {int(total_emp):,}")
    
    if 'tamano_empresa' in unidades.columns:
        distribucion = unidades['tamano_empresa'].value_counts()
        print(f"\n   📏 Distribución por tamaño:")
        for tamano, cantidad in distribucion.items():
            porcentaje = (cantidad / len(unidades)) * 100
            print(f"     - {tamano}: {cantidad:,} ({porcentaje:.1f}%)")
    
    if 'municipios' in datos_normalizados and datos_normalizados['municipios'] is not None:
        municipios = datos_normalizados['municipios']
        print(f"\n   🏙️  Municipios cubiertos: {len(municipios)}")
        print("     Top 5 municipios:")
        for idx, row in municipios.head(5).iterrows():
            print(f"       - {row['municipio']}, {row['estado']}")
    
    # Exportar a Excel
    print("\n📄 Exportando datos...")
    
    with pd.ExcelWriter('resultados_proyecto.xlsx') as writer:
        # Hoja 1: Unidades económicas
        unidades.to_excel(writer, sheet_name='Unidades_Economicas', index=False)
        
        # Hoja 2: Resumen por tamaño
        if 'tamano_empresa' in unidades.columns:
            resumen_tamano = unidades['tamano_empresa'].value_counts().reset_index()
            resumen_tamano.columns = ['Tamaño_Empresa', 'Cantidad']
            resumen_tamano.to_excel(writer, sheet_name='Resumen_Tamaño', index=False)
        
        # Hoja 3: Actividades económicas
        if 'actividades' in datos_normalizados and datos_normalizados['actividades'] is not None:
            datos_normalizados['actividades'].to_excel(writer, sheet_name='Actividades', index=False)
        
        # Hoja 4: Municipios
        if 'municipios' in datos_normalizados and datos_normalizados['municipios'] is not None:
            datos_normalizados['municipios'].to_excel(writer, sheet_name='Municipios', index=False)
        
        # Hoja 5: Georreferencias
        if 'georreferencias' in datos_normalizados and datos_normalizados['georreferencias'] is not None:
            datos_normalizados['georreferencias'].to_excel(writer, sheet_name='Georreferencias', index=False)
    
    print("✅ Datos exportados: 'resultados_proyecto.xlsx'")

def main():
    print("=" * 60)
    print("🎯 SISTEMA DE SEGMENTACIÓN DE MERCADO - INEGI")
    print("=" * 60)
    
    # Ruta al archivo Excel
    archivo_path = "data/normalizada.xlsx"
    
    # 1. Procesar archivo
    datos_normalizados = procesar_archivo_excel(archivo_path)
    
    if datos_normalizados is None:
        print("❌ No se pudo procesar el archivo")
        return
    
    # 2. Crear base de datos
    print("\n💾 Creando base de datos...")
    db = DatabaseManager("inegi_segmentacion.db")
    db.create_tables()
    
    # 3. Guardar datos en la base de datos
    for tabla, datos in datos_normalizados.items():
        if datos is not None and not datos.empty:
            # Renombrar columnas para la base de datos
            if tabla == 'actividades':
                datos = datos.rename(columns={
                    'codigo_actividad': 'codigo_act',
                    'nombre_actividad': 'nombre_act'
                })
            db.save_dataframe(datos, tabla)
    
    # 4. Generar análisis básico
    generar_analisis_basico(datos_normalizados)
    
    # 5. Información final
    print("\n" + "=" * 60)
    print("✅ PROCESO COMPLETADO EXITOSAMENTE!")
    print("\n📁 ARCHIVOS GENERADOS:")
    print("   1. inegi_segmentacion.db  - Base de datos SQLite")
    print("   2. resultados_proyecto.xlsx - Todos los datos y análisis")
    print("\n🚀 PRÓXIMOS PASOS:")
    print("   1. Ejecutar dashboard completo: streamlit run dashboard.py")
    print("   2. Ejecutar mapa interactivo: streamlit run dashboard_mapa.py")
    print("=" * 60)

if __name__ == "__main__":
    main()