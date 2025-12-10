# scraper_coordinator.py
# Coordina el uso de ambos scrapers: Google/DuckDuckGo y Facebook

import requests
from typing import List, Tuple
from collections import Counter
import time

# URLs de los servicios scraper
SCRAPER_GOOGLE_URL = "http://localhost:8001/search"  # Scraper de Google
SCRAPER_FACEBOOK_URL = "http://localhost:8002/extract"  # Scraper de Facebook

TIMEOUT = 30


def obtener_catalogo_google(nombre_libreria: str, ciudad: str = "") -> Tuple[List[str], List[str]]:
    """
    Obtiene catálogo desde el scraper de Google usando DuckDuckGo.
    
    Returns:
        Tuple de (libros, redes_sociales)
    """
    if not nombre_libreria:
        return [], []
    
    try:
        params = {
            "name": nombre_libreria,
            "city": ciudad if ciudad else None
        }
        
        params = {k: v for k, v in params.items() if v}
        
        response = requests.get(
            SCRAPER_GOOGLE_URL,
            params=params,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        
        data = response.json()
        
        libros = data.get("catalogo_detectado", [])
        redes_sociales = data.get("redes_sociales", [])
        
        return libros, redes_sociales
    
    except requests.exceptions.ConnectionError:
        return [], []
    except Exception:
        return [], []


def obtener_catalogo_facebook(url_facebook: str) -> List[str]:
    """
    Obtiene catálogo desde el scraper de Facebook.
    
    Args:
        url_facebook: URL del perfil/página de Facebook
    
    Returns:
        Lista de títulos de libros
    """
    if not url_facebook:
        return []
    
    try:
        payload = {"url": url_facebook}
        
        response = requests.post(
            SCRAPER_FACEBOOK_URL,
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        
        data = response.json()
        libros = data.get("titulos", [])
        
        if libros:
            print(f"✅ Facebook scraper: {len(libros)} libros encontrados")
        
        return libros
    
    except requests.exceptions.ConnectionError:
        print(f"⚠️ No se puede conectar al scraper de Facebook en {SCRAPER_FACEBOOK_URL}")
        return []
    except Exception as e:
        print(f"⚠️ Error con scraper de Facebook: {e}")
        return []


def obtener_ranking_libros_completo(
    df_librerias,
    max_librerias: int = 5,
    usar_facebook: bool = False
) -> tuple:
    """
    Obtiene ranking completo usando Google scraper y opcionalmente Facebook.
    
    Returns:
        Tuple de (ranking, libro_mas_popular)
    """
    nombres = (
        df_librerias["NOMBRE_FANTASIA_COMERCIAL"]
        .dropna().astype(str).str.strip().unique().tolist()
    )[:max_librerias]
    
    titulos = []
    redes_encontradas = []
    
    print(f"\n🌐 Intentando scrapers especializados para {len(nombres)} librerías...")
    
    # Paso 1: Buscar con Google scraper
    for i, nombre in enumerate(nombres, 1):
        if not nombre or nombre.strip() == "":
            continue
            
        print(f"  [{i}/{len(nombres)}] {nombre}...", end=" ")
        
        try:
            libros, redes = obtener_catalogo_google(nombre)
            if libros:
                titulos.extend(libros)
                redes_encontradas.extend(redes)
                print(f"✅ ({len(libros)} libros)")
            else:
                print("⚠️")
        except Exception as e:
            print(f"❌ ({str(e)[:20]})")
        
        time.sleep(0.5)
    
    # Paso 2: Si encontramos Facebook, usar el scraper de Facebook
    if usar_facebook and redes_encontradas:
        print("\n🔵 Procesando páginas de Facebook...")
        
        facebook_urls = [r for r in redes_encontradas if "facebook.com" in r.lower()]
        
        for url in facebook_urls[:2]:
            try:
                libros_fb = obtener_catalogo_facebook(url)
                if libros_fb:
                    titulos.extend(libros_fb)
                    print(f"  ✅ {url[:50]}... ({len(libros_fb)} libros)")
            except Exception as e:
                print(f"  ❌ {url[:50]}... ({str(e)[:20]})")
            
            time.sleep(1)
    
    # Paso 3: Crear ranking
    if not titulos:
        return [], None
    
    counter = Counter(titulos)
    ranking = counter.most_common(15)
    best_title = ranking[0][0] if ranking else None
    
    print(f"\n✅ Scrapers: {len(titulos)} libros, {len(counter)} únicos")
    if best_title:
        print(f"📘 {best_title} ({ranking[0][1]}x)")
    
    return ranking, best_title
