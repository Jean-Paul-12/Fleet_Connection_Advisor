# 🌦️ Fleet Connection Advisor — Frontend

Dashboard web para **inteligencia de inversión en flota** impulsada por el clima. Permite evaluar el impacto meteorológico en la operación de couriers, visualizar KPIs financieros, recomendaciones ejecutivas y la ubicación geográfica de cada ciudad consultada.

> Parte del proyecto **Fleet Connection Advisor**. El backend (Flask + Supabase + WeatherAPI) vive en la carpeta `../backend`.

---

## ✨ Características

- **Búsqueda por ciudad** — ingresa una ciudad (ej. `Bogotá, Colombia`) y evalúa el impacto en la flota.
- **Ciudades recientes** — acceso rápido a consultas previas guardadas en el backend.
- **KPIs ejecutivos** — tasa de conexión, nivel de riesgo, costo incremental por clima e inversión necesaria.
- **Panel de pronóstico** — condición meteorológica, probabilidad de lluvia, temperatura, humedad y viento.
- **Impacto financiero** — desglose de costos operativos normales vs. ajustados por clima.
- **Recomendaciones** — acciones sugeridas según el nivel de riesgo (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- **Gráfico de barras** — comparativa visual de costos e inversión (Recharts).
- **Mapa interactivo** — marcador en OpenStreetMap con las coordenadas de la ciudad (Leaflet).
- **Resumen ejecutivo** — tabla consolidada con métricas de flota y finanzas.
- **Diseño responsive** — adaptable a escritorio y móvil, con paleta inspirada en Rappi.

---

## 🛠️ Stack tecnológico

| Tecnología | Uso |
|------------|-----|
| [React 18](https://react.dev/) | UI y componentes |
| [Vite 5](https://vitejs.dev/) | Bundler y servidor de desarrollo |
| [Axios](https://axios-http.com/) | Cliente HTTP hacia la API |
| [Recharts](https://recharts.org/) | Gráficos de impacto financiero |
| [Leaflet](https://leafletjs.com/) + [react-leaflet](https://react-leaflet.js.org/) | Mapa de ubicación de la ciudad |

---

## 📋 Requisitos previos

- **Node.js** 18 o superior
- **npm** 9 o superior
- Backend Flask corriendo en `http://localhost:5000` (ver [`../backend/README.md`](../backend/README.md))

---

## 🚀 Instalación y ejecución

```bash
# 1. Entrar al directorio del frontend
cd frontend

# 2. Instalar dependencias
npm install

# 3. Configurar variables de entorno
copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux

# 4. Iniciar servidor de desarrollo
npm run dev
```

La aplicación quedará disponible en **http://localhost:5173**.

> **Nota:** no existe el script `npm start`. Usa `npm run dev` para desarrollo.

---

## ⚙️ Variables de entorno

Crea un archivo `.env` a partir de `.env.example`:

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `VITE_API_BASE_URL` | URL base de la API del backend | `/api` |

### Desarrollo local

Con `VITE_API_BASE_URL=/api`, Vite redirige las peticiones al backend Flask mediante proxy:

```
http://localhost:5173/api  →  http://127.0.0.1:5000/api
```

### Producción (Vercel)

Apunta a la URL pública del backend desplegado:

```env
VITE_API_BASE_URL=https://tu-backend.onrender.com/api
```

---

## 📜 Scripts disponibles

| Comando | Descripción |
|---------|-------------|
| `npm run dev` | Servidor de desarrollo con hot reload (puerto 5173) |
| `npm run build` | Genera el build de producción en `dist/` |
| `npm run preview` | Sirve localmente el build de producción |

---

## 🔌 Integración con la API

El cliente HTTP está centralizado en `src/api/advisorApi.js`.

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/cities` | Lista ciudades consultadas recientemente |
| `POST` | `/api/advisor/evaluate` | Evalúa impacto de flota para una ubicación |
| `GET` | `/api/advisor/dashboard?city_id={id}` | Recupera el dashboard de una ciudad guardada |

**Ejemplo de body para evaluar:**

```json
{
  "location": "Bogotá, Colombia"
}
```

**Respuesta esperada (campos principales):**

```json
{
  "location": { "name": "Bogotá", "country": "Colombia", "latitude": 4.711, "longitude": -74.0721 },
  "forecast": { "weather_condition": "Moderate rain", "rain_probability": 0.72, "temperature": 16 },
  "fleet": { "expected_orders": 11200, "required_couriers": 2800, "available_couriers": 2240 },
  "financials": { "connection_rate": 0.8, "investment_needed": 8400 },
  "risk_level": "CRITICAL",
  "recommendation": "Immediate action required..."
}
```

Si el backend no está disponible, la UI muestra un mensaje de error indicando que la API debe estar activa en el puerto 5000.

---

## 📁 Estructura del proyecto

```
frontend/
├── index.html                 # Punto de entrada HTML (título 🌦️ + favicon)
├── vite.config.js             # Configuración Vite y proxy /api
├── vercel.json                # Rewrites SPA para despliegue en Vercel
├── .env.example               # Plantilla de variables de entorno
└── src/
    ├── main.jsx               # Bootstrap de React
    ├── App.jsx                # Componente raíz
    ├── api/
    │   └── advisorApi.js      # Cliente Axios y funciones de la API
    ├── pages/
    │   └── Dashboard.jsx      # Vista principal del dashboard
    ├── components/
    │   ├── CitySearchInput.jsx
    │   ├── CityLocationMap.jsx
    │   ├── RecentCitiesDropdown.jsx
    │   ├── MetricCard.jsx
    │   ├── WeatherRiskBadge.jsx
    │   ├── ForecastChart.jsx
    │   ├── FinancialImpactPanel.jsx
    │   ├── RecommendationPanel.jsx
    │   └── SimulationNotice.jsx
    └── styles/
        ├── global.css         # Estilos globales y layout
        └── theme.js           # Colores y tokens de diseño
```

---

## 🚢 Despliegue

El frontend está preparado para **Vercel**:

1. Conecta el repositorio en Vercel con **Root Directory** = `frontend`.
2. Configura `VITE_API_BASE_URL` con la URL pública del backend.
3. El archivo `vercel.json` redirige todas las rutas a `index.html` (SPA).

Build command: `npm run build`  
Output directory: `dist`

---

## 🎨 Paleta de colores

| Token | Valor | Uso |
|-------|-------|-----|
| Primary | `#FF441F` | Acentos y gradiente del header |
| Secondary | `#FFD447` | Gradiente del header |
| Background | `#FFF8F2` | Fondo general |
| Risk LOW | `#22C55E` | Badge de riesgo bajo |
| Risk CRITICAL | `#991B1B` | Badge de riesgo crítico |

---

## 👤 Autor

Desarrollado por **Jean Paul Quitian**

---

## 📄 Licencia

Proyecto privado — uso interno / evaluación técnica.
