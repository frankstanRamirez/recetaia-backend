import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "recetaia.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Devuelve filas como diccionarios
    return conn

def init_db():
    """Crea todas las tablas si no existen"""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla de ingredientes escaneados por el usuario
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingredientes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT NOT NULL,
            cantidad    TEXT,
            fecha_escan TEXT DEFAULT (datetime('now')),
            vencimiento TEXT,
            activo      INTEGER DEFAULT 1
        )
    """)

    # Tabla de recetas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recetas (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre        TEXT NOT NULL,
            emoji         TEXT DEFAULT '🍽',
            tiempo_min    INTEGER DEFAULT 30,
            porciones     INTEGER DEFAULT 2,
            dificultad    TEXT DEFAULT 'facil',
            tags          TEXT DEFAULT '',
            ingredientes  TEXT NOT NULL,
            pasos         TEXT NOT NULL,
            fecha_creada  TEXT DEFAULT (datetime('now'))
        )
    """)

    # Tabla de historial (recetas que el usuario marcó como cocinadas)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            receta_id    INTEGER,
            receta_nombre TEXT,
            fecha        TEXT DEFAULT (datetime('now')),
            dinero_ahorro REAL DEFAULT 0,
            comida_g      INTEGER DEFAULT 0,
            FOREIGN KEY (receta_id) REFERENCES recetas(id)
        )
    """)

    # Tabla de preferencias/filtros del usuario
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preferencias (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            clave      TEXT UNIQUE NOT NULL,
            valor      TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Base de datos SQLite inicializada correctamente")
