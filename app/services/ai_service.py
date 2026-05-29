import os
import json
import httpx
from typing import List

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.1-8b-instant"


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
    return parsed.get("recetas", [])
