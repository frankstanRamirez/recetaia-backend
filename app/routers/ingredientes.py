from fastapi import APIRouter, HTTPException
from typing import List
from app.database import get_connection
from app.models.schemas import IngredienteCreate, IngredienteOut, ScanRequest, ScanResponse
from app.services.ai_service import detectar_ingredientes

router = APIRouter()


@router.get("/", response_model=List[IngredienteOut])
def listar_ingredientes():
    """Lista todos los ingredientes activos del inventario."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM ingredientes WHERE activo = 1 ORDER BY fecha_escan DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.post("/", response_model=IngredienteOut, status_code=201)
def agregar_ingrediente(data: IngredienteCreate):
    """Agrega un ingrediente manualmente al inventario."""
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO ingredientes (nombre, cantidad, vencimiento) VALUES (?, ?, ?)",
        (data.nombre.strip(), data.cantidad, data.vencimiento),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM ingredientes WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    conn.close()
    return dict(row)


@router.post("/escanear", response_model=ScanResponse)
async def escanear_imagen(data: ScanRequest):
    """
    Recibe una imagen en base64 y usa IA (Claude) para detectar ingredientes.
    Guarda automáticamente los ingredientes detectados en el inventario.
    """
    try:
        ingredientes = await detectar_ingredientes(data.imagen_base64, data.mime_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al analizar imagen: {str(e)}")

    if not ingredientes:
        raise HTTPException(status_code=422, detail="No se detectaron ingredientes en la imagen.")

    # Guardar en la base de datos
    conn = get_connection()
    for nombre in ingredientes:
        conn.execute(
            "INSERT INTO ingredientes (nombre) VALUES (?)", (nombre,)
        )
    conn.commit()
    conn.close()

    return ScanResponse(
        ingredientes_detectados=ingredientes,
        mensaje=f"Se detectaron {len(ingredientes)} ingrediente(s) correctamente."
    )


@router.delete("/{ingrediente_id}")
def eliminar_ingrediente(ingrediente_id: int):
    """Desactiva un ingrediente del inventario (soft delete)."""
    conn = get_connection()
    conn.execute(
        "UPDATE ingredientes SET activo = 0 WHERE id = ?", (ingrediente_id,)
    )
    conn.commit()
    conn.close()
    return {"mensaje": "Ingrediente eliminado correctamente."}


@router.delete("/limpiar/todo")
def limpiar_inventario():
    """Elimina todos los ingredientes del inventario."""
    conn = get_connection()
    conn.execute("UPDATE ingredientes SET activo = 0")
    conn.commit()
    conn.close()
    return {"mensaje": "Inventario limpiado correctamente."}
