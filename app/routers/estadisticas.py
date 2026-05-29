from fastapi import APIRouter
from app.database import get_connection
from app.models.schemas import EstadisticasOut, PreferenciaItem
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/", response_model=EstadisticasOut)
def obtener_estadisticas():
    """
    Calcula y devuelve todas las estadísticas de ahorro del usuario.
    """
    conn = get_connection()

    # Total de recetas cocinadas
    total = conn.execute("SELECT COUNT(*) FROM historial").fetchone()[0]

    # Dinero ahorrado total
    dinero = conn.execute(
        "SELECT COALESCE(SUM(dinero_ahorro), 0) FROM historial"
    ).fetchone()[0]

    # Comida salvada total en gramos
    comida = conn.execute(
        "SELECT COALESCE(SUM(comida_g), 0) FROM historial"
    ).fetchone()[0]

    # Actividad de los últimos 7 días (un conteo por día)
    actividad = []
    hoy = datetime.now()
    for i in range(6, -1, -1):
        dia = (hoy - timedelta(days=i)).strftime("%Y-%m-%d")
        count = conn.execute(
            "SELECT COUNT(*) FROM historial WHERE fecha LIKE ?", (f"{dia}%",)
        ).fetchone()[0]
        actividad.append(count)

    # Porcentajes por categoría
    def pct_tag(tag):
        if total == 0:
            return 0
        count = conn.execute(
            """SELECT COUNT(*) FROM historial h
               JOIN recetas r ON h.receta_id = r.id
               WHERE r.tags LIKE ?""",
            (f"%{tag}%",),
        ).fetchone()[0]
        return round(count / total * 100)

    pct_veg   = pct_tag("vegetariano")
    pct_prot  = pct_tag("proteina")
    pct_rapid = pct_tag("rapido")

    conn.close()

    return EstadisticasOut(
        total_recetas_cocinadas=total,
        dinero_total_ahorrado=round(dinero, 2),
        comida_total_g=comida,
        actividad_semana=actividad,
        pct_vegetariano=pct_veg,
        pct_proteina=pct_prot,
        pct_rapido=pct_rapid,
    )


@router.get("/preferencias")
def obtener_preferencias():
    """Devuelve las preferencias/filtros guardados del usuario."""
    conn = get_connection()
    rows = conn.execute("SELECT clave, valor FROM preferencias").fetchall()
    conn.close()
    return {r["clave"]: r["valor"] for r in rows}


@router.post("/preferencias")
def guardar_preferencia(data: PreferenciaItem):
    """Guarda o actualiza una preferencia del usuario."""
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO preferencias (clave, valor) VALUES (?, ?)",
        (data.clave, data.valor),
    )
    conn.commit()
    conn.close()
    return {"mensaje": f"Preferencia '{data.clave}' guardada correctamente."}
