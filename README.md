#  RecetaIA — Backend

**Proyecto Integrador — Complejo Educativo Pedro F. Cantor**  
Integrantes: Sofia Batres · Nayeli Herrera · Nancy Hernández · Ingrid Bautista · Karla Siguenza

---

## Estructura del proyecto

```
recetaia/
├── app/
│   ├── main.py              # Punto de entrada FastAPI
│   ├── database.py          # Conexión y creación de SQLite
│   ├── models/
│   │   └── schemas.py       # Modelos Pydantic (validación de datos)
│   ├── routers/
│   │   ├── ingredientes.py  # Endpoints de ingredientes + escaneo con IA
│   │   ├── recetas.py       # Endpoints de recetas + historial
│   │   └── estadisticas.py  # Endpoints de estadísticas de ahorro
│   └── services/
│       └── ai_service.py    # Integración con Claude AI (Anthropic)
├── requirements.txt
├── Procfile                 # Para Railway
├── railway.toml             # Configuración de Railway
├── .env.example             # Variables de entorno de ejemplo
└── .gitignore
```

---

## Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Estado del servidor |
| GET | `/api/ingredientes/` | Listar inventario |
| POST | `/api/ingredientes/` | Agregar ingrediente manual |
| POST | `/api/ingredientes/escanear` | **Escanear imagen con IA** |
| DELETE | `/api/ingredientes/{id}` | Eliminar ingrediente |
| POST | `/api/recetas/buscar` | **Generar recetas con IA** |
| GET | `/api/recetas/` | Listar recetas guardadas |
| GET | `/api/recetas/{id}` | Detalle de receta |
| POST | `/api/recetas/historial` | Marcar receta como cocinada |
| GET | `/api/recetas/historial/lista` | Ver historial |
| GET | `/api/estadisticas/` | Estadísticas de ahorro |
| GET | `/api/estadisticas/preferencias` | Ver filtros guardados |
| POST | `/api/estadisticas/preferencias` | Guardar filtro |

Documentación interactiva disponible en: `http://localhost:8000/docs`

---

## Cómo correr localmente

### 1. Instalar Python 3.11+
Descarga desde https://python.org

### 2. Crear entorno virtual
```bash
cd recetaia
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
# Copia el archivo de ejemplo
cp .env.example .env

# Edita .env y pon tu API key de Anthropic
# Consíguela en: https://console.anthropic.com
```

### 5. Correr el servidor
```bash
uvicorn app.main:app --reload
```

El backend estará en: http://localhost:8000  
Documentación en: http://localhost:8000/docs

---

## Deploy en Railway (nube gratis)

### 1. Crear cuenta en Railway
Ve a https://railway.app y crea cuenta con GitHub.

### 2. Subir código a GitHub
```bash
git init
git add .
git commit -m "RecetaIA backend inicial"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/recetaia-backend.git
git push -u origin main
```

### 3. Crear proyecto en Railway
- Entra a railway.app → "New Project" → "Deploy from GitHub repo"
- Selecciona tu repositorio

### 4. Agregar variable de entorno en Railway
- En tu proyecto → "Variables" → "New Variable"
- Nombre: `ANTHROPIC_API_KEY`
- Valor: tu API key de Anthropic

### 5. ¡Listo!
Railway te dará una URL pública como:
`https://recetaia-backend.up.railway.app`

---

## Arquitectura del sistema

```
Frontend (Google AI Studio / React Native)
        |
        | HTTP / JSON
        v
Backend (FastAPI + Python)
  ├── /api/ingredientes  →  Claude Vision AI (detecta ingredientes en fotos)
  ├── /api/recetas       →  Claude AI (genera recetas personalizadas)
  └── /api/estadisticas  →  SQLite (calcula ahorro acumulado)
        |
        v
Base de Datos (SQLite)
  ├── ingredientes  (inventario de la cocina)
  ├── recetas       (recetas generadas)
  ├── historial     (recetas cocinadas)
  └── preferencias  (filtros del usuario)
```

---

## Prompt para Google AI Studio (Frontend)

Copia y pega este prompt en Google AI Studio para que te genere el frontend
que conecta con este backend:

---

```
Crea una aplicación móvil completa en React Native (Expo) que funcione como 
"Escáner de Recetas e Ingredientes". 

El backend ya está desarrollado en Python/FastAPI y está desplegado en Railway.
La URL base del backend es: [PEGAR TU URL DE RAILWAY AQUÍ]

PANTALLAS REQUERIDAS:

1. PANTALLA INICIO / ESCÁNER
   - Botón grande para abrir cámara o galería
   - Al seleccionar foto, convertir a base64 y enviar POST a /api/ingredientes/escanear
     Body: { "imagen_base64": "...", "mime_type": "image/jpeg" }
   - Mostrar chips/tags con los ingredientes detectados (editables)
   - Permitir agregar ingredientes manualmente
   - Botón "Buscar Recetas" que envíe POST a /api/recetas/buscar
     Body: { "ingredientes": ["tomate","pollo",...], "filtros": {} }

2. PANTALLA MIS RECETAS
   - Grid de cards con las recetas generadas
   - Cada card muestra: emoji, nombre, tiempo, porciones, barra de match %
   - Chips de categoría: Vegetariano / Rápido / Proteína
   - Al tocar una receta → pantalla de detalle

3. PANTALLA DETALLE DE RECETA
   - Header con emoji grande
   - Lista de ingredientes
   - Pasos numerados de preparación
   - Botón "¡Ya la preparé!" → POST a /api/recetas/historial
     Body: { "receta_nombre": "...", "receta_id": 1, "dinero_ahorro": 4.5, "comida_g": 250 }

4. PANTALLA ESTADÍSTICAS
   - GET /api/estadisticas/ para obtener datos
   - Mostrar: dinero ahorrado, recetas cocinadas, comida salvada
   - Gráfico de barras de actividad semanal
   - Barras de progreso por categoría

5. PANTALLA FILTROS Y PREFERENCIAS
   - Toggles para: Vegano, Vegetariano, Sin gluten, Sin lactosa
   - Slider para tiempo máximo de preparación
   - Slider para número de porciones
   - Al aplicar → guardar con POST a /api/estadisticas/preferencias

DISEÑO:
- Colores principales: verde #1D9E75 y blanco
- Barra de navegación inferior con 4 tabs: Escáner, Recetas, Estadísticas, Filtros
- Estilo moderno y limpio, similar a apps de cocina populares
- Usar expo-image-picker para la cámara
- Usar axios para las llamadas HTTP al backend

DEPENDENCIAS NECESARIAS:
- expo-image-picker
- axios
- @react-navigation/native
- @react-navigation/bottom-tabs
- react-native-chart-kit (para estadísticas)
```

---

*Proyecto desarrollado con Python + FastAPI + SQLite + Claude AI (Anthropic)*
