# mapping.py

import unicodedata
import folium


def _norm(text: str) -> str:
    """Normaliza cadenas para comparación exacta de provincia."""
    if text is None:
        return ""
    text = unicodedata.normalize("NFKD", str(text))
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.strip().lower()


def create_map_html(df_geo, provincia: str) -> str:
    """
    Crea un mapa Folium con las librerías geocodificadas y filtra por provincia.
    Usa provincia_geo (retornada por Geoapify) como fuente de verdad.
    """
    if df_geo is None or df_geo.empty:
        return "<h3>No hay datos geocodificados para mostrar.</h3>"

    df = df_geo.copy()

    # Filtrado estricto usando provincia_geo (retornada por Geoapify) como fuente de verdad
    prov_norm = _norm(provincia)
    if prov_norm:
        # Priorizar provincia_geo (retornada por Geoapify) para máxima precisión
        if "provincia_geo" in df.columns:
            df = df[df["provincia_geo"].apply(_norm) == prov_norm].copy()
        elif "DESCRIPCION_PROVINCIA_EST" in df.columns:
            df = df[df["DESCRIPCION_PROVINCIA_EST"].apply(_norm) == prov_norm].copy()

    if df.empty:
        return "<h3>No hay librerías geocodificadas para la provincia seleccionada.</h3>"

    # Centrar el mapa en el promedio de las coordenadas filtradas
    center_lat = df["lat"].astype(float).mean()
    center_lon = df["lon"].astype(float).mean()
    mapa = folium.Map(location=[center_lat, center_lon], zoom_start=9)

    for _, row in df.iterrows():
        lat = row.get("lat")
        lon = row.get("lon")
        if lat is None or lon is None:
            continue

        nombre = row.get("NOMBRE_FANTASIA_COMERCIAL", "Sin nombre")
        parroquia = row.get("parroquia", "")
        canton = row.get("canton", "")

        popup = f"<b>{nombre}</b><br>{parroquia} - {canton}"
        folium.Marker(
            location=[lat, lon],
            popup=popup,
            icon=folium.Icon(color="blue"),
        ).add_to(mapa)

    return mapa._repr_html_()
