# main.py

import os
import streamlit as st
import pandas as pd

from data_processing import (
    load_and_clean_data,
    filter_by_province,
    detect_libraries,
    geocode_libraries,
    get_library_statistics,
    build_books_ranking_from_libraries,
)

from mapping import create_map_html
from groq_handler import (
    init_groq_client,
    explain_best_seller,
    summarize_analysis,
)

# ============================
# CONFIGURACIÓN DE LA PÁGINA
# ============================
st.set_page_config(page_title="Análisis de Librerías", layout="wide", page_icon="📚")

st.title("📚 Sistema de Análisis de Librerías por Provincia (Dataset SRI)")

st.markdown("""
Este sistema usa el dataset del SRI con al menos las siguientes columnas:

- **NOMBRE_FANTASIA_COMERCIAL**
- **DESCRIPCION_PROVINCIA_EST**
- **DESCRIPCION_CANTON_EST**
- **DESCRIPCION_PARROQUIA_EST**

Y realiza:
1. Filtrado por provincia (automático).
2. Detección de librerías (CIIU + nombre).
3. Cálculo de métricas básicas.
4. Geocodificación con Geoapify y mapa.
5. Scraping de catálogos de libros desde webs de librerías.
6. Análisis con Groq (libro más repetido + piratería).
""")

# ============================
# SESSION STATE KEYS
# ============================
if "geoapify" not in st.session_state:
    st.session_state["geoapify"] = ""

if "groq" not in st.session_state:
    st.session_state["groq"] = ""

# ============================
# API KEYS
# ============================
env_geo = os.getenv("GEOAPIFY_KEY", "")
env_groq = os.getenv("GROQ_API_KEY", "")

if env_geo and not st.session_state["geoapify"]:
    st.session_state["geoapify"] = env_geo

if env_groq and not st.session_state["groq"]:
    st.session_state["groq"] = env_groq

st.sidebar.header("🔐 API Keys")

geoapify_key = st.sidebar.text_input(
    "Geoapify API Key",
    value=st.session_state["geoapify"],
    key="geoapify",
    type="password",
)

groq_key = st.sidebar.text_input(
    "Groq API Key",
    value=st.session_state["groq"],
    key="groq",
    type="password",
)

# ============================
# 1. CARGA DEL CSV
# ============================
st.header("📂 1. Cargar archivo CSV del SRI")

uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])

if not uploaded_file:
    st.stop()

try:
    df = load_and_clean_data(uploaded_file)
except Exception as e:
    st.error(f"Error leyendo el CSV: {e}")
    st.stop()

with st.expander("Ver primeras filas del dataset"):
    st.dataframe(df.head())

required_cols = [
    "NOMBRE_FANTASIA_COMERCIAL",
    "DESCRIPCION_PROVINCIA_EST",
    "DESCRIPCION_CANTON_EST",
    "DESCRIPCION_PARROQUIA_EST",
]
for col in required_cols:
    if col not in df.columns:
        st.error(f"Falta la columna obligatoria: **{col}**")
        st.stop()

# ============================
# 2. DETECCIÓN AUTOMÁTICA DE PROVINCIA
# ============================
st.header("📍 2. Provincia detectada")

try:
    provincia_sel = df["DESCRIPCION_PROVINCIA_EST"].dropna().mode()[0]
except Exception:
    provincia_sel = df["DESCRIPCION_PROVINCIA_EST"].dropna().unique()[0]

st.success(f"📍 Provincia detectada automáticamente: **{provincia_sel}**")

df_provincia = filter_by_province(df, provincia_sel)

st.write(f"Total de registros en **{provincia_sel}**: {len(df_provincia)}")

# ============================
# 3. DETECCIÓN DE LIBRERÍAS
# ============================
st.header("📚 3. Detección de librerías")

df_librerias = detect_libraries(df_provincia)

st.success(f"Librerías detectadas: **{len(df_librerias)}**")

with st.expander("Ver librerías detectadas"):
    st.dataframe(
        df_librerias[
            [
                "NOMBRE_FANTASIA_COMERCIAL",
                "DESCRIPCION_CANTON_EST",
                "DESCRIPCION_PARROQUIA_EST",
            ]
        ].head(100)
    )

# ============================
# 4. MÉTRICAS Y GEOLOCALIZACIÓN
# ============================
st.header("📊 4. Métricas y mapa")

if not geoapify_key:
    st.warning("Falta GEOAPIFY_KEY (en variable de entorno o sidebar) para geocodificar.")
    df_geo = pd.DataFrame()
else:
    max_geo = st.slider("Máximo de librerías a geocodificar", 5, 200, 50, 5)

    with st.spinner("Geocodificando librerías con Geoapify..."):
        df_geo = geocode_libraries(
            df_librerias,
            geoapify_key=geoapify_key,
            max_registros=max_geo,
            provincia_filtro=provincia_sel,
        )

if df_geo is None:
    df_geo = pd.DataFrame()

stats = get_library_statistics(df_provincia, df_librerias, df_geo)

# Tres tarjetas antes del mapa
col1, col2, col3 = st.columns(3)
col1.metric("Total registros provincia", stats["total_registros_provincia"])
col2.metric("Total librerías detectadas", stats["total_librerias"])
col3.metric("Parroquia con más librerías", stats["parroquia_top"] or "N/D")

with st.expander("Conteo de librerías por parroquia"):
    st.write(pd.DataFrame.from_dict(stats["conteo_por_parroquia"], orient="index", columns=["Cantidad"]))

# Mapa
st.subheader(f"🗺️ Mapa de librerías en {provincia_sel}")

if df_geo.empty:
    st.warning("No se pudieron obtener coordenadas para las librerías.")
else:
    html_map = create_map_html(df_geo, provincia_sel)
    st.components.v1.html(html_map, height=600)

# ============================
# 5. LIBROS MÁS REPETIDOS (SCRAPING)
# ============================
st.header("📖 5. Libros más repetidos según catálogos web")

with st.spinner("Buscando páginas de librerías y extrayendo catálogos..."):
    ranking, best_title = build_books_ranking_from_libraries(df_librerias, max_librerias=5)

if not ranking:
    st.warning("No se pudieron extraer títulos de libros desde las webs de las librerías.")
else:
    st.success("Libros detectados en catálogos de librerías (más repetidos primero):")
    df_rank = pd.DataFrame(ranking, columns=["Título", "Repeticiones"])
    st.table(df_rank)
    st.write(f"📘 Posible libro más vendido: **{best_title}**")

# ============================
# 6. ANÁLISIS CON GROQ (LIBRO + PIRATERÍA)
# ============================
st.header("🤖 6. Análisis con Groq (mercado editorial y piratería)")

if not groq_key:
    st.error("Falta GROQ_API_KEY (en variable de entorno o sidebar).")
    st.stop()

client = init_groq_client(groq_key)

if best_title:
    with st.spinner("Generando análisis del libro más repetido..."):
        explicacion = explain_best_seller(client, best_title, provincia_sel)
    st.subheader("📘 Análisis del libro más repetido")
    st.write(explicacion)
else:
    st.info("No hay un libro dominante para análisis detallado.")

# Texto de libros para el resumen
libros_texto = "\n".join([f"- {t} (x{n})" for t, n in (ranking or [])])

with st.spinner("Generando resumen general y análisis de piratería..."):
    resumen = summarize_analysis(client, provincia_sel, stats, libros_texto)

st.subheader("📋 Resumen general del mercado y piratería")
st.write(resumen)
