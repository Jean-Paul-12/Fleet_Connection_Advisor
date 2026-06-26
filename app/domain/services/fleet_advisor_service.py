from typing import Any

from app.config.settings import Settings
from app.domain.models.advisor_result import AdvisorResult
from app.domain.models.financials import FinancialResult
from app.domain.models.fleet import FleetData
from app.domain.models.weather import WeatherForecast
from app.domain.services.financial_service import FinancialService
from app.domain.services.simulation_service import SimulationService


class FleetAdvisorService:
    RECOMMENDATIONS = {
        "LOW": (
            "Fleet connection is stable. Maintain standard incentives and monitor "
            "weather changes."
        ),
        "MEDIUM": (
            "Monitor courier supply closely and prepare selective incentives for zones "
            "with higher rain probability."
        ),
        "HIGH": (
            "Increase courier incentives and activate additional fleet supply to protect "
            "service levels during rainy conditions."
        ),
        "CRITICAL": (
            "Immediate action required: deploy emergency incentives, prioritize "
            "high-demand zones and monitor courier availability in real time."
        ),
    }

    def __init__(self, settings: Settings):
        self._settings = settings
        self._simulation_service = SimulationService(settings)
        self._financial_service = FinancialService(settings)

    def evaluate(
        self,
        city_id: str,
        forecast: WeatherForecast,
        manual_simulation: dict[str, Any] | None = None,
    ) -> AdvisorResult:
        fleet = self._simulation_service.generate(
            rain_probability=forecast.rain_probability,
            manual_data=manual_simulation,
        )
        financials = self._financial_service.calculate(forecast, fleet)
        risk_level = self._resolve_risk_level(forecast, financials)
        recommendation = self.RECOMMENDATIONS[risk_level]

        return AdvisorResult(
            city_id=city_id,
            location=forecast.location,
            forecast=forecast,
            fleet=fleet,
            financials=financials,
            risk_level=risk_level,
            recommendation=recommendation,
        )

    def _resolve_risk_level(
        self, forecast: WeatherForecast, financials: FinancialResult
    ) -> str:
        rain_probability = forecast.rain_probability
        connection_rate = financials.connection_rate

        if (
            rain_probability >= self._settings.high_risk_rain_threshold
            and connection_rate < 0.75
        ):
            return "CRITICAL"

        if (
            rain_probability >= self._settings.medium_risk_rain_threshold
            or connection_rate < 0.85
        ):
            return "HIGH"

        if (
            rain_probability >= self._settings.low_risk_rain_threshold
            or connection_rate < self._settings.target_connection_rate
        ):
            return "MEDIUM"

        return "LOW"
