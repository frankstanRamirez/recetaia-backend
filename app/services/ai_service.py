import os
import json
import httpx
from typing import List

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4-20250514"
API_URL = "https://api.anthropic.com/v1/messages"

HEADERS = {
    "x-api-key": ANTHROPIC_API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}


async def detectar_ingredientes(imagen_base64: str, mime_type: str) -> List[str]:
    """
    Envía la imagen a Claude y devuelve la lista de ingredientes detectados.
    """
    payload = {
        "model": CLAUDE_MODEL,
        "max_tokens": 500,
        "system": (
            "Eres un asistente de cocina experto en visión de alimentos. "
            "Analiza la imagen y devuelve SOLO un JSON válido sin backticks ni texto extra: "
            '{"ingredientes":["ingrediente1","ingrediente2",...]}. '
            "Identifica máximo 10 ingredientes visibles. Usa nombres simples en español."
        ),
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": imagen_base64,
                        },
                    },
                    {"type": "text", "text": "¿Qué ingredientes ves en esta imagen?"},
                ],
            }
        ],
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(API_URL, headers=HEADERS, json=payload)
        resp.raise_for_status()
        data = resp.json()
        text = data["content"][0]["text"].strip()
        parsed = json.loads(text)
        return parsed.get("ingredientes", [])


async def generar_recetas(ingredientes: List[str], filtros: dict = {}) -> List[dict]:
    """
    Genera recetas personalizadas basadas en los ingredientes disponibles.
    """
    filtros_texto = ""
    if filtros.get("vegetariano"):
        filtros_texto += " Solo recetas vegetarianas."
    if filtros.get("sin_gluten"):
        filtros_texto += " Sin gluten."
    if filtros.get("tiempo_max"):
        filtros_texto += f" Máximo {filtros['tiempo_max']} minutos de preparación."
    if filtros.get("porciones"):
        filtros_texto += f" Para {filtros['porciones']} personas."

    payload = {
        "model": CLAUDE_MODEL,
        "max_tokens": 1500,
        "system": (
            "Eres un chef profesional latinoamericano. "
            "Devuelve SOLO un JSON válido sin backticks ni texto extra con este formato exacto: "
            '{"recetas":[{"nombre":"...","emoji":"🍳","tiempo_min":20,"porciones":2,'
            '"dificultad":"facil","tags":"rapido,vegetariano",'
            '"match_pct":90,'
            '"ingredientes":["ing1","ing2"],'
            '"pasos":["paso1","paso2"]}]}. '
            "Tags válidos: rapido, vegetariano, proteina. "
            "match_pct indica qué porcentaje de ingredientes el usuario ya tiene (0-100). "
            "Genera exactamente 4 recetas variadas y deliciosas."
        ),
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Ingredientes disponibles: {', '.join(ingredientes)}. "
                    f"{filtros_texto}"
                    "Genera 4 recetas que pueda preparar con estos ingredientes."
                ),
            }
        ],
    }

    async with httpx.AsyncClient(timeout=40) as client:
        resp = await client.post(API_URL, headers=HEADERS, json=payload)
        resp.raise_for_status()
        data = resp.json()
        text = data["content"][0]["text"].strip()
        parsed = json.loads(text)
        return parsed.get("recetas", [])
