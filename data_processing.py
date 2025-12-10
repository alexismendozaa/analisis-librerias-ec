

import csv
import unicodedata
import requests
import pandas as pd
import time
import re
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any, List
from collections import Counter


# ============================================================
# UTILIDADES BÁSICAS
# ============================================================

def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return " ".join(text.lower().strip().split())


# ============================================================
# LECTURA ROBUSTA DEL CSV
# ============================================================

def detectar_separador(uploaded_file) -> str:
    """
    Detecta separador probable usando csv.Sniffer.
    Fallback a ';' que es muy típico en SRI.
    """
    raw = uploaded_file
    raw.seek(0)
    sample = raw.read(4096).decode(errors="ignore")
    raw.seek(0)

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";", "|", "\t"])
        return dialect.delimiter
    except Exception:
        return ";"


def load_and_clean_data(uploaded_file) -> pd.DataFrame:
    """
    Carga el CSV, detecta separador y limpia columnas/espacios.
    """
    sep = detectar_separador(uploaded_file)

    uploaded_file.seek(0)
    try:
        df = pd.read_csv(
            uploaded_file,
            sep=sep,
            encoding="latin1",
            dtype=str,
            engine="python",
            on_bad_lines="skip",
        )
    except Exception:
        uploaded_file.seek(0)
        df = pd.read_csv(
            uploaded_file,
            sep=sep,
            encoding="utf-8",
            dtype=str,
            engine="python",
            on_bad_lines="skip",
        )

    # Limpiar espacios de nombres de columnas y valores
    df.columns = [c.strip() for c in df.columns]
    for col in df.columns:
        df[col] = df[col].fillna("").astype(str).str.strip()

    return df


# ============================================================
# FILTRO POR PROVINCIA
# ============================================================

def filter_by_province(df: pd.DataFrame, provincia: str) -> pd.DataFrame:
    """
    Usa la columna real del SRI: DESCRIPCION_PROVINCIA_EST.
    """
    provincia = provincia.strip().upper()
    if "DESCRIPCION_PROVINCIA_EST" not in df.columns:
        return df.copy()

    mask = df["DESCRIPCION_PROVINCIA_EST"].astype(str).str.upper() == provincia
    return df.loc[mask].copy()


# ============================================================
# DETECCIÓN DE LIBRERÍAS (CIIU + nombre comercial)
# ============================================================

CIIU_CODIGOS_LIBRERIAS = {
    "464993": "Venta al por mayor de material de papelería, libros, revistas, periódicos",
    "G4761": "Venta al por menor de libros, periódicos y artículos de papelería",
    "G47610": "Venta al por menor de libros, periódicos y artículos de papelería en comercios especializados",
    "G476101": "Venta al por menor de libros de todo tipo en establecimientos especializados",
    "G477401": "Venta al por menor de libros de segunda mano en establecimientos especializados",
}

KEYWORDS_LIBRERIAS = [
    "libreria",
    "librería",
    "libros",
    "book",
    "books",
    "editorial",
    "lectura",
    "biblioteca",
]


def detect_libraries(df_provincia: pd.DataFrame) -> pd.DataFrame:
    """
    Detecta librerías combinando:
    - Códigos CIIU relevantes
    - Palabras clave en NOMBRE_FANTASIA_COMERCIAL
    - Estado ACTIVO si la columna existe
    """
    df = df_provincia.copy()

    # 1) Intentar por CIIU
    col_ciiu = None
    for c in df.columns:
        if "ciiu" in c.lower():
            col_ciiu = c
            break

    mask_ciiu = pd.Series([False] * len(df), index=df.index)

    if col_ciiu:
        df[col_ciiu] = df[col_ciiu].astype(str).str.strip()
        mask_ciiu = df[col_ciiu].apply(
            lambda v: any(code in v for code in CIIU_CODIGOS_LIBRERIAS.keys())
        )

    # 2) Intentar por nombre comercial
    if "NOMBRE_FANTASIA_COMERCIAL" in df.columns:
        nombres = df["NOMBRE_FANTASIA_COMERCIAL"].fillna("").astype(str)
        mask_nombre = nombres.apply(
            lambda x: any(kw in normalize_text(x) for kw in KEYWORDS_LIBRERIAS)
        )
    else:
        mask_nombre = pd.Series([False] * len(df), index=df.index)

    # 3) Unir
    mask_total = mask_ciiu | mask_nombre
    df_lib = df[mask_total].copy()

    # 4) Filtrar activos
    if "ESTADO_CONTRIBUYENTE" in df_lib.columns:
        df_lib["ESTADO_CONTRIBUYENTE"] = (
            df_lib["ESTADO_CONTRIBUYENTE"].astype(str).str.upper().str.strip()
        )
        df_lib = df_lib[df_lib["ESTADO_CONTRIBUYENTE"] == "ACTIVO"].copy()

    # 5) Asegurar que NOMBRE_FANTASIA_COMERCIAL esté limpio
    if "NOMBRE_FANTASIA_COMERCIAL" in df_lib.columns:
        df_lib["NOMBRE_FANTASIA_COMERCIAL"] = (
            df_lib["NOMBRE_FANTASIA_COMERCIAL"].fillna("").astype(str).str.strip()
        )

    return df_lib


