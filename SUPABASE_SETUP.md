# Supabase - Guía de conexión para Fleet Connection Advisor

## Lo que ya está hecho

1. **Proyecto conectado:** `Rappi_Prueba` (`dihvikxxzoqzsriijpmk`)
2. **Tablas creadas** en Supabase:
   - `cities`
   - `weather_forecasts`
   - `fleet_advisor_results`
3. **Archivo local:** `.env` con tu `SUPABASE_URL`

## Diferencia importante: paso 2 de Supabase vs este proyecto

La guía genérica de Supabase (paso 2) asume esto:

```text
React (navegador) --> @supabase/supabase-js --> Supabase
```

**Este MVP NO funciona así.** Usa esta arquitectura:

```text
React (navegador) --> Flask API --> supabase-py --> Supabase
```

El frontend (repo aparte) solo necesita:

```env
VITE_API_BASE_URL=https://fleet-connection-advisor.onrender.com/api
```

## Qué te falta completar (1 paso)

En Supabase Dashboard:

1. Ve a **Project Settings → API**
2. Copia la clave **`service_role`** (secret, no la publishable)
3. Pégala en `.env`:

```env
SUPABASE_SERVICE_ROLE_KEY=tu_service_role_key_aqui
```

> **Importante:** La `service_role` key es secreta. Solo va en el backend, nunca en React ni en GitHub.

También agrega tu `WEATHER_API_KEY` en el mismo archivo.

## Cómo probar que Supabase quedó conectado

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m app.main
```

Luego levanta el frontend desde su repositorio (`Fleet_Connection_Advisor_View`) y evalúa una ciudad.

## Seguridad (RLS)

Las tablas tienen **RLS activado** en Supabase. El backend Flask usa `SUPABASE_SERVICE_ROLE_KEY`, que **bypasea RLS**.

Ver `supabase/schema.sql` para el DDL completo.
