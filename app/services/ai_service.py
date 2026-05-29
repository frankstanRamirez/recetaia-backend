import os
import json
import httpx
from typing import List

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"


async def _gemini_post(prompt: str, max_tokens: int = 1000) -> str:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": max_tokens}
    }
    async with httpx.AsyncClient(timeout=40) as client:
        resp = await client.post(GEMINI_URL, headers=headers, params=params, json=body)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()


async def detectar_ingredientes(imagen_base64: str, mime_type: str) -> List[str]:
    GEMINI_VISION_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    body = {
        "contents": [{
            "parts": [
                {"inline_data": {"mime_type": mime_type, "data": imagen_base64}},
                {"text": "Analiza la imagen y devuelve SOLO un JSON válido sin backticks: {\"ingredientes\":[\"ingrediente1\",\"ingrediente2\"]}. Máximo 10 ingredientes en español."}
            ]
        }],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 500}
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(GEMINI_VISION_URL, headers=headers, params=params, json=body)
        resp.raise_for_status()
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
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
        "Eres un chef profesional latinoamericano. "
        "Devuelve SOLO un JSON válido sin backticks con este formato exacto: "
        "{\"recetas\":[{\"nombre\":\"...\",\"emoji\":\"🍳\",\"tiempo_min\":20,\"porciones\":2,"
        "\"dificultad\":\"facil\",\"tags\":\"rapido,vegetariano\","
        "\"match_pct\":90,"
        "\"ingredientes\":[\"ing1\",\"ing2\"],"
        "\"pasos\":[\"paso1\",\"paso2\"]}]}. "
        "Tags válidos: rapido, vegetariano, proteina. "
        "match_pct es qué porcentaje de ingredientes el usuario ya tiene (0-100). "
        f"Ingredientes disponibles: {', '.join(ingredientes)}. {filtros_texto}"
        "Genera exactamente 4 recetas variadas y deliciosas."
    )

    text = await _gemini_post(prompt, max_tokens=1500)
    parsed = json.loads(text)
    return parsed.get("recetas", [])