# ============================================================
# GEOAPIFY – GEOCODIFICACIÓN POR NOMBRE COMERCIAL
# ============================================================

GEOAPIFY_URL = "https://api.geoapify.com/v1/geocode/search"

def geocode_one(name: str, provincia: str, api_key: str) -> Optional[Dict[str, Any]]:
    """
    Geocodifica una librería usando el nombre comercial + provincia + Ecuador.
    """
    if not api_key or not name:
        return None

    q = f"{name}, {provincia}, Ecuador"

    params = {
        "text": q,
        "apiKey": api_key,
        "format": "json",
        "limit": 1,
    }

    try:
        r = requests.get(GEOAPIFY_URL, params=params, timeout=10)
        r.raise_for_status()
    except Exception:
        return None

    data = r.json().get("results", [])
    if not data:
        return None

    p = data[0]

    # Respetar país
    if p.get("country") and "ecuador" not in str(p["country"]).lower():
        return None

    # State opcional
    state = p.get("state") or ""
    return {
        "nombre_comercial": name,
        "lat": p.get("lat"),
        "lon": p.get("lon"),
        "provincia_geo": state,
        "raw": p,
    }


def geocode_libraries(
    df_librerias: pd.DataFrame,
    geoapify_key: str,
    max_registros: int = 50,
    provincia_filtro: Optional[str] = None,
) -> pd.DataFrame:

    if df_librerias.empty:
        return pd.DataFrame()

    df = df_librerias.copy().head(max_registros)

    rows = []

    for _, row in df.iterrows():
        nombre = str(row.get("NOMBRE_FANTASIA_COMERCIAL", "")).strip()
        prov = str(row.get("DESCRIPCION_PROVINCIA_EST", "")).strip()

        if not prov and provincia_filtro:
            prov = provincia_filtro

        info = geocode_one(nombre, prov, geoapify_key)
        if not info:
            continue

        # Si hay filtro de provincia, validar
        if provincia_filtro and info["provincia_geo"]:
            if provincia_filtro.lower() not in info["provincia_geo"].lower():
                continue

        rows.append(
            {
                "NOMBRE_FANTASIA_COMERCIAL": nombre,
                "provincia": prov,
                "provincia_geo": info.get("provincia_geo", ""),
                "canton": row.get("DESCRIPCION_CANTON_EST", ""),
                "parroquia": row.get("DESCRIPCION_PARROQUIA_EST", ""),
                "lat": info["lat"],
                "lon": info["lon"],
            }
        )

        # Pequeña espera para no saturar
        time.sleep(0.3)

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)


# ============================================================
# ESTADÍSTICAS
# ============================================================

def get_library_statistics(df_provincia, df_librerias, df_geo):
    """
    - Total registros de la provincia
    - Total librerías detectadas
    - Parroquia con más librerías (según datos del SRI, no del mapa)
    """
    total_registros = len(df_provincia)
    total_librerias = len(df_librerias)

    if "DESCRIPCION_PARROQUIA_EST" in df_librerias.columns:
        parroquias = (
            df_librerias["DESCRIPCION_PARROQUIA_EST"]
            .fillna("SIN PARROQUIA")
            .astype(str)
            .str.strip()
        )
        conteo = parroquias.value_counts()
        parroquia_top = conteo.idxmax() if not conteo.empty else None
        conteo_por_parroquia = conteo.to_dict()
    else:
        parroquia_top = None
        conteo_por_parroquia = {}

    return {
        "total_registros_provincia": total_registros,
        "total_librerias": total_librerias,
        "parroquia_top": parroquia_top,
        "conteo_por_parroquia": conteo_por_parroquia,
    }


