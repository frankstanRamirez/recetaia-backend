from pydantic import BaseModel
from typing import Optional, List

# ── Ingredientes ──────────────────────────────────────────
class IngredienteCreate(BaseModel):
    nombre: str
    cantidad: Optional[str] = None
    vencimiento: Optional[str] = None

class IngredienteOut(BaseModel):
    id: int
    nombre: str
    cantidad: Optional[str]
    fecha_escan: str
    vencimiento: Optional[str]
    activo: int

# ── Escaneo con imagen ────────────────────────────────────
class ScanRequest(BaseModel):
    imagen_base64: str          # imagen en base64
    mime_type: str = "image/jpeg"

class ScanResponse(BaseModel):
    ingredientes_detectados: List[str]
    mensaje: str

# ── Recetas ───────────────────────────────────────────────
class RecetaCreate(BaseModel):
    nombre: str
    emoji: Optional[str] = "🍽"
    tiempo_min: int = 30
    porciones: int = 2
    dificultad: str = "facil"
    tags: str = ""
    ingredientes: str           # JSON string con lista de ingredientes
    pasos: str                  # JSON string con lista de pasos

class RecetaOut(BaseModel):
    id: int
    nombre: str
    emoji: str
    tiempo_min: int
    porciones: int
    dificultad: str
    tags: str
    ingredientes: str
    pasos: str
    fecha_creada: str

class BuscarRecetasRequest(BaseModel):
    ingredientes: List[str]
    filtros: Optional[dict] = {}

# ── Historial ─────────────────────────────────────────────
class HistorialCreate(BaseModel):
    receta_id: Optional[int] = None
    receta_nombre: str
    dinero_ahorro: float = 4.5
    comida_g: int = 250

class HistorialOut(BaseModel):
    id: int
    receta_nombre: str
    fecha: str
    dinero_ahorro: float
    comida_g: int

# ── Estadísticas ──────────────────────────────────────────
class EstadisticasOut(BaseModel):
    total_recetas_cocinadas: int
    dinero_total_ahorrado: float
    comida_total_g: int
    actividad_semana: List[int]   # 7 valores, uno por día
    pct_vegetariano: int
    pct_proteina: int
    pct_rapido: int

# ── Preferencias ──────────────────────────────────────────
class PreferenciaItem(BaseModel):
    clave: str
    valor: str
