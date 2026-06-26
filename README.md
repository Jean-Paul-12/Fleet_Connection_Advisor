# Fleet Connection Advisor — Backend

Flask API for weather-driven fleet investment intelligence.

Repositorio: [Fleet_Connection_Advisor](https://github.com/Jean-Paul-12/Fleet_Connection_Advisor)  
Frontend (separado): [Fleet_Connection_Advisor_View](https://github.com/Jean-Paul-12/Fleet_Connection_Advisor_View)

## Setup local

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m app.main
```

API en `http://localhost:5000/api`.

## Deploy (Render)

- **Build:** `pip install -r requirements.txt`
- **Start:** `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
- **Health:** `/api/health`

Ver `render.yaml` y `SUPABASE_SETUP.md` para más detalle.

Apply `supabase/schema.sql` in your Supabase SQL Editor before using persistence endpoints.