# ============================================================
# SCRAPING GOOGLE + CATALOGO (SIN OTRAS API KEYS)
# ============================================================

SCRAPE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; LibreriaScraper/5.0)"
}


def google_search_first_result(query: str) -> Optional[str]:
    """
    Búsqueda directa en Google sin ScrapingDog.
    Devuelve el primer enlace orgánico que no sea de Google.
    """
    from urllib.parse import quote_plus

    q = quote_plus(query)
    url = f"https://www.google.com/search?q={q}&hl=es-419"

    try:
        r = requests.get(url, headers=SCRAPE_HEADERS, timeout=10)
        r.raise_for_status()
    except Exception:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    for a in soup.select("a"):
        href = a.get("href") or ""
        if not href.startswith("http"):
            continue
        if "google." in href:
            continue
        if "webcache.googleusercontent" in href or "policies.google.com" in href:
            continue
        return href

    return None


def extraer_catalogo_web(url: str) -> List[str]:
    """
    Extrae posibles títulos de libros de una página de librería.
    No es perfecto, pero se basa en selectores típicos de catálogos.
    """
    try:
        r = requests.get(url, headers=SCRAPE_HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
    except Exception:
        return []

    items = []

    selectores = [
        ".book-item",
        ".producto-libro",
        ".product-title",
        ".woocommerce-loop-product__title",
        ".book-title",
        ".titulo-libro",
        ".entry-title",
        "li.product",
        "article",
    ]

    for sel in selectores:
        for el in soup.select(sel):
            t = el.get_text(strip=True)
            if 3 < len(t) < 120:
                items.append(t)

    # Títulos que parecen ser libros por contexto
    PALABRAS_LIBROS = [
        "libro",
        "novela",
        "cuento",
        "autor",
        "editorial",
        "tapa dura",
        "tapa blanda",
        "literatura",
        "poesía",
        "ensayo",
        "biografia",
    ]

    for tag in soup.find_all(["h1", "h2", "h3", "h4", "a"]):
        t = tag.get_text(strip=True)
        if any(w in t.lower() for w in PALABRAS_LIBROS):
            if 3 < len(t) < 120:
                items.append(t)

    clean = []
    for i in items:
        low = i.lower()
        if "papeler" in low or "útiles" in low:
            continue
        if i not in clean:
            clean.append(i)

    return clean[:50]


def build_books_ranking_from_libraries(
    df_librerias: pd.DataFrame,
    max_librerias: int = 5,
):
    """
    Construye ranking de libros:
    1. Intenta extraer desde catálogos de librerías
    2. Si falla → usa libros más vendidos globales como fallback
    """

    # -------------- FASE 1: EXTRAER DESDE WEB REAL ----------------
    nombres = (
        df_librerias["NOMBRE_FANTASIA_COMERCIAL"]
        .dropna().astype(str).str.strip().unique().tolist()
    )[:max_librerias]

    titulos = []

    for nombre in nombres:
        url = google_search_first_result(f"{nombre} librería Ecuador libros")
        if not url:
            continue
        libros = extraer_catalogo_web(url)
        titulos.extend(libros)
        time.sleep(2)

    # Si encontramos libros reales → devolverlos
    if titulos:
        from collections import Counter
        ranking = Counter(titulos).most_common(15)
        return ranking, ranking[0][0]

    # -------------- FASE 2: FALLBACK — BESTSELLERS 2024 --------------
    fallback = [
        "Hábitos Atómicos",
        "El Sutil Arte de que Todo te Importe una Mierda",
        "Padre Rico Padre Pobre",
        "Cómo Ganar Amigos e Influir sobre las Personas",
        "1984",
        "El Principito",
        "Cien Años de Soledad",
        "Harry Potter y la Piedra Filosofal",
        "El Alquimista",
        "El Poder del Ahora",
    ]

    ranking = [(titulo, 1) for titulo in fallback]
    best = fallback[0]
    return ranking, best
