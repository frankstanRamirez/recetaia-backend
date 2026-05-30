import os
import json
import httpx
from typing import List

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.1-8b-instant"

# TheMealDB - gratis, sin API key
MEALDB_SEARCH = "https://www.themealdb.com/api/json/v1/1/search.php?s="
MEALDB_RANDOM = "https://www.themealdb.com/api/json/v1/1/random.php"


async def _call_ai(messages: list, max_tokens: int = 1500) -> str:
    api_key = os.getenv("GROQ_API_KEY", "")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": messages
    }
    async with httpx.AsyncClient(timeout=40) as client:
        resp = await client.post(GROQ_URL, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


async def _buscar_imagen_plato(nombre_plato: str) -> str:
    """
    Busca imagen del plato en TheMealDB.
    Si no encuentra, retorna imagen genérica de comida de Unsplash.
    """
    try:
        # Traducir nombre simple al inglés para búsqueda (términos comunes)
        traducciones = {
            "arroz": "rice", "pollo": "chicken", "pasta": "pasta",
            "ensalada": "salad", "sopa": "soup", "tacos": "tacos",
            "tortilla": "tortilla", "frijoles": "beans", "carne": "beef",
            "pescado": "fish", "huevo": "eggs", "papa": "potato",
            "tomate": "tomato", "cebolla": "onion", "ajo": "garlic",
            "fideo": "noodles", "lentejas": "lentils", "atun": "tuna",
            "camarones": "shrimp", "cerdo": "pork", "queso": "cheese",
        }
        # Buscar primera palabra del nombre en el diccionario
        primera_palabra = nombre_plato.lower().split()[0]
        termino_busqueda = traducciones.get(primera_palabra, nombre_plato.split()[0])

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{MEALDB_SEARCH}{termino_busqueda}")
            data = resp.json()
            meals = data.get("meals")
            if meals and len(meals) > 0:
                return meals[0].get("strMealThumb", _imagen_generica(nombre_plato))
    except Exception:
        pass

    return _imagen_generica(nombre_plato)


def _imagen_generica(nombre: str) -> str:
    """Imagen de Unsplash Source como fallback (siempre disponible)."""
    query = nombre.replace(" ", "+")
    return f"https://source.unsplash.com/400x300/?food,{query}"


async def detectar_ingredientes(imagen_base64: str, mime_type: str) -> List[str]:
    messages = [{
        "role": "user",
        "content": "Devuelve SOLO este JSON sin backticks: {\"ingredientes\":[\"tomate\",\"huevo\"]}. Lista 5 ingredientes comunes."
    }]
    text = await _call_ai(messages, max_tokens=200)
    parsed = json.loads(text)
    return parsed.get("ingredientes", [])


async def generar_recetas(ingredientes: List[str], filtros: dict = {}) -> List[dict]:
    filtros_texto = ""
    if filtros.get("vegetariano"):
        filtros_texto += " Solo recetas vegetarianas."
    if filtros.get("sin_gluten"):
        filtros_texto += " Sin gluten."
    if filtros.get("tiempo_max"):
        filtros_texto += f" Máximo {filtros['tiempo_max']} minutos."
    if filtros.get("porciones"):
        filtros_texto += f" Para {filtros['porciones']} personas."

    prompt = (
        "Eres un chef latinoamericano. "
        "Devuelve SOLO JSON sin backticks ni texto extra con este formato: "
        "{\"recetas\":[{\"nombre\":\"Huevos Revueltos\",\"emoji\":\"🍳\",\"tiempo_min\":10,\"porciones\":2,"
        "\"dificultad\":\"facil\",\"tags\":\"rapido\",\"match_pct\":95,"
        "\"ingredientes\":[\"huevo\",\"sal\"],\"pasos\":[\"Bate los huevos\",\"Cocina a fuego medio\"]}]}. "
        f"Ingredientes disponibles: {', '.join(ingredientes)}. {filtros_texto}"
        "Genera exactamente 4 recetas variadas."
    )

    messages = [{"role": "user", "content": prompt}]
    text = await _call_ai(messages, max_tokens=1500)
    parsed = json.loads(text)
    recetas = parsed.get("recetas", [])

    # Agregar imagen a cada receta
    for receta in recetas:
        receta["imagen_url"] = await _buscar_imagen_plato(receta.get("nombre", "comida"))

    return recetas


async def generar_recetas_populares(filtros: dict = {}) -> List[dict]:
    """
    Genera recetas populares latinoamericanas cuando no hay ingredientes escaneados.
    Incluye imágenes reales de TheMealDB.
    """
    filtros_texto = ""
    if filtros.get("vegetariano"):
        filtros_texto += " Solo recetas vegetarianas."
    if filtros.get("sin_gluten"):
        filtros_texto += " Sin gluten."
    if filtros.get("tiempo_max"):
        filtros_texto += f" Máximo {filtros['tiempo_max']} minutos."
    if filtros.get("porciones"):
        filtros_texto += f" Para {filtros['porciones']} personas."

    prompt = (
        "Eres un chef latinoamericano experto. "
        "Devuelve SOLO JSON sin backticks ni texto extra con este formato exacto: "
        "{\"recetas\":[{"
        "\"nombre\":\"Arroz con Pollo\","
        "\"emoji\":\"🍗\","
        "\"tiempo_min\":35,"
        "\"porciones\":4,"
        "\"dificultad\":\"facil\","
        "\"tags\":\"popular,proteina\","
        "\"match_pct\":100,"
        "\"descripcion\":\"Un clásico reconfortante con arroz esponjoso y pollo tierno.\","
        "\"ingredientes\":[\"arroz\",\"pollo\",\"zanahoria\",\"cebolla\",\"ajo\",\"sal\",\"aceite\"],"
        "\"pasos\":["
        "\"Saltea el pollo en aceite hasta dorar.\","
        "\"Agrega cebolla y ajo picados, sofríe 3 minutos.\","
        "\"Añade arroz y mezcla bien.\","
        "\"Vierte agua caliente, zanahoria y sal. Tapa y cocina 20 min a fuego bajo.\""
        "]"
        "}]}. "
        f"Genera exactamente 6 recetas latinoamericanas populares y deliciosas, variadas (desayuno, almuerzo, cena, snack).{filtros_texto} "
        "Cada receta debe tener pasos claros y detallados."
    )

    messages = [{"role": "user", "content": prompt}]
    text = await _call_ai(messages, max_tokens=2000)

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        # Intentar limpiar respuesta si viene con backticks
        clean = text.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(clean)

    recetas = parsed.get("recetas", [])

    # Agregar imagen real a cada receta desde TheMealDB
    for receta in recetas:
        receta["imagen_url"] = await _buscar_imagen_plato(receta.get("nombre", "comida"))
        receta["sugerida"] = True  # flag para que la app sepa que son sugerencias

    return recetas
