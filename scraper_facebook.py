# scraper_facebook.py
# Scraper de Facebook para detectar títulos de libros en posts

import json
import time
from datetime import datetime
from typing import Optional, List
from unidecode import unidecode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

try:
    from groq import Groq
    GROQ_DISPONIBLE = True
except ImportError:
    GROQ_DISPONIBLE = False


# ============================================================
# CONFIGURACIÓN SELENIUM
# ============================================================
def configurar_selenium():
    """Configura y retorna una instancia de Chrome WebDriver."""
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        print(f"Error al configurar Selenium: {e}")
        return None


# ============================================================
# CARGAR COOKIES DE FACEBOOK
# ============================================================
def cargar_cookies(driver, cookies_file: str = "cookies.json"):
    """Carga cookies guardadas para mantener sesión."""
    try:
        with open(cookies_file, "r") as f:
            cookies = json.load(f)
        
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception:
                pass
        
        return True
    except FileNotFoundError:
        print(f"⚠️ {cookies_file} no encontrado. Usa login manual.")
        return False


# ============================================================
# EXTRAER POSTS DE FACEBOOK
# ============================================================
def extraer_posts(url: str, cantidad: int = 10, tiempo_scroll: int = 30) -> List[str]:
    """Extrae posts de texto de una página de Facebook."""
    posts = []
    driver = configurar_selenium()
    
    if not driver:
        return posts
    
    try:
        driver.get(url)
        time.sleep(3)
        
        # Intentar cargar cookies
        cargar_cookies(driver, "cookies.json")
        driver.get(url)
        time.sleep(3)
        
        # Scroll para cargar más posts
        scroll_start = time.time()
        while time.time() - scroll_start < tiempo_scroll:
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(2)
        
        # Extraer posts
        try:
            post_elements = driver.find_elements(By.XPATH, "//div[@data-feed-item-type='feeditem']")
        except Exception:
            post_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'userContentWrapper')]")
        
        for elemento in post_elements[:cantidad]:
            try:
                texto = elemento.text
                if texto and len(texto) > 20:
                    posts.append(texto)
            except Exception:
                continue
        
        return posts
    
    except Exception as e:
        print(f"Error extrayendo posts: {e}")
        return posts
    
    finally:
        driver.quit()


# ============================================================
# DETECTAR TÍTULOS CON GROQ AI
# ============================================================
def detectar_titulos_batch(posts: List[str], api_key: Optional[str] = None) -> List[str]:
    """Usa Groq AI para detectar títulos de libros en posts."""
    if not GROQ_DISPONIBLE or not api_key:
        return []
    
    try:
        client = Groq(api_key=api_key)
        titulos = []
        
        for post in posts[:5]:
            try:
                prompt = f"""
Analiza este post de Facebook y extrae SOLO los títulos de libros mencionados.
Responde con una lista separada por comas, solo los títulos, sin explicaciones.
Si no hay libros, responde "NINGUNO".

Post: "{post}"
"""
                
                response = client.messages.create(
                    model="llama-3.3-70b-versatile",
                    max_tokens=200,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                resultado = response.content[0].text.strip()
                if resultado != "NINGUNO":
                    for titulo in resultado.split(","):
                        titulo = titulo.strip()
                        if titulo:
                            titulos.append(titulo)
            
            except Exception:
                continue
        
        return titulos
    
    except Exception as e:
        print(f"Error con Groq: {e}")
        return []


# ============================================================
# LIMPIAR DUPLICADOS Y NORMALIZAR
# ============================================================
def limpiar_duplicados(titulos: List[str]) -> List[str]:
    """Elimina duplicados y mantiene la versión más larga."""
    diccionario = {}
    
    for titulo in titulos:
        normalizado = unidecode(titulo.lower())
        
        if normalizado not in diccionario:
            diccionario[normalizado] = titulo
        else:
            if len(titulo) > len(diccionario[normalizado]):
                diccionario[normalizado] = titulo
    
    return list(diccionario.values())


def normalizar_titulo(titulo: str) -> str:
    """Normaliza un título: capitalize, limpia espacios."""
    return " ".join(titulo.strip().title().split())


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================
def extraer_libros_facebook(
    url: str,
    cantidad_posts: int = 10,
    api_key_groq: Optional[str] = None
) -> dict:
    """
    Función principal: extrae libros de una página de Facebook.
    Retorna un diccionario con el resultado.
    """
    print(f"\n📘 Extrayendo posts de: {url}")
    
    # Extraer posts
    posts = extraer_posts(url, cantidad_posts)
    print(f"✓ {len(posts)} posts extraídos")
    
    # Detectar títulos con Groq
    if api_key_groq and GROQ_DISPONIBLE:
        print("🤖 Detectando títulos con Groq AI...")
        titulos = detectar_titulos_batch(posts, api_key_groq)
    else:
        titulos = []
    
    # Limpiar duplicados y normalizar
    titulos_limpios = limpiar_duplicados(titulos)
    titulos_limpios = [normalizar_titulo(t) for t in titulos_limpios]
    
    resultado = {
        "total": len(titulos_limpios),
        "titulos": titulos_limpios,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    print(f"✓ {resultado['total']} títulos detectados")
    
    return resultado


# ============================================================
# ENDPOINT FASTAPI (OPCIONAL)
# ============================================================
if __name__ != "__main__":
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware

        app = FastAPI(title="Scraper Facebook - Detección de Libros")

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @app.get("/extract")
        def extract_endpoint(url: str, groq_key: Optional[str] = None):
            return extraer_libros_facebook(url, api_key_groq=groq_key)

    except ImportError:
        pass
