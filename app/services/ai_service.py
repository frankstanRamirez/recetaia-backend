import os
import json
import httpx
from typing import List

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def _openrouter_post(prompt: str, max_tokens: int = 1000) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "google/gemma-3-27b-it:free",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}]
    }
    async with httpx.AsyncClient(timeout=40) as client:
        resp = await client.post(OPENROUTER_URL, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


async def detectar_ingredientes(imagen_base64: str, mime_type: str) -> List[str]:
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "google/gemma-3-27b-it:free",
        "max_tokens": 500,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{imagen_base64}"}},
                {"type": "text", "text": "Analiza la imagen y devuelve SOLO un JSON válido sin backticks: {\"ingredientes\":[\"ingrediente1\",\"ingrediente2\"]}. Máximo 10 ingredientes en español."}
            ]
        }]
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(OPENROUTER_URL, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["message"]["content"].strip()
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

    text = await _openrouter_post(prompt, max_tokens=1500)
    parsed = json.loads(text)
    return parsed.get("recetas", [])
