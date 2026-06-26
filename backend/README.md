# Fleet Connection Advisor - Backend

Flask API for weather-driven fleet investment intelligence.

## Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Configure `.env` with Supabase and WeatherAPI credentials, then run:

```bash
python -m app.main
```

Apply `supabase/schema.sql` in your Supabase SQL Editor before using persistence endpoints.
