# 🚀 GUÍA DE EJECUCIÓN - SCRAPERS INTEGRADOS

Este proyecto ahora integra **dos scrapers especializados** para extraer catálogos de libros desde librerías:

## 📋 Requisitos

```bash
pip install requests beautifulsoup4 selenium webdriver-manager unidecode fastapi uvicorn
```

---

## 🔧 Configuración de Scrapers

### Opción 1: Ejecutar en Paralelo (Recomendado)

Abre **3 terminales** diferentes:

#### Terminal 1: Scraper de Google (DuckDuckGo)
```bash
python -m uvicorn scraper_google:app --port 8001 --reload
```
✅ Accesible en: `http://localhost:8001/docs`

#### Terminal 2: Scraper de Facebook (Selenium + Groq)
```bash
python scraper_facebook.py
```
⚠️ Requiere:
- `cookies.json` en la raíz del proyecto (para mantener sesión en Facebook)
- API Key de Groq configurada en el script

#### Terminal 3: Aplicación Principal (Streamlit)
```bash
streamlit run main.py
```
✅ Accesible en: `http://localhost:8501`

---

## 📱 Scraper de Google (DuckDuckGo)

**Ubicación:** `scraper_google.py`

**Características:**
- ✅ Búsqueda con DuckDuckGo (100% gratis, sin bloqueos)
- ✅ Clasificación automática de links
- ✅ Extracción de catálogos de librerías
- ✅ Identificación de redes sociales

**Endpoint:**
```bash
GET /search?name=LibreríaName&city=Ciudad
```

**Respuesta:**
```json
{
  "query": "LibreríaName Ciudad",
  "ubicaciones": [...],
  "links_encontrados": [...],
  "paginas_web_detectadas": [...],
  "redes_sociales": ["https://facebook.com/..."],
  "catalogo_detectado": ["Libro 1", "Libro 2", ...]
}
```

---

## 🔵 Scraper de Facebook (con IA)

**Ubicación:** `scraper_facebook.py`

**Características:**
- ✅ Extrae posts de páginas de Facebook
- ✅ Detecta títulos de libros con IA (Groq)
- ✅ Normalizador de títulos
- ✅ Manejo automático de sesión con cookies

**Preparación:**
1. Obtén tu API Key de Groq: https://console.groq.com/
2. Reemplaza `GROQ_API_KEY` en el script
3. Genera `cookies.json` (ver sección de cookies más abajo)

**Uso:**
```bash
python scraper_facebook.py
```

---

## 🍪 Configurar Cookies de Facebook

Para que el scraper de Facebook funcione sin bloques:

### Método Manual:
1. Abre Firefox/Chrome en modo normal
2. Ve a `https://facebook.com`
3. Inicia sesión
4. Abre DevTools (F12) → Application → Cookies
5. Copia todas las cookies en formato JSON a `cookies.json`:

```json
[
  {
    "name": "cookie_name",
    "value": "cookie_value",
    "domain": ".facebook.com",
    "path": "/",
    "secure": true,
    "httpOnly": true,
    "sameSite": "Lax"
  },
  ...
]
```

---

## 🧠 Cómo Funciona la Integración

```
┌─────────────────────────────────────────────────────────────┐
│         STREAMLIT (main.py)                                 │
│  - Carga CSV del SRI                                        │
│  - Detecta librerías por provincia                          │
│  - Solicita catálogos                                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ├─────────────────────────────────────┐
                      │                                     │
        ┌─────────────▼─────────────┐   ┌──────────────────▼──────────┐
        │  Scraper Google           │   │  Scraper Facebook           │
        │  (DuckDuckGo + Websites)  │   │  (Selenium + IA/Groq)       │
        │                           │   │                             │
        │  - Busca librerías        │   │  - Extrae posts             │
        │  - Clasifica links        │   │  - Detecta títulos con IA   │
        │  - Extrae catálogos       │   │  - Normaliza títulos        │
        └──────────┬────────────────┘   └──────────┬───────────────────┘
                   │                              │
                   │      ┌──────────────────────┘
                   │      │
                   └──────▼──────────────────────┐
                          │                      │
        ┌─────────────────▼─────────────────────┘
        │
        ▼
        Coordinador (scraper_coordinator.py)
        - Combina resultados de ambos scrapers
        - Crea ranking de libros
        - Retorna libro más popular

        ▼
        main.py
        - Muestra tabla de ranking
        - Envía libro más popular a Groq
        - Genera análisis de mercado y piratería
```

---

## ⚙️ Variables de Entorno Recomendadas

```bash
# Geoapify (geocodificación)
export GEOAPIFY_API_KEY="your_key_here"

# Groq (análisis de IA)
export GROQ_API_KEY="your_key_here"
```

---

## 🚨 Troubleshooting

### "Connection refused" en los scrapers
```
✅ Solución: Asegúrate de ejecutar las 3 terminales abiertas
```

### Facebook scraper bloqueado
```
✅ Soluciones:
1. Actualiza las cookies (regenera cookies.json)
2. Usa una VPN
3. Espera 24 horas antes de intentar de nuevo
```

### "Groq API error"
```
✅ Solución: Verifica tu API Key en https://console.groq.com/keys
```

### Resultados vacíos en web scraping
```
✅ Solución: Los sitios web pueden bloquear scrapers
          Usa Facebook scraper que es más confiable
```

---

## 📊 Ejemplos de Resultado Final

```
Provincia: Los Ríos
Librerías detectadas: 5

📚 RANKING DE LIBROS:
1. Hábitos Atómicos - 5 repeticiones
2. Cien Años de Soledad - 4 repeticiones
3. 1984 - 3 repeticiones
...

📘 Libro más vendido: Hábitos Atómicos

📖 ANÁLISIS IA:
"Este libro es popular porque... [análisis detallado]"
```

---

## 💡 Tips

- **Para mejor resultado:** Usa ambos scrapers (Google + Facebook)
- **Más rápido:** Solo Google (más veloz)
- **Más confiable:** Solo Facebook (menos bloqueos)
- **Óptimo:** Ambos en paralelo

---

**Última actualización:** Diciembre 2025
