# scraper_google.py
# Scraper de librerías usando DuckDuckGo - INTEGRADO

import requests
from bs4 import BeautifulSoup
import unicodedata
from urllib.parse import unquote, parse_qs, urlparse
from typing import Optional

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; LibreriaScraper/5.0)"
}

# ============================================================
# NORMALIZAR TEXTO
# ============================================================
def normalizar(text: str):
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.strip()

# ============================================================
# UBICACIONES GEOAPIFY
# ============================================================
GEOAPIFY_KEY = "9dcad49b26d34081bb8e1389b025fab9"

def buscar_ubicaciones(query: str):
    q = normalizar(query)
    url = "https://api.geoapify.com/v1/geocode/search"
    params = {"text": q, "lang": "es", "apiKey": GEOAPIFY_KEY}

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()

        data = r.json()
        results = []

        for f in data.get("features", []):
            p = f["properties"]
            results.append({
                "lat": p.get("lat"),
                "lon": p.get("lon"),
                "direccion": p.get("formatted")
            })

        return results[:10]

    except Exception:
        return []

# ============================================================
# BUSQUEDA WEB GRATIS (DuckDuckGo HTML)
# ============================================================
def buscar_en_google(query: str):
    """
    Búsqueda usando DuckDuckGo - 100% GRATIS y sin bloqueos
    """
    # DuckDuckGo HTML (no bloquea como Google)
    search_url = "https://html.duckduckgo.com/html/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://duckduckgo.com/"
    }
    
    # DuckDuckGo usa POST
    data = {
        "q": query,
        "b": "",
        "kl": "ec-es"  # Ecuador
    }
    
    try:
        r = requests.post(search_url, data=data, headers=headers, timeout=15)
        r.raise_for_status()
        
        soup = BeautifulSoup(r.text, "html.parser")
        links = []
        
        # DuckDuckGo usa la clase 'result__url' para mostrar URLs
        for result in soup.find_all("a", class_="result__url"):
            href = result.get("href")
            if href:
                # DuckDuckGo puede usar redirección, limpiar
                if href.startswith("//duckduckgo.com/l/?"):
                    # Extraer URL real del parámetro uddg
                    try:
                        parsed = urlparse(href)
                        params = parse_qs(parsed.query)
                        if "uddg" in params:
                            href = unquote(params["uddg"][0])
                    except Exception:
                        continue
                
                if href.startswith("http"):
                    links.append(href)
        
        # También buscar en resultados normales
        for result in soup.find_all("a", class_="result__a"):
            href = result.get("href")
            if href and href.startswith("http") and href not in links:
                links.append(href)
        
        # Eliminar duplicados
        unique_links = list(dict.fromkeys(links))
        
        return unique_links[:50]
    
    except Exception:
        return []

# ============================================================
# CLASIFICACIÓN DE LINKS – SOLO LIBRERÍAS
# ============================================================
SOCIAL = ["facebook.com", "instagram.com", "x.com", "twitter.com", "tiktok.com", "youtube.com"]

# Palabras que indican papelería o no-libros
EXCLUIR = [
    "papeler", "utiles", "escolar", "escolares",
    "juguet", "oficina", "kinder", "ferreter", 
    "bazar", "souvenir", "supermercado", "farmacia"
]

# Palabras que indican venta de libros
INCLUIR = [
    "libr", "book", "books", "bookstore",
    "libro", "editorial", "lectura", "poesia",
    "literatura", "literaria", "noveleria"
]

# Dominios confiables de librerías
DOMINIOS_LIBROS = [
    "librimundi", "mrbooks", "englishbook", "confederacionlibre",
    "casadelacultura", "puce.edu", "usfq.edu"
]

def clasificar_links(links):
    webs = []
    redes = []

    for link in links:
        lk = link.lower()
        
        # clasificar redes
        if any(s in lk for s in SOCIAL):
            redes.append(link)
            continue

        # excluir tiendas no relacionadas con libros (excepción fuerte)
        if any(x in lk for x in EXCLUIR):
            continue

        # INCLUIR si:
        # 1. Tiene palabra clave de libros en la URL
        # 2. O es un dominio conocido de librería
        # 3. O es un resultado orgánico (permitir más flexibilidad)
        webs.append(link)

    return webs, redes

# ============================================================
# SCRAPER DE CATALOGO – SOLO LIBROS
# ============================================================
def extraer_catalogo(url: str):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        items = []

        # selectores comunes en tiendas de libros
        selectores = [
            ".book-item",
            ".producto-libro",
            ".product-title",
            ".woocommerce-loop-product__title",
            ".book-title",
            ".titulo-libro",
            ".entry-title",
            "li.product",
            "article"
        ]

        for sel in selectores:
            for el in soup.select(sel):
                t = el.get_text(strip=True)
                if 3 < len(t) < 120:
                    items.append(t)

        # Buscar títulos relacionados con literatura
        PALABRAS_LIBROS = [
            "libro", "novela", "cuento", "autor", "editorial",
            "tapa dura", "tapa blanda", "historia", "poesía",
            "literatura", "ensayo", "biografia"
        ]

        for tag in soup.find_all(["h1", "h2", "h3", "h4", "a"]):
            t = tag.get_text(strip=True)
            if any(w in t.lower() for w in PALABRAS_LIBROS) and 3 < len(t) < 120:
                items.append(t)

        # limpieza
        clean = []
        for i in items:
            low = i.lower()
            # descartar basura o papelería infiltrada
            if any(x in low for x in EXCLUIR):
                continue
            if low.startswith("leer más"):
                continue
            clean.append(i)

        return list(dict.fromkeys(clean))[:40]

    except Exception:
        return []

# ============================================================
# FUNCIÓN PRINCIPAL DE BÚSQUEDA
# ============================================================
def buscar(name: str, city: Optional[str] = None):
    """Busca catálogo de libros de una librería (función principal)."""
    query = f"{name} {city}" if city else name

    ubicaciones = buscar_ubicaciones(query)
    links = buscar_en_google(query)
    paginas_web, redes = clasificar_links(links)

    # Extraer catálogo (solo si parece una librería real)
    catalogo = []
    for w in paginas_web:
        c = extraer_catalogo(w)
        if len(c) >= 3:
            catalogo = c
            break

    return {
        "query": query,
        "ubicaciones": ubicaciones,
        "links_encontrados": links,
        "paginas_web_detectadas": paginas_web,
        "redes_sociales": redes,
        "catalogo_detectado": catalogo
    }

# ============================================================
# ENDPOINT FASTAPI (OPCIONAL - para uso como servidor)
# ============================================================
if __name__ != "__main__":
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware

        app = FastAPI(title="Scraper Librerías Mejorado SOLO LIBROS")

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @app.get("/search")
        def search_endpoint(name: str, city: Optional[str] = None):
            return buscar(name, city)

    except ImportError:
        pass
