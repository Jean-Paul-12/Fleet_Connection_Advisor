# Supabase - Guía de conexión para Fleet Connection Advisor

## Lo que ya está hecho

1. **Proyecto conectado:** `Rappi_Prueba` (`dihvikxxzoqzsriijpmk`)
2. **Tablas creadas** en Supabase:
   - `cities`
   - `weather_forecasts`
   - `fleet_advisor_results`
3. **Archivo local:** `backend/.env` con tu `SUPABASE_URL`

## Diferencia importante: paso 2 de Supabase vs este proyecto

La guía genérica de Supabase (paso 2) asume esto:

```text
React (navegador) --> @supabase/supabase-js --> Supabase
```

**Este MVP NO funciona así.** Usa esta arquitectura:

```text
React (navegador) --> Flask API --> supabase-py --> Supabase
```

Por eso **no necesitas** instalar `@supabase/supabase-js` en el frontend para que funcione el dashboard.

| Qué pide Supabase (paso 2) | Qué usa nuestro proyecto |
|----------------------------|--------------------------|
| `VITE_SUPABASE_URL` en frontend | `SUPABASE_URL` en **backend/.env** |
| `VITE_SUPABASE_PUBLISHABLE_KEY` en frontend | `SUPABASE_SERVICE_ROLE_KEY` en **backend/.env** |
| `utils/supabase.ts` en React | `app/infrastructure/clients/supabase_client.py` en Flask |
| `supabase.from('todos').select()` en App | Repositorios Python (`city_repository`, etc.) |

El frontend solo necesita:

```env
VITE_API_BASE_URL=http://localhost:5000/api
```

## Qué te falta completar (1 paso)

En Supabase Dashboard:

1. Ve a **Project Settings → API**
2. Copia la clave **`service_role`** (secret, no la publishable)
3. Pégala en `backend/.env`:

```env
SUPABASE_SERVICE_ROLE_KEY=tu_service_role_key_aqui
```

> **Importante:** La `service_role` key es secreta. Solo va en el backend, nunca en React ni en GitHub.

También agrega tu `WEATHER_API_KEY` en el mismo archivo.

## Cómo probar que Supabase quedó conectado

```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

Luego en otra terminal:

```bash
cd frontend
npm run dev
```

Abre `http://localhost:5173`, evalúa una ciudad y verifica en Supabase → **Table Editor** que aparezcan filas en las 3 tablas.

## Seguridad (RLS)

Las tablas tienen **RLS activado** en Supabase. Esto bloquea acceso directo desde el navegador con la clave `anon`/`publishable`.

El backend Flask usa `SUPABASE_SERVICE_ROLE_KEY`, que **bypasea RLS**, así que la persistencia sigue funcionando con normalidad.

```sql
-- Ya aplicado en el proyecto remoto y en backend/supabase/schema.sql
ALTER TABLE public.cities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.weather_forecasts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fleet_advisor_results ENABLE ROW LEVEL SECURITY;
```

Si en el futuro conectas Supabase directamente desde React, deberás crear políticas explícitas de lectura/escritura para el rol `authenticated`.
