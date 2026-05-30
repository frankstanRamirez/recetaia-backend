import json
from fastapi import APIRouter, HTTPException
from typing import List
from app.database import get_connection
from app.models.schemas import RecetaOut, BuscarRecetasRequest, HistorialCreate, HistorialOut
from app.services.ai_service import generar_recetas, generar_recetas_populares

router = APIRouter()


@router.post("/buscar")
async def buscar_recetas(data: BuscarRecetasRequest):
    """
    Recibe lista de ingredientes y filtros.
    - Si hay ingredientes: genera recetas personalizadas con IA.
    - Si NO hay ingredientes: devuelve recetas populares sugeridas con imágenes.
    """
    try:
        if data.ingredientes:
            # Flujo normal: recetas basadas en ingredientes del usuario
            recetas_ia = await generar_recetas(data.ingredientes, data.filtros or {})
            modo = "personalizado"
            ingredientes_usados = data.ingredientes
        else:
            # Sin ingredientes: sugerencias populares con imágenes
            recetas_ia = await generar_recetas_populares(data.filtros or {})
            modo = "sugerencias_populares"
            ingredientes_usados = []

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar recetas con IA: {str(e)}")

    # Guardar recetas en la BD
    conn = get_connection()
    recetas_guardadas = []
    for r in recetas_ia:
        ingredientes_json = json.dumps(r.get("ingredientes", []), ensure_ascii=False)
        pasos_json = json.dumps(r.get("pasos", []), ensure_ascii=False)
        cursor = conn.execute(
            """INSERT INTO recetas (nombre, emoji, tiempo_min, porciones, dificultad, tags, ingredientes, pasos)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                r.get("nombre", "Sin nombre"),
                r.get("emoji", "🍽"),
                r.get("tiempo_min", 30),
                r.get("porciones", 2),
                r.get("dificultad", "facil"),
                r.get("tags", ""),
                ingredientes_json,
                pasos_json,
            ),
        )
        r["id"] = cursor.lastrowid
        recetas_guardadas.append(r)
    conn.commit()
    conn.close()

    return {
        "recetas": recetas_guardadas,
        "total": len(recetas_guardadas),
        "ingredientes_usados": ingredientes_usados,
        "modo": modo,
        # Mensaje amigable para mostrar en la app
        "mensaje": (
            "Recetas basadas en tus ingredientes 🎯"
            if modo == "personalizado"
            else "¡Aquí tienes recetas populares para inspirarte! 🌟"
        ),
    }


@router.get("/", response_model=List[RecetaOut])
def listar_recetas(limite: int = 20):
    """Lista las recetas guardadas en la base de datos."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM recetas ORDER BY fecha_creada DESC LIMIT ?", (limite,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/{receta_id}")
def obtener_receta(receta_id: int):
    """Obtiene el detalle de una receta por su ID."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM recetas WHERE id = ?", (receta_id,)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Receta no encontrada.")
    r = dict(row)
    try:
        r["ingredientes"] = json.loads(r["ingredientes"])
        r["pasos"] = json.loads(r["pasos"])
    except Exception:
        pass
    return r


@router.post("/historial", response_model=HistorialOut, status_code=201)
def marcar_cocinada(data: HistorialCreate):
    """Registra que el usuario cocinó una receta (para estadísticas)."""
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO historial (receta_id, receta_nombre, dinero_ahorro, comida_g)
           VALUES (?, ?, ?, ?)""",
        (data.receta_id, data.receta_nombre, data.dinero_ahorro, data.comida_g),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM historial WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    conn.close()
    return dict(row)


@router.get("/historial/lista", response_model=List[HistorialOut])
def ver_historial(limite: int = 30):
    """Muestra el historial de recetas cocinadas."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM historial ORDER BY fecha DESC LIMIT ?", (limite,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
