# groq_handler.py

from groq import Groq

# MODELO REALMENTE DISPONIBLE
GROQ_MODEL = "llama-3.3-70b-versatile"


def init_groq_client(api_key: str):
    return Groq(api_key=api_key)


def explain_best_seller(client, titulo_libro: str, provincia: str) -> str:
    prompt = f"""
    Analiza por qué el libro "{titulo_libro}" aparece como uno de los más repetidos
    entre las librerías de la provincia de {provincia}.

    Explica:
    - Qué factores de mercado influyen en su popularidad.
    - Qué tipo de lector lo compra.
    - Cómo se comporta el mercado editorial en provincias similares.
    - Riesgos de piratería asociados al título.

    Responde en un solo párrafo claro.
    """

    try:
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "Eres un analista experto en mercado editorial y piratería."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=400,
        )

        return resp.choices[0].message.content

    except Exception as e:
        return f"Error generando explicación con IA: {e}"


def summarize_analysis(client, provincia: str, stats: dict, libros_texto: str = "") -> str:
    ranking_block = (
        f"    Ranking de libros detectados (si aplica):\n    {libros_texto}\n\n"
        if libros_texto
        else ""
    )

    prompt = f"""
    Genera un informe breve del mercado editorial de la provincia {provincia}.

    Datos:
    - Total de registros: {stats['total_registros_provincia']}
    - Total de librerías detectadas: {stats['total_librerias']}
    - Parroquia con más librerías: {stats['parroquia_top']}
{ranking_block}    Incluye:
    - Cómo afecta esta distribución al acceso a la lectura.
    - Riesgo de piratería en la provincia.
    - Sugerencias para mejorar el ecosistema editorial local.
    """

    try:
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "Eres un experto en análisis editorial y piratería."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=450,
        )

        return resp.choices[0].message.content

    except Exception as e:
        return f"Error generando resumen con IA: {e}"
