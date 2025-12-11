import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.database import DatabaseManager
from shapely.geometry import Point, Polygon
import warnings
warnings.filterwarnings('ignore')

# Configuración
st.set_page_config(page_title="Dashboard Unificado INEGI", layout="wide")
st.title("🗺️ Dashboard Unificado - Análisis con Selección de Área")

# Conectar a base de datos
@st.cache_resource
def get_db():
    db = DatabaseManager()
    db.connect()
    return db

db = get_db()

# ============================================
# FUNCIONES CORREGIDAS
# ============================================

def filtrar_por_poligono(df, coordenadas_poligono):
    """Filtra empresas dentro de un polígono"""
    if not coordenadas_poligono or len(coordenadas_poligono) < 3:
        return pd.DataFrame()
    
    try:
        poligono = Polygon(coordenadas_poligono)
    except:
        return pd.DataFrame()
    
    empresas_dentro = []
    
    for idx, row in df.iterrows():
        try:
            lat = row['latitud'] if 'latitud' in df.columns else None
            lon = row['longitud'] if 'longitud' in df.columns else None
            
            if pd.notna(lat) and pd.notna(lon):
                punto = Point(lon, lat)
                if poligono.contains(punto):
                    empresas_dentro.append(row)
        except:
            continue
    
    return pd.DataFrame(empresas_dentro)

def filtrar_por_circulo(df, centro_lat, centro_lon, radio_km):
    """Filtra empresas dentro de un círculo - VERSIÓN CORREGIDA"""
    from math import radians, sin, cos, sqrt, atan2
    
    def haversine(lat1, lon1, lat2, lon2):
        """Calcula distancia entre dos puntos en la Tierra (km)"""
        R = 6371.0  # Radio de la Tierra en km
        
        # Convertir grados a radianes
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        # Diferencias
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Fórmula de Haversine
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return R * c
    
    empresas_dentro = []
    
    for idx, row in df.iterrows():
        try:
            lat = row['latitud'] if 'latitud' in df.columns else None
            lon = row['longitud'] if 'longitud' in df.columns else None
            
            if pd.notna(lat) and pd.notna(lon):
                distancia = haversine(centro_lat, centro_lon, lat, lon)
                
                if distancia <= radio_km:
                    empresas_dentro.append(row)
        except:
            continue
    
    return pd.DataFrame(empresas_dentro)

def calcular_coordenadas_circulo(centro_lat, centro_lon, radio_km, puntos=36):
    """Calcula coordenadas para dibujar un círculo en el mapa"""
    coordenadas = []
    
    for i in range(puntos + 1):
        angulo = 2 * np.pi * i / puntos
        
        # Conversión km a grados (aproximada)
        # 1° latitud ≈ 111 km
        # 1° longitud ≈ 111 km * cos(latitud)
        delta_lat = (radio_km / 111.32) * np.cos(angulo)
        delta_lon = (radio_km / (111.32 * np.cos(np.radians(centro_lat)))) * np.sin(angulo)
        
        lat = centro_lat + delta_lat
        lon = centro_lon + delta_lon
        
        coordenadas.append((lon, lat))
    
    return coordenadas

