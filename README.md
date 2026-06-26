# Fleet Connection Advisor

MVP end-to-end para evaluar el **impacto climático en la conexión operativa de flota de domiciliarios**. Consulta el clima en tiempo real, simula demanda operativa, calcula impacto financiero, persiste resultados en Supabase y expone un dashboard ejecutivo en React.

---

## Tabla de contenidos

- [Qué hace](#qué-hace)
- [Arquitectura](#arquitectura)
- [Stack tecnológico](#stack-tecnológico)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Requisitos previos](#requisitos-previos)
- [Configuración local](#configuración-local)
- [API REST](#api-rest)
- [Flujo de negocio](#flujo-de-negocio)
- [Variables de entorno](#variables-de-entorno)
- [Despliegue en producción](#despliegue-en-producción)
- [Seguridad](#seguridad)
- [Troubleshooting](#troubleshooting)

---

## Qué hace

1. El usuario ingresa una ciudad (ej. `Bogotá, Colombia`).
2. El backend consulta el clima vía **Weatherstack** (u otro proveedor configurado).
3. Se simula demanda de pedidos y disponibilidad de couriers cuando no hay datos reales.
4. Se calculan métricas financieras, nivel de riesgo y recomendación ejecutiva.
5. Todo se persiste en **Supabase** (ciudad, pronóstico, resultado del advisor).
6. El frontend muestra KPIs, forecast, impacto financiero y ciudades recientes.

---

## Arquitectura

```text
┌─────────────┐      HTTP       ┌──────────────┐      supabase-py      ┌───────────┐
│   React     │ ──────────────► │  Flask API   │ ────────────────────► │ Supabase  │
│   (Vite)    │   /api/*        │  (Python)    │                       │ Postgres  │
└─────────────┘                 └──────┬───────┘                       └───────────┘
                                       │
                                       │ requests
                                       ▼
                                ┌──────────────┐
                                │ Weatherstack │
                                │ (clima)      │
                                └──────────────┘
```

> El frontend **no** se conecta directamente a Supabase. Toda la persistencia pasa por el backend con la `service_role` key.

---

## Stack tecnológico

| Capa | Tecnologías |
|------|-------------|
| **Backend** | Python 3.11+, Flask, Marshmallow, supabase-py, Gunicorn |
| **Frontend** | React 18, Vite, Axios, Recharts, Leaflet |
| **Base de datos** | Supabase (PostgreSQL) con RLS activado |
| **Clima** | [Weatherstack](https://weatherstack.com/) (también soporta OpenWeatherMap y WeatherAPI) |

---

## Estructura del proyecto

```text
Fleet_Connection_Advisor/        # Repositorio backend (GitHub)
├── backend/
│   ├── app/
│   │   ├── api/routes/          # Endpoints REST
│   │   ├── config/              # Settings, logging, startup checks
│   │   ├── domain/
│   │   │   ├── models/          # Entidades de dominio
│   │   │   └── services/        # Lógica de negocio
│   │   ├── infrastructure/
│   │   │   ├── clients/         # Supabase, Weatherstack
│   │   │   └── repositories/    # Acceso a datos
│   │   ├── schemas/             # Validación Marshmallow
│   │   └── utils/
│   ├── supabase/
│   │   └── schema.sql           # DDL para Supabase
│   ├── requirements.txt
│   └── .env.example
├── render.yaml                  # Deploy backend en Render
├── wsgi.py                      # Entrypoint Gunicorn
├── requirements.txt             # Wrapper para Render
├── runtime.txt
├── SUPABASE_SETUP.md
└── README.md

# El frontend vive en un repositorio/proyecto Vercel aparte (carpeta local `frontend/` no versionada aquí).
```

---

## Requisitos previos

- **Python** 3.11+
- **Node.js** 18+
- Cuenta en [Weatherstack](https://weatherstack.com/signup) (plan free disponible)
- Proyecto en [Supabase](https://supabase.com/)

---

## Configuración local

### 1. Clonar e instalar

```bash
git clone <tu-repo>
cd fleet-connection-advisor
```

### 2. Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux
```

Completa `backend/.env` con tus credenciales (ver [Variables de entorno](#variables-de-entorno)).

**Crear tablas en Supabase:**

1. Abre el **SQL Editor** de tu proyecto Supabase.
2. Ejecuta el contenido de [`backend/supabase/schema.sql`](backend/supabase/schema.sql).

**Iniciar el servidor:**

```bash
python -m app.main
```

API disponible en `http://localhost:5000/api`.

Al arrancar verás en consola si la key de clima fue verificada correctamente.

### 3. Frontend

```bash
cd frontend
npm install
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux
npm run dev
```

Dashboard en `http://localhost:5173`.

En desarrollo, Vite hace **proxy** de `/api` hacia Flask en el puerto 5000 (no necesitas CORS manual si usas la URL que muestra Vite).

### 4. Probar el flujo

1. Abre `http://localhost:5173`.
2. Escribe una ciudad, por ejemplo `Bogotá, Colombia`.
3. Haz clic en **Evaluate Fleet Impact**.
4. Revisa KPIs, forecast, impacto financiero y recomendación.
5. La ciudad aparecerá en **Recent cities** (persistida en Supabase).

**Health check rápido:**

```bash
curl http://localhost:5000/api/health
```

---

## API REST

Todas las rutas usan el prefijo `/api` y responden con:

```json
{ "success": true, "data": { ... } }
```

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/health` | Health check del servicio |
| `GET` | `/api/cities` | Lista ciudades recientes (máx. 20) |
| `POST` | `/api/cities` | Crear ciudad manualmente |
| `POST` | `/api/forecast/generate` | Generar pronóstico por ubicación |
| `GET` | `/api/forecast?city_id={uuid}` | Último pronóstico de una ciudad |
| `POST` | `/api/advisor/evaluate` | Evaluar impacto completo de flota |
| `GET` | `/api/advisor/dashboard?city_id={uuid}` | Dashboard cacheado por ciudad |

**Ejemplo — evaluar una ciudad:**

```bash
curl -X POST http://localhost:5000/api/advisor/evaluate \
  -H "Content-Type: application/json" \
  -d '{"location": "Bogota"}'
```

---

## Flujo de negocio

```text
POST /advisor/evaluate { location }
        │
        ├─► Weatherstack → clima actual
        ├─► Supabase     → upsert ciudad + guardar forecast
        ├─► Simulación   → expected_orders, couriers (si no hay datos reales)
        ├─► Financiero   → costos, connection rate, inversión
        └─► Supabase     → guardar advisor result + risk + recommendation
```

Cuando no se envían datos operativos reales, el backend simula demanda y flota. Esos valores quedan marcados con `is_simulated: true` y una nota explicativa.

---

## Variables de entorno

### Backend (`backend/.env`)

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `SUPABASE_URL` | Sí | URL del proyecto Supabase |
| `SUPABASE_SERVICE_ROLE_KEY` | Sí | Clave secreta (`sb_secret_...`). Solo backend |
| `WEATHER_API_PROVIDER` | Sí | `weatherstack`, `openweathermap` o `weatherapi` |
| `WEATHER_API_KEY` | Sí | API key del proveedor de clima |
| `WEATHER_API_BASE_URL` | Sí | Base URL del proveedor |
| `CORS_ALLOWED_ORIGINS` | Sí | Orígenes permitidos separados por coma |
| `FLASK_ENV` | No | `development` o `production` |
| `PORT` | No | Puerto Flask (default: `5000`) |

Variables de negocio (multiplicadores, umbrales de riesgo, simulación): ver [`backend/.env.example`](backend/.env.example).

### Frontend (`frontend/.env`)

| Variable | Descripción |
|----------|-------------|
| `VITE_API_BASE_URL` | URL base de la API. En dev usa `/api` (proxy Vite). En producción, la URL pública del backend |

> Las variables `VITE_*` son **públicas** (van al bundle del navegador). Nunca pongas secretos ahí.

---

## Despliegue en producción

La arquitectura recomendada es **frontend en Vercel** + **backend en Render**:

| Componente | Plataforma | Archivo de config |
|------------|------------|-------------------|
| Frontend React | [Vercel](https://vercel.com) | [`frontend/vercel.json`](frontend/vercel.json) |
| Backend Flask | [Render](https://render.com) | [`render.yaml`](render.yaml) |
| Supabase | Ya en la nube | — |

### Backend en Render

1. Conecta tu repo en Render → **New Blueprint** o **Web Service**.
2. Render detecta `render.yaml` en la raíz del repo (con `rootDir: backend`).
3. Configura las variables secretas en el dashboard:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `WEATHER_API_KEY`
   - `CORS_ALLOWED_ORIGINS` → incluye tu dominio de Vercel
4. Verifica: `https://tu-api.onrender.com/api/health`

### Frontend en Vercel

1. Importa el repo en Vercel.
2. **Root Directory:** `frontend`
3. **Build Command:** `npm run build`
4. **Output Directory:** `dist`
5. Variable de entorno:
   ```env
   VITE_API_BASE_URL=/api
   ```
   El archivo `frontend/vercel.json` hace proxy de `/api/*` hacia Render, así el navegador no necesita CORS cross-origin.

   > Si usas la URL completa de Render (`https://...onrender.com/api`), debes configurar `CORS_ALLOWED_ORIGINS` en el backend con tu dominio de Vercel.

### Conectar ambos

Actualiza `CORS_ALLOWED_ORIGINS` en Render con la URL final de Vercel:

```env
CORS_ALLOWED_ORIGINS=https://tu-app.vercel.app,http://localhost:5173
```

> **Nota:** el plan free de Render pone el backend en sleep tras ~15 min sin tráfico. La primera petición puede tardar ~30 s.

---

## Seguridad

- **Nunca** subas `.env` al repositorio (está en `.gitignore`).
- `SUPABASE_SERVICE_ROLE_KEY` y `WEATHER_API_KEY` van **solo en el backend**.
- El frontend no usa `@supabase/supabase-js`; no expone credenciales de Supabase.
- **RLS activado** en las tablas de Supabase. Bloquea acceso directo desde el navegador; el backend usa `service_role` que bypassa RLS.
- Regenera keys si las compartiste accidentalmente.

Más detalle en [`SUPABASE_SETUP.md`](SUPABASE_SETUP.md).

---

## Troubleshooting

| Problema | Causa probable | Solución |
|----------|----------------|----------|
| `Unable to reach the backend API` | Backend apagado o CORS | Levanta Flask; incluye tu origen en `CORS_ALLOWED_ORIGINS` |
| `Invalid API key` (clima) | Key incorrecta o proveedor mal configurado | Revisa `WEATHER_API_PROVIDER` y `WEATHER_API_BASE_URL` en `.env` |
| Ciudades recientes vacías | Evaluate nunca completó | Confirma clima + Supabase; revisa logs del backend |
| Error Supabase al guardar | Schema no aplicado o key inválida | Ejecuta `schema.sql`; verifica `SUPABASE_SERVICE_ROLE_KEY` |
| CORS en navegador | URL sin `/api` o origen no permitido | Usa `VITE_API_BASE_URL=/api` en Vercel (proxy); o agrega tu dominio Vercel a `CORS_ALLOWED_ORIGINS` en Render |
| Render lento al inicio | Cold start (plan free) | Normal; espera ~30 s o usa plan pago |

**Comandos útiles:**

```bash
# Verificar clima al arrancar
python -m app.main

# Probar evaluate
curl -X POST http://localhost:5000/api/advisor/evaluate \
  -H "Content-Type: application/json" \
  -d '{"location": "Medellin"}'

# Listar ciudades
curl http://localhost:5000/api/cities
```

---

## Licencia

Proyecto de prueba / MVP. Uso interno.
