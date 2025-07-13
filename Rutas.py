# INSTALAR LO SIGUIENTE:
# pip install streamlit
# streamlit hello
# pip install streamlit-folium folium
# CALCULA Hash

import streamlit as st
import pandas as pd
import json
import re # Para parsear las cadenas de latLng
from streamlit_folium import st_folium
import folium
from datetime import datetime, date
import hashlib # <-- Importado para calcular hashes
import io # <-- Importado para manejar el contenido del archivo

st.set_page_config(layout="wide")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
        /* Import Font Awesome for icons */
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css');

        html, body, [class*="st-"] {
            font-family: "Inter", sans-serif;
            color: #333;
        }
        /* Estilo para la descripción de la herramienta */
        .tool-description {
            text-align: center;
            margin-top: 10px;
            margin-bottom: 20px;
            padding: 10px 20px;
            background-color: #e6f7ff; /* Un azul muy claro */
            border-left: 5px solid #007bff; /* Borde azul para destacar */
            border-radius: 8px;
            color: #333;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        }
        .tool-description p {
            font-size: 0.85em; /* Ajusta este valor para hacer la letra más pequeña */
            margin: 0; /* Elimina el margen por defecto de los párrafos si no lo necesitas */
        }
        /* Estilo para la firma profesional */
        .professional-signature {
            text-align: center;
            margin-top: 30px;
            padding: 15px;
            background-color: #e9ecef; /* Un gris claro para el fondo */
            border-radius: 8px;
            border: 1px solid #ced4da;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        }
        .professional-signature p {
            margin: 5px 0;
            font-size: 0.95em;
            color: #495057;
        }
        .professional-signature strong {
            color: #212529;
            font-size: 1.1em;
        }
        /* Estilos para el título principal con icono */
        .main-title-container {
            display: flex;
            align-items: center;
            justify-content: center; /* Centra el título y el icono */
            gap: 10px; /* Espacio entre el icono y el texto */
            margin-bottom: 20px;
        }
        .main-title-container h1 {
            margin: 0;
            padding: 0;
            font-size: 2.5em; /* Ajusta el tamaño del título si es necesario */
            color: #2c3e50; /* Color oscuro para el título */
        }
        .main-title-container .fa-solid {
            font-size: 1.2em; /* Tamaño del icono */
            color: #3498db; /* Color del icono */
        }
        /* Estilos para la información y hashes */
        .hash-info-box {
            background-color: #e7f3ff; /* Light blue for information */
            border-left: 5px solid #2196F3; /* Blue border on the left */
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            font-size: 0.9em;
            color: #333;
            width: 100%; /* Asegura que ocupe todo el ancho disponible */
        }
        .hash-info-box strong {
            color: #0056b3;
        }
        .hash-info-box .hash-value {
            display: inline-block; /* Permite aplicar padding y background sin romper la línea */
            word-break: break-all; /* Permite que los hashes largos se rompan en cualquier punto */
            color: #495057; /* Color gris oscuro para los hashes */
            padding: 0px 0px; /* Espaciado interno para el hash */
            border-radius: 4px; /* Bordes ligeramente redondeados para el hash */
            font-size: 0.95em; /* Ligeramente más grande para el hash */
            margin-left: 5px; /* Pequeño margen para separar del label */
        }
    </style>
""", unsafe_allow_html=True)

# Título de la aplicación con icono
st.markdown("""
    <div class="main-title-container">
        <i class="fa-solid fa-map-location-dot"></i> <h1>GeoSenda - Visualizador de Rutas de Google</h1>
    </div>
""", unsafe_allow_html=True)

# Descripción de la herramienta
st.markdown("""
    <div class="tool-description">
        <p>Esta aplicación, diseñada por Marcelo G. Montiel, Analista Universitario de Sistemas - Universidad Tecnológica Nacional, Especialista en Pericias Informáticas, tiene como objetivo principal ofrecer una visualización mejorada de los datos de rutas exportados de Google. Su interfaz gráfica facilita una lectura y análisis más eficientes de las ubicaciones y trayectorias. Incluye funcionalidades técnicas, como el cálculo de hashes, lo cual es de particular relevancia en el ámbito de las Pericias Informáticas para la verificación de la integridad de los datos. El código fuente de esta herramienta está disponible para aquellos interesados en su estudio y aplicación.</p>
        <p><strong>"Que la sabiduría no sea humillación para tú prójimo. Omar Khayyam".</strong></p>
    </div>
""", unsafe_allow_html=True)


# Sección desplegable para la explicación de los campos
with st.expander("ℹ️ Explicación de los Campos de la Tabla"):
    st.markdown("""
    A continuación, se presenta una explicación detallada de los campos que encontrarás en la tabla, incluyendo su nombre original en inglés y su traducción al español, **junto con los valores que pueden tomar y su significado**:

    | Nombre de Campo (en tabla) | Nombre de Campo Original (si aplica) | Traducción al Español | Explicación |
    |---|---|---|---|
    | `Hora de Inicio` | `startTime` | Hora de Inicio | La marca de tiempo de inicio del segmento en formato ISO 8601 (YYYY-MM-DDTHH:MM:SS.mmm-ZonaHoraria). Por ejemplo: `2024-01-16T09:00:00.000-03:00`. |
    | `Hora de Fin` | `endTime` | Hora de Fin | La marca de tiempo de finalización del segmento en formato ISO 8601 (YYYY-MM:DDTHH:MM:SS.mmm-ZonaHoraria). Por ejemplo: `2024-01-16T11:00:00.000-03:00`. |
    | `Desplazamiento UTC Inicio (Minutos)` | `startTimeTimezoneUtcOffsetMinutes` | Desplazamiento de Zona Horaria UTC de Inicio (Minutos) | El desplazamiento en minutos de la zona horaria UTC para la hora de inicio del segmento. **Valor:** Número entero (ej. `-180` para -03:00). |
    | `Desplazamiento UTC Fin (Minutos)` | `endTimeTimezoneUtcOffsetMinutes` | Desplazamiento de Zona Horaria UTC de Fin (Minutos) | El desplazamiento en minutos de la zona horaria UTC para la hora de finalización del segmento. **Valor:** Número entero (ej. `-180` para -03:00). |
    | `Tipo de Segmento` | - | Tipo de Segmento | Indica si el segmento es una `Ruta`, una `Visita` o una `Actividad`.<br>**Valores Posibles:**<br>- `Ruta`: Un desplazamiento continuo entre puntos geográficos.<br>- `Visita`: Una estancia en un lugar específico, como una casa o un negocio.<br>- `Actividad`: Una actividad de movimiento, como caminar, conducir o estar quieto, pero que no necesariamente se asocia a una ruta detallada o un lugar específico de visita. |
    | `Descripción del Segmento` | - | Descripción del Segmento | Una breve descripción del segmento, indicando el tipo de actividad o lugar, generada por la aplicación para facilitar la comprensión. |
    | `Detalle_Trayectoria` | `timelinePath` | Detalle de Trayectoria | Indica si este segmento es una ruta y, si lo es, el número de puntos que la componen. Si es una `Visita` o `Actividad`, indica "No aplica". |
    | `Latitud/Longitud (Inicio)` | `latLng` (en `start`/`timelinePath`) | Latitud y Longitud (Inicio) | Las coordenadas de latitud y longitud del punto de inicio de una actividad o ruta. **Formato:** `latitud°, longitud°` (ej. `-26.8106089°, -65.2372888°`). |
    | `Latitud/Longitud (Fin)` | `latLng` (en `end`/`timelinePath`) | Latitud y Longitud (Fin) | Las coordenadas de latitud y longitud del punto final de una actividad o ruta. **Formato:** `latitud°, longitud°` (ej. `-26.8094538°, -65.2325117°`). |
    | `Distancia (Metros)` | `distanceMeters` | Distancia (Metros) | La distancia total recorrida durante una actividad en metros. **Valor:** Número entero o decimal positivo. |
    | `ID del Lugar` | `placeId` | ID del Lugar | Un identificador único de Google Places para el lugar visitado. Es un string alfanumérico. |
    | `Tipo Semántico` | `semanticType` | Tipo Semántico | El tipo de lugar inferido por Google.<br>**Valores Posibles:**<br>- `INFERRED_HOME`: Lugar inferido como el hogar del usuario.<br>- `INFERRED_WORK`: Lugar inferido como el trabajo del usuario.<br>- `UNKNOWN`: El sistema no pudo inferir un tipo semántico específico.<br>- Otros valores como `INFERRED_SCHOOL`, `INFERRED_STATION`, `INFERRED_AIRPORT`, `INFERRED_SHOPPING_CENTER`, etc., son posibles pero menos comunes en los ejemplos. |
    | `Probabilidad (Visita/Actividad)` | `probability` | Probabilidad (Visita/Actividad) | La probabilidad o nivel de confianza de que este sea el lugar o tipo de actividad correcto.<br>**Rango de Valores:** De `0.0` (0% de probabilidad) a `1.0` (100% de probabilidad). Valores más cercanos a `1.0` indican mayor certeza. |
    | `Nivel de Jerarquía` | `hierarchyLevel` | Nivel de Jerarquía | Un valor numérico que indica el nivel de anidamiento de la visita. Por ejemplo, una visita a un centro comercial grande puede tener un nivel de jerarquía, y una tienda específica dentro de él, otro.<br>**Valores Posibles:** Típicamente números enteros no negativos (`0`, `1`, `2`, etc.). |
    | `Tipo de Actividad (Top Candidato)` | `type` (en `activity.topCandidate`) | Tipo de Actividad (Candidato Principal) | El tipo de actividad principal inferido para un segmento de tipo `Actividad`.<br>**Valores Posibles:**<br>- `IN_PASSENGER_VEHICLE`: En un vehículo de pasajeros.<br>- `WALKING`: Caminando.<br>- `STILL`: Quieto, sin moverse.<br>- `UNKNOWN`: El sistema no pudo inferir el tipo de actividad.<br>- Otros como `ON_BICYCLE` (en bicicleta), `ON_FOOT` (a pie, genérico), `RUNNING` (corriendo), `IN_TRAIN` (en tren), `IN_BUS` (en autobús), `IN_TRAM` (en tranvía), `IN_SUBWAY` (en metro), etc. |
    """)

# Función para parsear la cadena "latitud°, longitud°" a una tupla (lat, lng)
def parse_lat_lng(lat_lng_str):
    if isinstance(lat_lng_str, str) and '°' in lat_lng_str:
        try:
            parts = lat_lng_str.replace('°', '').split(',')
            lat = float(parts[0].strip())
            lng = float(parts[1].strip())
            return (lat, lng)
        except (ValueError, IndexError):
            return None
    return None

# --- Carga del archivo JSON ---
uploaded_file = st.file_uploader(
    "Sube tu archivo JSON de rutas",
    type="json"
)

if uploaded_file is not None:
    # Leer el contenido del archivo en bytes para los hashes y la carga JSON
    file_content = uploaded_file.getvalue()

    # Calcular tamaño del archivo
    file_size_bytes = len(file_content)
    # Formatear el tamaño para una mejor lectura
    if file_size_bytes < 1024:
        file_size_str = f"{file_size_bytes} Bytes"
    elif file_size_bytes < (1024 * 1024):
        file_size_str = f"{file_size_bytes / 1024:.2f} KB"
    else:
        file_size_str = f"{file_size_bytes / (1024 * 1024):.2f} MB"

    # Calcular SHA256 hash
    sha256_hash = hashlib.sha256(file_content).hexdigest()

    # Calcular MD5 hash
    md5_hash = hashlib.md5(file_content).hexdigest()

    # --- Mostrar información del archivo y hashes (dentro de un expander) ---
    with st.expander("📊 Información y Hashes del Archivo Cargado", expanded=True):
        st.markdown(f"""
            <div class="hash-info-box">
                <div><strong>Nombre del Archivo:</strong> {uploaded_file.name}</div>
                <div><strong>Tamaño:</strong> {file_size_str}</div>
                <div><strong>Hash SHA256:</strong> <span class="hash-value">{sha256_hash}</span></div>
                <div><strong>Hash MD5:</strong> <span class="hash-value">{md5_hash}</span></div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("---") # Separador visual para el contenido siguiente

    # Ahora cargar el JSON desde el contenido en bytes
    try:
        data = json.load(io.BytesIO(file_content))
        st.success("Archivo JSON cargado exitosamente.")

        raw_processed_data = [] # Data sin filtrar por fecha aún
        
        if "semanticSegments" in data:
            for segment in data["semanticSegments"]:
                row = {
                    "Hora de Inicio": segment.get("startTime"),
                    "Hora de Fin": segment.get("endTime"),
                    "Desplazamiento UTC Inicio (Minutos)": segment.get("startTimeTimezoneUtcOffsetMinutes"),
                    "Desplazamiento UTC Fin (Minutos)": segment.get("endTimeTimezoneUtcOffsetMinutes"),
                    "Tipo de Segmento": "N/A",
                    "Descripción del Segmento": "N/A",
                    "Detalle_Trayectoria": "No aplica", 
                    "Latitud/Longitud (Inicio)": "N/A",
                    "Latitud/Longitud (Fin)": "N/A",
                    "Distancia (Metros)": "N/A",
                    "ID del Lugar": "N/A",
                    "Tipo Semántico": "N/A",
                    "Probabilidad (Visita/Actividad)": "N/A",
                    "Nivel de Jerarquía": "N/A",
                    "Tipo de Actividad (Top Candidato)": "N/A",
                    "Path_Coordinates": [] 
                }

                if "timelinePath" in segment:
                    row["Tipo de Segmento"] = "Ruta"
                    path_points = []
                    if segment["timelinePath"]:
                        start_point_str = segment["timelinePath"][0].get("point")
                        end_point_str = segment["timelinePath"][-1].get("point")
                        row["Latitud/Longitud (Inicio)"] = start_point_str if start_point_str else "N/A"
                        row["Latitud/Longitud (Fin)"] = end_point_str if end_point_str else "N/A"

                        for path_data in segment["timelinePath"]:
                            point_loc = parse_lat_lng(path_data.get("point"))
                            if point_loc:
                                path_points.append(point_loc)
                        row["Path_Coordinates"] = path_points 
                        row["Detalle_Trayectoria"] = f"Trayectoria ({len(path_points)} puntos)" if path_points else "Sin puntos" 
                        
                    row["Descripción del Segmento"] = "Movimiento a lo largo de una ruta."
                elif "visit" in segment:
                    row["Tipo de Segmento"] = "Visita"
                    visit_data = segment["visit"]
                    row["Nivel de Jerarquía"] = visit_data.get("hierarchyLevel")
                    row["Probabilidad (Visita/Actividad)"] = visit_data.get("probability")
                    if "topCandidate" in visit_data:
                        candidate = visit_data["topCandidate"]
                        row["ID del Lugar"] = candidate.get("placeId")
                        row["Tipo Semántico"] = candidate.get("semanticType")
                        row["Probabilidad (Visita/Actividad)"] = candidate.get("probability") 
                        if "placeLocation" in candidate and "latLng" in candidate["placeLocation"]:
                            lat_lng_str = candidate["placeLocation"]["latLng"]
                            row["Latitud/Longitud (Inicio)"] = lat_lng_str 
                    row["Descripción del Segmento"] = f"Estancia en un lugar. Tipo Semántico: {row['Tipo Semántico'] if row['Tipo Semántico'] != 'N/A' else 'Desconocido'}."
                    row["Detalle_Trayectoria"] = "No aplica (Visita)" 
                elif "activity" in segment:
                    row["Tipo de Segmento"] = "Actividad"
                    activity_data = segment["activity"]
                    if "start" in activity_data and "latLng" in activity_data["start"]:
                        row["Latitud/Longitud (Inicio)"] = activity_data["start"]["latLng"]
                    if "end" in activity_data and "latLng" in activity_data["end"]:
                        row["Latitud/Longitud (Fin)"] = activity_data["end"]["latLng"]
                    row["Distancia (Metros)"] = activity_data.get("distanceMeters")
                    if "topCandidate" in activity_data:
                        row["Tipo de Actividad (Top Candidato)"] = activity_data['topCandidate'].get('type')
                        row["Probabilidad (Visita/Actividad)"] = activity_data['topCandidate'].get('probability')
                        row["Descripción del Segmento"] = f"Tipo: {row['Tipo de Actividad (Top Candidato)'] if row['Tipo de Actividad (Top Candidato)'] != 'N/A' else 'Desconocido'} (Prob: {row['Probabilidad (Visita/Actividad)'] if row['Probabilidad (Visita/Actividad)'] != 'N/A' else 'N/A'})"
                    else:
                        row["Descripción del Segmento"] = "Actividad de movimiento."
                    row["Detalle_Trayectoria"] = "No aplica (Actividad)" 

                raw_processed_data.append(row)
        
        if raw_processed_data:
            df_full = pd.DataFrame(raw_processed_data)
            
            df_full['Hora de Inicio_dt'] = pd.to_datetime(df_full['Hora de Inicio'])
            df_full['Hora de Fin_dt'] = pd.to_datetime(df_full['Hora de Fin'])

            min_date = df_full['Hora de Inicio_dt'].min().date() if not df_full.empty else date.today()
            max_date = df_full['Hora de Fin_dt'].max().date() if not df_full.empty else date.today()

            st.write("### Seleccionar Rango de Fechas")
            if min_date > max_date:
                min_date, max_date = max_date, min_date 
                
            date_range = st.slider(
                "Selecciona un rango de fechas:",
                min_value=min_date,
                max_value=max_date,
                value=(min_date, max_date),
                format="YYYY-MM-DD", 
                key="date_filter"
            )

            if len(date_range) == 2:
                start_filter_date = date_range[0] 
                end_filter_date = date_range[1]
                df_filtered = df_full[
                    (df_full['Hora de Inicio_dt'].dt.date >= start_filter_date) &
                    (df_full['Hora de Inicio_dt'].dt.date <= end_filter_date)
                ].copy() 
            else:
                df_filtered = df_full.copy()

            all_visit_locations = []
            all_route_polylines = []
            
            for index, row in df_filtered.iterrows():
                if row['Tipo de Segmento'] == 'Visita':
                    loc = parse_lat_lng(row['Latitud/Longitud (Inicio)'])
                    if loc:
                        all_visit_locations.append(loc)
                elif row['Tipo de Segmento'] == 'Ruta':
                    if row['Path_Coordinates']:
                        all_route_polylines.append(row['Path_Coordinates'])

            st.write("### Mapa de Ubicaciones")
            
            default_center = [-26.8106089, -65.2372888] # San Miguel de Tucumán, Argentina
            
            map_center = default_center
            map_zoom = 12

            all_map_points = all_visit_locations[:] 
            for polyline in all_route_polylines:
                all_map_points.extend(polyline) 

            m = folium.Map(location=map_center, zoom_start=map_zoom)

            if all_map_points:
                latitudes = [p[0] for p in all_map_points]
                longitudes = [p[1] for p in all_map_points]
                
                if min(latitudes) != max(latitudes) or min(longitudes) != max(longitudes):
                    bounds = [[min(latitudes), min(longitudes)], [max(latitudes), max(longitudes)]]
                    m.fit_bounds(bounds) 
                else: 
                    m.location = all_map_points[0]
                    m.zoom_start = 15 
                
            for loc in all_visit_locations:
                folium.Marker(
                    location=loc,
                    popup=f"Visita: {loc[0]:.4f}, {loc[1]:.4f}",
                    icon=folium.Icon(color='green', icon='info-sign') 
                ).add_to(m)

            for polyline_coords in all_route_polylines:
                if len(polyline_coords) > 1: 
                    folium.PolyLine(
                        locations=polyline_coords,
                        color='blue', 
                        weight=5,
                        opacity=0.8,
                        popup="Ruta Recorrida"
                    ).add_to(m)

            st_folium(m, width="100%", height=700, key="folium_map", returned_objects=[])

            st.write("### Datos de Rutas Filtrados")
            
            df_display = df_filtered.drop(columns=['Hora de Inicio_dt', 'Hora de Fin_dt', 'Path_Coordinates']) 

            # --- NUEVOS FILTROS Y ORDENAMIENTO ---
            st.subheader("Opciones de Filtrado y Ordenamiento de Tabla")

            col1, col2 = st.columns(2)

            with col1:
                # Filtrado por columna
                filter_column = st.selectbox(
                    "Selecciona una columna para filtrar:",
                    ['Selecciona una'] + list(df_display.columns),
                    key="filter_column_select"
                )

                if filter_column != 'Selecciona una':
                    if filter_column == "Tipo de Segmento":
                        unique_values = df_display[filter_column].unique()
                        selected_values = st.multiselect(
                            f"Selecciona valores para filtrar por '{filter_column}':",
                            options=unique_values,
                            key="filter_value_multiselect"
                        )
                        if selected_values:
                            df_display = df_display[df_display[filter_column].isin(selected_values)]
                    else:
                        # Para otras columnas (texto o numéricas), usar text_input para búsqueda de contenido
                        filter_value = st.text_input(
                            f"Introduce texto/valor para filtrar por '{filter_column}':",
                            key="filter_value_text"
                        )
                        if filter_value:
                            # Convertir la columna a string para asegurar el método .str.contains()
                            df_display = df_display[df_display[filter_column].astype(str).str.contains(filter_value, case=False, na=False)]
            
            with col2:
                # Ordenamiento por columna
                sort_column = st.selectbox(
                    "Ordenar por columna:",
                    ['Selecciona una'] + list(df_display.columns),
                    key="sort_column_select"
                )

                if sort_column != 'Selecciona una':
                    sort_order = st.radio(
                        "Orden:",
                        ("Ascendente", "Descendente"),
                        key="sort_order_radio"
                    )
                    ascending = True if sort_order == "Ascendente" else False
                    df_display = df_display.sort_values(by=sort_column, ascending=ascending)

            st.dataframe(
                df_display, 
                use_container_width=True, 
                height=500, 
                hide_index=True 
            )
            
            if df_display.empty: # Se debe verificar df_display aquí, después de todos los filtros y órdenes
                st.info("No hay datos para las fechas y filtros seleccionados.")
            else:
                st.info("La tabla y el mapa muestran datos filtrados por el rango de fechas y opciones adicionales seleccionadas.")

        else:
            st.warning("El archivo JSON no contiene segmentos semánticos o está vacío.")

    except json.JSONDecodeError:
        st.error(
            "Error al decodificar el archivo JSON. "
            "Asegúrate de que el archivo no esté corrupto y tenga el formato JSON correcto."
        )
    except Exception as e:
        st.error(f"Ocurrió un error inesperado al procesar el archivo: {e}")

else:
    st.info("Por favor, sube un archivo JSON para comenzar.")

# Información profesional al final de la aplicación
st.markdown("""
    <div class="professional-signature">
        <p>Diseñado por <strong>Marcelo G. Montiel</strong></p>
        <p>Analista Universitario de Sistemas - Universidad Tecnológica Nacional</p>
        <p>San Miguel de Tucumán, Tucumán, Argentina</p>
    </div>
""", unsafe_allow_html=True)