def analizar_concentracion(df_area):
    """Analiza concentración en un área específica"""
    if len(df_area) == 0:
        return {
            'total_empresas': 0,
            'tipo_dominante': 'N/A',
            'porcentaje_dominante': 0,
            'total_empleados': 0,
            'sectores_principales': {},
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

# ============================================
# INICIALIZACIÓN DE ESTADO - CORREGIDO
# ============================================

# Inicializar todas las variables de sesión
if 'click_coords' not in st.session_state:
    st.session_state.click_coords = None
if 'df_area' not in st.session_state:
    st.session_state.df_area = pd.DataFrame()
if 'analisis_area' not in st.session_state:
    st.session_state.analisis_area = None
if 'coordenadas_area' not in st.session_state:
    st.session_state.coordenadas_area = None
if 'area_type' not in st.session_state:
    st.session_state.area_type = "cuadro"
if 'centro_actual' not in st.session_state:
    st.session_state.centro_actual = None
if 'centro_por_defecto' not in st.session_state:
    st.session_state.centro_por_defecto = None

# Sidebar
st.sidebar.header("🔍 Filtros y Configuración")

# Cargar datos
@st.cache_data
def load_data():
    return db.get_all_data()

try:
    df = load_data()
    
    # Verificar que tenemos datos
    if len(df) == 0:
        st.error("No hay datos disponibles. Ejecuta primero: python procesamiento.py")
        st.stop()
    
    # ============================================
    # DETECCIÓN DE UBICACIÓN
    # ============================================
    
    # Determinar ubicación aproximada de los datos
    tiene_coordenadas = 'latitud' in df.columns and 'longitud' in df.columns
    
    if tiene_coordenadas:
        # Filtrar coordenadas válidas
        df_coords = df.dropna(subset=['latitud', 'longitud'])
        
        if len(df_coords) > 0:
            # Calcular centro de los datos
            centro_datos_lat = df_coords['latitud'].mean()
            centro_datos_lon = df_coords['longitud'].mean()
            
            # Guardar centro para usar por defecto
            st.session_state.centro_por_defecto = {
                'lat': centro_datos_lat,
                'lon': centro_datos_lon
            }
            
            # Si no hay centro actual, usar este
            if st.session_state.centro_actual is None:
                st.session_state.centro_actual = {
                    'lat': centro_datos_lat,
                    'lon': centro_datos_lon
                }
    
    # ============================================
    # FILTROS
    # ============================================
    
    st.sidebar.subheader("Filtros de Datos")
    
    # Municipios
    if 'municipio' in df.columns:
        municipios = sorted(df['municipio'].dropna().unique())
        municipios_lista = ["Todos"] + municipios[:50]
        filtro_municipio = st.sidebar.selectbox("Municipio", municipios_lista)
    else:
        filtro_municipio = "Todos"
    
    # Tamaños
    if 'tamano_empresa' in df.columns:
        tamanos = sorted(df['tamano_empresa'].dropna().unique())
        tamanos_lista = ["Todos"] + list(tamanos)[:20]
        filtro_tamano = st.sidebar.selectbox("Tamaño de Empresa", tamanos_lista)
    else:
        filtro_tamano = "Todos"
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if filtro_municipio != "Todos":
        df_filtrado = df_filtrado[df_filtrado['municipio'] == filtro_municipio]
    
    if filtro_tamano != "Todos":
        df_filtrado = df_filtrado[df_filtrado['tamano_empresa'] == filtro_tamano]
    
    # ============================================
    # OBTENER COORDENADAS
    # ============================================
    
    st.sidebar.subheader("📍 Obtener Coordenadas")
    
    st.sidebar.info("""
    **Para obtener coordenadas:**
    1. En el mapa, pasa el mouse sobre una empresa
    2. Anota la Latitud y Longitud que aparecen
    3. Pégala en los campos abajo
    """)
    
    # Entrada manual de coordenadas
    st.sidebar.markdown("**Ingresar coordenadas manualmente:**")
    
    col_lat, col_lon = st.sidebar.columns(2)
    
    with col_lat:
        # Valor por defecto inteligente
        if st.session_state.centro_actual:
            default_lat = st.session_state.centro_actual['lat']
        elif st.session_state.centro_por_defecto:
            default_lat = st.session_state.centro_por_defecto['lat']
        elif 'latitud' in df_filtrado.columns:
            df_coords_filtrado = df_filtrado.dropna(subset=['latitud', 'longitud'])
            default_lat = df_coords_filtrado['latitud'].mean() if len(df_coords_filtrado) > 0 else 0
        else:
            default_lat = 0
        
        lat_input = st.number_input(
            "Latitud",
            value=float(default_lat),
            format="%.6f",
            step=0.0001,
            key="lat_input"
        )
    
    with col_lon:
        if st.session_state.centro_actual:
            default_lon = st.session_state.centro_actual['lon']
        elif st.session_state.centro_por_defecto:
            default_lon = st.session_state.centro_por_defecto['lon']
        elif 'longitud' in df_filtrado.columns:
            df_coords_filtrado = df_filtrado.dropna(subset=['latitud', 'longitud'])
            default_lon = df_coords_filtrado['longitud'].mean() if len(df_coords_filtrado) > 0 else 0
        else:
            default_lon = 0
        
        lon_input = st.number_input(
            "Longitud",
            value=float(default_lon),
            format="%.6f",
            step=0.0001,
            key="lon_input"
        )
    
    # Botón para usar estas coordenadas
    if st.sidebar.button("📌 Usar estas coordenadas", use_container_width=True):
        st.session_state.click_coords = {'lat': lat_input, 'lon': lon_input}
        st.session_state.centro_actual = {'lat': lat_input, 'lon': lon_input}
        st.rerun()
    
    # Mostrar coordenadas guardadas
    if st.session_state.click_coords:
        st.sidebar.success("✅ **Coordenadas actuales:**")
        st.sidebar.write(f"Lat: `{st.session_state.click_coords['lat']:.6f}`")
        st.sidebar.write(f"Lon: `{st.session_state.click_coords['lon']:.6f}`")
    
    # ============================================
    # CONFIGURAR ÁREA DE ANÁLISIS
    # ============================================
    
    st.sidebar.subheader("⚙️ Configurar Área de Análisis")
    
    # Tipo de área
    area_type = st.sidebar.radio(
        "Tipo de área:",
        ["Cuadro/Rectángulo", "Círculo"],
        index=0 if st.session_state.area_type == "cuadro" else 1,
        key="area_type_radio"
    )
    
    st.session_state.area_type = "cuadro" if area_type == "Cuadro/Rectángulo" else "circulo"
    
    # Obtener centro actual
    if st.session_state.centro_actual:
        centro_actual_lat = st.session_state.centro_actual['lat']
        centro_actual_lon = st.session_state.centro_actual['lon']
    else:
        centro_actual_lat = lat_input
        centro_actual_lon = lon_input
    
    if area_type == "Cuadro/Rectángulo":
        st.sidebar.markdown("**Configurar cuadro:**")
        
        # Coordenadas del centro
        st.sidebar.write(f"**Centro:** {centro_actual_lat:.6f}, {centro_actual_lon:.6f}")
        
        # Tamaño del cuadro
        tamaño_cuadro = st.sidebar.slider(
            "Tamaño (lado en km)",
            min_value=0.1,
            max_value=20.0,
            value=2.0,
            step=0.1,
            key="tamaño_cuadro",
            help="Longitud de cada lado del cuadrado"
        )
        
        # Convertir km a grados (aproximado)
        tamaño_grados = tamaño_cuadro * 0.009
        
        # Calcular coordenadas
        lat_min = centro_actual_lat - tamaño_grados
        lat_max = centro_actual_lat + tamaño_grados
        lon_min = centro_actual_lon - tamaño_grados
        lon_max = centro_actual_lon + tamaño_grados
        
        # Mostrar resumen
        with st.sidebar.expander("📐 Ver detalles del cuadro", expanded=False):
            st.write(f"**Lado:** {tamaño_cuadro} km ≈ {tamaño_grados:.4f}°")
            st.write(f"**Área:** {tamaño_cuadro**2:.1f} km²")
            st.write(f"**Latitud:** {lat_min:.6f} a {lat_max:.6f}")
            st.write(f"**Longitud:** {lon_min:.6f} a {lon_max:.6f}")
        
        # Botón para analizar
        if st.sidebar.button("🔍 Analizar área cuadrada", use_container_width=True, type="primary", key="btn_cuadro"):
            coordenadas = [
                (lon_min, lat_min),
                (lon_max, lat_min),
                (lon_max, lat_max),
                (lon_min, lat_max),
                (lon_min, lat_min)
            ]
            
            try:
                df_area = filtrar_por_poligono(df_filtrado, coordenadas)
                st.session_state.df_area = df_area
                st.session_state.analisis_area = analizar_concentracion(df_area)
                st.session_state.coordenadas_area = coordenadas
                st.session_state.area_type = "cuadro"
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error al analizar área: {e}")
    
    else:  # Círculo
        st.sidebar.markdown("**Configurar círculo:**")
        
        # Coordenadas del centro
        st.sidebar.write(f"**Centro:** {centro_actual_lat:.6f}, {centro_actual_lon:.6f}")
        
        # Radio del círculo
        radio_km = st.sidebar.slider(
            "Radio (kilómetros)",
            min_value=0.1,
            max_value=20.0,
            value=2.0,
            step=0.1,
            key="radio_circulo_slider"
        )
        
        # Calcular área
        area_km2 = np.pi * (radio_km ** 2)
        
        # Mostrar información
        st.sidebar.metric("Área aproximada", f"{area_km2:.1f} km²")
        
        with st.sidebar.expander("📐 Ver detalles del círculo", expanded=False):
            st.write(f"**Radio:** {radio_km} km")
            st.write(f"**Diámetro:** {radio_km * 2} km")
            st.write(f"**Circunferencia:** {2 * np.pi * radio_km:.1f} km")
        
        # Botón para analizar - CORREGIDO
        if st.sidebar.button("🔍 Analizar área circular", use_container_width=True, type="primary", key="btn_circulo"):
            try:
                df_area = filtrar_por_circulo(df_filtrado, centro_actual_lat, centro_actual_lon, radio_km)
                st.session_state.df_area = df_area
                st.session_state.analisis_area = analizar_concentracion(df_area)
                
                # Guardar datos del círculo de manera consistente
                st.session_state.coordenadas_area = {
                    'type': 'circulo',
                    'centro': (centro_actual_lat, centro_actual_lon),
                    'radio': radio_km,
                    'coordenadas_dibujo': calcular_coordenadas_circulo(centro_actual_lat, centro_actual_lon, radio_km)
                }
                st.session_state.area_type = "circulo"
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error al analizar área circular: {str(e)}")
    
    # Botón para limpiar
    if st.sidebar.button("🗑️ Limpiar selección", use_container_width=True, key="btn_limpiar"):
        st.session_state.df_area = pd.DataFrame()
        st.session_state.analisis_area = None
        st.session_state.coordenadas_area = None
        st.session_state.click_coords = None
        st.session_state.centro_actual = None
        st.rerun()
    
    # ============================================
    # MÉTRICAS PRINCIPALES
    # ============================================
    
    st.subheader("📈 Métricas Principales")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Empresas totales", f"{len(df_filtrado):,}")
    with col2:
        if 'empleados_max' in df_filtrado.columns:
            empleados = df_filtrado['empleados_max'].sum()
            st.metric("Empleados totales", f"{int(empleados):,}")
        else:
            st.metric("Empleados totales", "N/A")
    with col3:
        if 'municipio' in df_filtrado.columns:
            municipios_count = df_filtrado['municipio'].nunique()
            st.metric("Municipios", municipios_count)
        else:
            st.metric("Municipios", "N/A")
    with col4:
        if 'nombre_act' in df_filtrado.columns:
            sectores = df_filtrado['nombre_act'].nunique()
            st.metric("Sectores", sectores)
        else:
            st.metric("Sectores", "N/A")
    
    # ============================================
    # MAPA INTERACTIVO - CORREGIDO
    # ============================================
    
    col_mapa, col_analisis = st.columns([2, 1])
    
    with col_mapa:
        st.subheader("🗺️ Mapa Interactivo")
        
        if tiene_coordenadas:
            # Filtrar coordenadas válidas
            mapa_df = df_filtrado.dropna(subset=['latitud', 'longitud'])
            
            if len(mapa_df) > 0:
                # Definir colores por tamaño
                color_map = {
                    'Micro': '#2ecc71',
                    'Pequeña': '#3498db',
                    'Mediana': '#e67e22',
                    'Grande': '#e74c3c',
                    'Sin información': '#95a5a6',
                    'Otro': '#9b59b6'
                }
                
                # Crear figura del mapa
                fig = go.Figure()
                
                # Agregar marcadores de empresas
                for tamano in mapa_df['tamano_empresa'].unique():
                    if pd.isna(tamano):
                        continue
                    
                    df_tamano = mapa_df[mapa_df['tamano_empresa'] == tamano]
                    color = color_map.get(str(tamano), '#95a5a6')
                    
                    # Crear texto para hover
                    hover_texts = []
                    for _, row in df_tamano.iterrows():
                        texto = f"<b>{row['razon_social']}</b><br>"
                        texto += f"Tamaño: {row['tamano_empresa']}<br>"
                        texto += f"📍 <b>Lat: {row['latitud']:.6f}</b><br>"
                        texto += f"📍 <b>Lon: {row['longitud']:.6f}</b><br>"
                        if 'municipio' in row:
                            texto += f"Municipio: {row['municipio']}<br>"
                        if 'rango_empleados' in row:
                            texto += f"Empleados: {row['rango_empleados']}"
                        hover_texts.append(texto)
                    
                    fig.add_trace(go.Scattermapbox(
                        lat=df_tamano['latitud'],
                        lon=df_tamano['longitud'],
                        mode='markers',
                        marker=dict(
                            size=8,
                            color=color,
                            opacity=0.7
                        ),
                        name=str(tamano),
                        text=hover_texts,
                        hoverinfo='text'
                    ))
                
                # Agregar área seleccionada si existe - CORREGIDO
                if st.session_state.coordenadas_area:
                    if st.session_state.area_type == "cuadro":
                        # Verificar que sea una lista (cuadro)
                        if isinstance(st.session_state.coordenadas_area, list):
                            lats = [p[1] for p in st.session_state.coordenadas_area]
                            lons = [p[0] for p in st.session_state.coordenadas_area]
                            
                            fig.add_trace(go.Scattermapbox(
                                lat=lats,
                                lon=lons,
                                mode='lines',
                                line=dict(width=3, color='red'),
                                fill='toself',
                                fillcolor='rgba(255, 0, 0, 0.15)',
                                name='Área seleccionada',
                                hoverinfo='text',
                                text=f"Área cuadrada: {len(st.session_state.df_area)} empresas"
                            ))
                    
                    else:  # círculo
                        # Verificar que sea un diccionario (círculo)
                        if isinstance(st.session_state.coordenadas_area, dict) and 'coordenadas_dibujo' in st.session_state.coordenadas_area:
                            coordenadas_circulo = st.session_state.coordenadas_area['coordenadas_dibujo']
                            lats = [p[1] for p in coordenadas_circulo]
                            lons = [p[0] for p in coordenadas_circulo]
                            
                            fig.add_trace(go.Scattermapbox(
                                lat=lats,
                                lon=lons,
                                mode='lines',
                                line=dict(width=3, color='red'),
                                fill='toself',
                                fillcolor='rgba(255, 0, 0, 0.15)',
                                name='Área seleccionada',
                                hoverinfo='text',
                                text=f"Área circular: {len(st.session_state.df_area)} empresas"
                            ))
                
                # Configurar centro del mapa - CORREGIDO
                if st.session_state.coordenadas_area:
                    if st.session_state.area_type == "cuadro" and isinstance(st.session_state.coordenadas_area, list):
                        # Centro del cuadro
                        lats = [p[1] for p in st.session_state.coordenadas_area[:-1]]
                        lons = [p[0] for p in st.session_state.coordenadas_area[:-1]]
                        centro_lat = sum(lats) / len(lats)
                        centro_lon = sum(lons) / len(lons)
                        zoom = 12
                    
                    elif st.session_state.area_type == "circulo" and isinstance(st.session_state.coordenadas_area, dict):
                        # Centro del círculo
                        centro_lat, centro_lon = st.session_state.coordenadas_area['centro']
                        zoom = 12
                    
                    else:
                        # Fallback a centro de datos
                        centro_lat = mapa_df['latitud'].mean()
                        centro_lon = mapa_df['longitud'].mean()
                        zoom = 10
                else:
                    # Centro en los datos
                    centro_lat = mapa_df['latitud'].mean()
                    centro_lon = mapa_df['longitud'].mean()
                    zoom = 10
                
                # Configurar layout
                fig.update_layout(
                    mapbox=dict(
                        style="open-street-map",
                        center=dict(lat=centro_lat, lon=centro_lon),
                        zoom=zoom
                    ),
                    margin={"r":0,"t":40,"l":0,"b":0},
                    height=600,
                    showlegend=True,
                    legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01,
    bgcolor='rgba(255, 255, 255, 0.85)',
    bordercolor='gray',
    borderwidth=1,
    font=dict(
        color='black',
        size=12
    )
)
,
                    title="Pasa el mouse sobre una empresa para ver sus coordenadas"
                )
                
                # Mostrar el mapa
                st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
                
                # Instrucciones
                st.info("""
                **🎯 ¿Cómo obtener coordenadas?**
                
                1. **Pasa el mouse** sobre cualquier empresa en el mapa
                2. **Anota** la **Latitud** y **Longitud** que aparecen
                3. **Pégalas** en los campos del sidebar
                4. **Selecciona** tipo de área (cuadro o círculo)
                5. **Ajusta** el tamaño (en kilómetros)
                6. **Haz clic** en "Analizar área"
                """)
                
                # Mostrar estadísticas
                with st.expander("📊 Estadísticas del mapa", expanded=False):
                    col_stat1, col_stat2 = st.columns(2)
                    
                    with col_stat1:
                        st.metric("Empresas visibles", f"{len(mapa_df):,}")
                    
                    with col_stat2:
                        if st.session_state.df_area is not None and len(st.session_state.df_area) > 0:
                            st.metric("Empresas en área", f"{len(st.session_state.df_area):,}")
                        else:
                            st.metric("Empresas en área", "0")
            
            else:
                st.warning("No hay empresas con coordenadas válidas después de aplicar los filtros")
        else:
            st.info("ℹ️ Los datos no contienen coordenadas geográficas")
    
    # ============================================
    # ANÁLISIS DEL ÁREA SELECCIONADA - CORREGIDO
    # ============================================
    
    with col_analisis:
        st.subheader("📊 Análisis del Área")
        
        # Mostrar análisis si hay área seleccionada
        if st.session_state.analisis_area is not None and len(st.session_state.df_area) > 0:
            analisis = st.session_state.analisis_area
            df_area = st.session_state.df_area
            
            st.success(f"✅ **{analisis['total_empresas']} empresas en el área**")
            
            # Mostrar tipo de área - CORREGIDO
            if st.session_state.area_type == "cuadro":
                st.caption("📐 **Área cuadrada**")
            elif st.session_state.area_type == "circulo":
                st.caption("⭕ **Área circular**")
            else:
                st.caption("📍 **Área seleccionada**")
            
            # Mostrar tipo dominante
            if analisis['tipo_dominante'] != 'N/A':
                color_dominante = {
                    'Micro': '#2ecc71',
                    'Pequeña': '#3498db',
                    'Mediana': '#e67e22',
                    'Grande': '#e74c3c'
                }.get(analisis['tipo_dominante'], '#95a5a6')
                
                st.markdown(f"**🏆 Empresa dominante:**")
                st.markdown(
                    f"<div style='background-color:{color_dominante}; color:white; padding:10px; "
                    f"border-radius:8px; text-align:center; font-size:18px; font-weight:bold; "
                    f"margin:5px 0;'>{analisis['tipo_dominante']}</div>",
                    unsafe_allow_html=True
                )
                
                st.metric("Porcentaje", f"{analisis['porcentaje_dominante']:.1f}%")
            
            # Métricas adicionales
            col_met1, col_met2 = st.columns(2)
            with col_met1:
                if analisis['total_empleados'] > 0:
                    st.metric("Total empleados", f"{analisis['total_empleados']:,}")
            with col_met2:
                if analisis['empleados_promedio'] > 0:
                    st.metric("Promedio/empresa", f"{analisis['empleados_promedio']:.1f}")
            
            # Gráfico de distribución
            if 'tamano_empresa' in df_area.columns:
                st.subheader("📈 Distribución")
                
                distribucion = df_area['tamano_empresa'].value_counts()
                
                if not distribucion.empty:
                    fig_pastel = px.pie(
                        values=distribucion.values,
                        names=distribucion.index,
                        color=distribucion.index,
                        color_discrete_map={
                            'Micro': '#2ecc71',
                            'Pequeña': '#3498db',
                            'Mediana': '#e67e22',
                            'Grande': '#e74c3c'
                        }
                    )
                    
                    fig_pastel.update_layout(
                        height=220,
                        showlegend=True,
                        margin=dict(t=10, b=10, l=10, r=10)
                    )
                    st.plotly_chart(fig_pastel, use_container_width=True)
            
            # Top sectores
            if analisis['sectores_principales']:
                st.subheader("🏭 Sectores principales")
                for sector, cantidad in analisis['sectores_principales'].items():
                    porcentaje = (cantidad / len(df_area)) * 100
                    st.write(f"• **{sector[:30]}...** - {cantidad} ({porcentaje:.1f}%)")
            
            # Listar empresas
            with st.expander("📄 Ver empresas", expanded=False):
                if len(df_area) > 0:
                    # Columnas disponibles
                    columnas_disponibles = [c for c in ['razon_social', 'tamano_empresa', 'municipio', 'nombre_act'] 
                                          if c in df_area.columns]
                    
                    if columnas_disponibles:
                        st.dataframe(
                            df_area[columnas_disponibles].head(20),
                            use_container_width=True,
                            height=200
                        )
                        
                        if len(df_area) > 20:
                            st.caption(f"Mostrando 20 de {len(df_area)} empresas")
        
        else:
            st.info("🎯 **Configura un área para ver el análisis**")
            
            with st.expander("📋 Instrucciones rápidas", expanded=True):
                st.markdown("""
                1. **Obtén coordenadas** del mapa (pasa mouse sobre empresa)
                2. **Pégalas** en el sidebar
                3. **Selecciona** tipo de área
                4. **Ajusta** el tamaño
                5. **Haz clic** en "Analizar área"
                
                **Resultados que verás:**
                - Número de empresas en el área
                - Tipo de empresa dominante
                - Distribución por tamaño
                - Sectores principales
                - Lista de empresas
                """)

except Exception as e:
    st.error(f"Error al cargar datos: {str(e)}")
    import traceback
    st.code(traceback.format_exc())

# Footer
st.markdown("---")
st.markdown("**Proyecto Backend I - Segmentación de Mercado INEGI**")
