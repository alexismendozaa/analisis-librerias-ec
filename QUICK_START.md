# 🚀 INICIO RÁPIDO

## Paso 1: Instalar dependencias
```bash
pip install -r requirements.txt
```

## Paso 2: Opción A - Solo Streamlit (Recomendado para empezar)

Una sola terminal:
```bash
export GEOAPIFY_API_KEY="your_key"
export GROQ_API_KEY="your_key"
streamlit run main.py
```

✅ Esto usará web scraping automático

---

## Paso 3: Opción B - Con Scrapers Especializados (Para mejor resultado)

Abre 2 terminales:

### Terminal 1 - App Principal
```bash
export GEOAPIFY_API_KEY="your_key"
export GROQ_API_KEY="your_key"
streamlit run main.py
```

### Terminal 2 - Scraper Google (FastAPI)
```bash
python -m uvicorn scraper_google:app --port 8001 --reload
```

✅ Con esto obtendrá catálogos desde DuckDuckGo

---

## Paso 4: Opción C - Con Scraper Facebook (Máxima precisión)

Abre 3 terminales + prepara cookies:

### Preparar cookies.json (una sola vez)
Ver `SCRAPERS_SETUP.md` sección "Configurar Cookies de Facebook"

### Terminal 1 - App Principal
```bash
export GEOAPIFY_API_KEY="your_key"
export GROQ_API_KEY="your_key"
streamlit run main.py
```

### Terminal 2 - Scraper Google
```bash
python -m uvicorn scraper_google:app --port 8001 --reload
```

### Terminal 3 - Scraper Facebook
```bash
python scraper_facebook.py
```

✅ Esto obtendrá catálogos desde Facebook con IA

---

## 🌐 Acceso

- **Streamlit:** http://localhost:8501
- **Scraper Google API:** http://localhost:8001/docs
- **Scraper Facebook:** Se ejecuta bajo demanda

---

## ⚙️ Variables de Entorno

```bash
# Geoapify (geocodificación)
export GEOAPIFY_API_KEY="9dcad49b26d34081bb8e1389b025fab9"

# Groq (análisis de IA)
export GROQ_API_KEY="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"
```

---

## 📊 Flujo de Datos

```
Streamlit (main.py)
    ↓
    ├→ Web Scraping (Google Search)
    ├→ Scraper Google (DuckDuckGo + FastAPI)
    └→ Scraper Facebook (Selenium + IA)
    ↓
Ranking de Libros
    ↓
Groq IA Analysis
    ↓
Resultados
```

---

## 🎯 Recomendaciones

- **Rápido:** Solo opción A (1 terminal)
- **Balanceado:** Opción B (2 terminales)
- **Máxima precisión:** Opción C (3 terminales + cookies)

---

Ver `SCRAPERS_SETUP.md` para más detalles técnicos.

