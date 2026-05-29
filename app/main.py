from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import ingredientes, recetas, estadisticas

app = FastAPI(
    title="RecetaIA API",
    description="Backend del Escáner de Recetas e Ingredientes — Complejo Educativo Pedro F. Cantor",
    version="1.0.0"
)

# Permite que el frontend (cualquier origen) se conecte al backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/")
def root():
    return {"mensaje": "RecetaIA API funcionando ✅", "version": "1.0.0"}

app.include_router(ingredientes.router, prefix="/api/ingredientes", tags=["Ingredientes"])
app.include_router(recetas.router,      prefix="/api/recetas",      tags=["Recetas"])
app.include_router(estadisticas.router, prefix="/api/estadisticas", tags=["Estadísticas"])
