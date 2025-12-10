# 📚 Sistema de Análisis de Librerías por Provincia (Dataset SRI)

Un sistema inteligente y escalable que analiza datos del SRI para identificar, mapear y estudiar librerías por provincia, incluyendo análisis de catálogos de libros con IA mediante Groq.

---

## 🎯 Características Principales

✨ **Análisis Completo de Librerías**
- Detección automática de librerías usando CIIU y análisis de nombres
- Filtrado por provincia, cantón y parroquia
- Cálculo de métricas estadísticas detalladas

🗺️ **Visualización Geoespacial**
- Geocodificación con Geoapify
- Mapas interactivos con Folium
- Localización precisa de librerías

📖 **Scraping de Catálogos**
- Extracción automática de catálogos de libros desde sitios web
- Análisis de frecuencia de títulos
- Detección de patrones de inventario

🤖 **Análisis con IA (Groq)**
- Explicaciones inteligentes sobre best-sellers
- Análisis de factores de mercado
- Evaluación de riesgos de piratería
- Resúmenes automáticos del análisis

---

## 📋 Requisitos Previos

### Sistema Operativo
- macOS, Linux o Windows
- Python 3.8 o superior

### Credenciales Necesarias
1. **API Key de Geoapify** - Para geocodificación
   - Obtén una en: [geoapify.com](https://www.geoapify.com/)
   - Créditos gratuitos disponibles

2. **API Key de Groq** - Para análisis con IA
   - Obtén una en: [console.groq.com](https://console.groq.com/)
   - Modelo usado: `llama-3.3-70b-versatile`

3. **Dataset SRI**
   - Archivo CSV con columnas requeridas:
     - `NOMBRE_FANTASIA_COMERCIAL`
     - `DESCRIPCION_PROVINCIA_EST`
     - `DESCRIPCION_CANTON_EST`
     - `DESCRIPCION_PARROQUIA_EST`
     - Otras columnas de ubicación (detectadas automáticamente)

---

## 🚀 Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tuusuario/completo.git
cd completo
```

### 2. Crear Entorno Virtual
```bash
python3 -m venv venv
source venv/bin/activate  # En macOS/Linux
# o para Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno (Opcional)

Las API Keys se pueden configurar de dos formas:

#### Opción A: Variables de Entorno (Recomendado para desarrollo)

**En macOS/Linux:**
```bash
export GEOAPIFY_API_KEY="tu_clave_aqui"
export GROQ_API_KEY="tu_clave_aqui"
streamlit run main.py
```

**En Windows (PowerShell):**
```powershell
$env:GEOAPIFY_API_KEY="tu_clave_aqui"
$env:GROQ_API_KEY="tu_clave_aqui"
streamlit run main.py
```

**En Windows (CMD):**
```cmd
set GEOAPIFY_API_KEY=tu_clave_aqui
set GROQ_API_KEY=tu_clave_aqui
streamlit run main.py
```

#### Opción B: Interfaz Frontend (Más seguro)
Si no configuras variables de entorno, la aplicación te pedirá las claves directamente en la interfaz cuando la ejecutes.

---

## 💻 Ejecución

### Iniciar la Aplicación Streamlit

En el terminal, desde la carpeta del proyecto:

```bash
streamlit run main.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`

**Nota:** Asegúrate de que tu entorno virtual (`venv`) esté activado antes de ejecutar el comando.

---

## 📖 Guía de Uso

### Paso 1: Cargar Dataset
1. Haz clic en **"Subir archivo CSV"**
2. Selecciona tu archivo CSV del SRI
3. El sistema detectará automáticamente el separador (`,`, `;`, `|`, etc.)

### Paso 2: Ingresar Credenciales
- **API Key de Geoapify**: Ingresa tu clave para geocodificación
- **API Key de Groq**: Ingresa tu clave para análisis de IA

### Paso 3: Seleccionar Provincia
1. Elige la provincia a analizar del dropdown
2. El sistema mostrará:
   - Cantidad de librerías detectadas
   - Cantones y parroquias con presencia

### Paso 4: Analizar Datos
La aplicación ejecutará automáticamente:
1. **Detección de librerías** - Identifica negocios del rubro
2. **Geocodificación** - Obtiene coordenadas precisas
3. **Estadísticas** - Calcula métricas de distribución
4. **Mapa interactivo** - Visualiza ubicaciones en tiempo real

### Paso 5: Análisis de Catálogos (Opcional)
- Ingresa URLs de sitios web de librerías
- El sistema extraerá automáticamente títulos de libros
- Identifica los libros más populares

### Paso 6: Análisis con IA
- El sistema generará insights automáticos:
  - Por qué ciertos libros son best-sellers
  - Factores del mercado local
  - Análisis de riesgos de piratería
  - Resumen integral del análisis

---

## 📁 Estructura del Proyecto

```
completo/
├── main.py                  # Aplicación principal Streamlit
├── data_processing.py       # Funciones de procesamiento de datos
├── groq_handler.py          # Integración con API de Groq
├── mapping.py               # Generación de mapas interactivos
├── requirements.txt         # Dependencias del proyecto
├── .gitignore              # Archivos ignorados en git
└── README.md               # Este archivo
```

### Descripción de Módulos

#### `main.py`
- Interfaz principal de Streamlit
- Manejo de sesiones y estado de la aplicación
- Orquestación de todo el flujo de análisis
- Gestión de inputs del usuario

#### `data_processing.py`
- `load_and_clean_data()` - Carga y limpia CSV
- `filter_by_province()` - Filtra por provincia
- `detect_libraries()` - Detecta librerías automáticamente
- `geocode_libraries()` - Geocodifica ubicaciones
- `get_library_statistics()` - Calcula estadísticas
- `build_books_ranking_from_libraries()` - Ranking de libros

#### `groq_handler.py`
- `init_groq_client()` - Inicializa cliente Groq
- `explain_best_seller()` - Análisis de libros populares
- `summarize_analysis()` - Resumen integral del análisis

#### `mapping.py`
- `create_map_html()` - Genera mapas interactivos con Folium

---

## 🔧 Configuración Avanzada

### Variables de Sesión
El sistema mantiene estado usando `streamlit.session_state`:
- `geoapify` - API Key de Geoapify
- `groq` - API Key de Groq
- `df` - DataFrame cargado
- `filtered_df` - DataFrame filtrado por provincia
- `libraries_df` - Librerías detectadas
- `geocoded_df` - Librerías geocodificadas
- `map_html` - HTML del mapa generado

### Parámetros Personalizables

En `data_processing.py`:
```python
# Detectar librerías por estos CIIU
LIBRARY_CIIUS = [...]

# Palabras clave para identificar librerías
LIBRARY_KEYWORDS = [...]

# Timeout para requests
REQUEST_TIMEOUT = 10

# Delay entre requests (para respetar servidores)
REQUEST_DELAY = 1
```

---

## 📊 Salidas y Resultados

### Tablas de Datos
- **Librerías detectadas** - Nombre, ubicación, CIIU
- **Estadísticas por cantón/parroquia** - Distribución geográfica
- **Ranking de libros** - Títulos más repetidos

### Visualizaciones
- **Mapa interactivo** - Ubicación de todas las librerías
- **Gráficos estadísticos** - Distribución por zona

### Análisis de IA
- **Explicación de best-sellers** - Por qué ciertos libros lideran
- **Resumen de mercado** - Tendencias y patrones
- **Evaluación de piratería** - Riesgos por título

---

## 🐛 Troubleshooting

### Error: "Invalid API Key"
- Verifica que tu clave sea correcta en [console.groq.com](https://console.groq.com/) o [geoapify.com](https://www.geoapify.com/)
- Revisa que no tengas espacios en blanco

### Error: "Could not geocode address"
- Puede ser una limitación de Geoapify
- Intenta reducir la cantidad de librerías
- Verifica tu saldo de créditos en Geoapify

### Aplicación lenta
- Los requests web y geocodificación toman tiempo
- Usa datasets más pequeños para pruebas
- Considera usar caché de Streamlit (se configura automáticamente)

### CSV no se carga
- Verifica que esté en formato válido
- Asegúrate de que tenga las columnas requeridas
- Intenta otro delimitador manualmente

---

## 🚢 Despliegue

### En Streamlit Cloud (Gratuito)
```bash
# 1. Pushea a GitHub
git push origin main

# 2. Ve a https://streamlit.io/cloud
# 3. Conecta tu repositorio
# 4. Crea un secreto con tus API Keys en los settings
```

### En Servidor Personal
```bash
# Instala supervisor o similar para mantener el proceso vivo
pip install gunicorn
streamlit run main.py --server.port 8501 &
```

---

## 📝 Dependencias

| Librería | Versión | Uso |
|----------|---------|-----|
| streamlit | latest | Framework web |
| pandas | latest | Procesamiento de datos |
| requests | latest | HTTP requests |
| beautifulsoup4 | latest | Web scraping |
| folium | latest | Mapas interactivos |
| branca | latest | Soporte de mapas |
| groq | latest | API de IA |

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/mejora`)
3. Commit tus cambios (`git commit -m 'Añade mejora'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Abre un Pull Request

---


## 📞 Contacto y Soporte

Si encuentras problemas:
- Abre un issue en GitHub
- Revisa la sección de Troubleshooting
- Consulta la documentación de las APIs externas

---

## 🎓 Casos de Uso

✅ Análisis de mercado editorial por provincia
✅ Estudio de distribución de librerías
✅ Detección de tendencias de lectura
✅ Investigación de piratería
✅ Planificación de expansión comercial
✅ Análisis competitivo de librerías

---

**Última actualización:** Diciembre 2025

¡Disfruta analizando el mercado de librerías! 📚✨
