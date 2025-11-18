from pathlib import Path
import json
from typing import Dict, List, Optional


class ForecastDataLoader:
    def __init__(self, data_path: str = "data/forecast_data.json"):
        self.data_path = Path(data_path)
        self.data: Optional[Dict] = None
        # (country_code, month, year) -> forecast dict
        self.forecasts_by_country_month: Dict[tuple, Dict] = {}
        self.load_data()

    def load_data(self) -> None:
        """Load JSON data and build the (country, month, year) index."""
        with self.data_path.open("r", encoding="utf-8") as f:
            self.data = json.load(f)

        self.forecasts_by_country_month.clear()
        for forecast in self.data["forecasts"]:
            key = (
                forecast["country_code"],
                forecast["month"],
                forecast["year"],
            )
            self.forecasts_by_country_month[key] = forecast

    def get_forecast(self, country_code: str, month: int, year: int) -> Optional[Dict]:
        """Return forecast for a given country-month-year, or None."""
        key = (country_code, month, year)
        return self.forecasts_by_country_month.get(key)

    def get_all_countries(self) -> List[str]:
        countries = set()
        for forecast in self.data["forecasts"]:
            countries.add(forecast["country_code"])
        return sorted(list(countries))

    def get_country_forecasts(self, country_code: str) -> List[Dict]:
        """
        Return all forecasts for a country, sorted chronologically.
        """
        forecasts: List[Dict] = []
        for forecast in self.data["forecasts"]:
            if forecast["country_code"] == country_code:
                forecasts.append(forecast)
        return sorted(forecasts, key=lambda x: (x["year"], x["month"]))

    def get_latest_forecast_for_map(self) -> Dict[str, Dict]:
        """
        Keep for fallback: latest forecast per country.
        Returns dict[country_code] -> forecast dict.
        """
        latest_by_country: Dict[str, Dict] = {}

        for forecast in self.data["forecasts"]:
            country = forecast["country_code"]
            month = forecast["month"]
            year = forecast["year"]

            if country not in latest_by_country:
                latest_by_country[country] = forecast
            else:
                existing = latest_by_country[country]
                if (year > existing["year"]) or (
                    year == existing["year"] and month > existing["month"]
                ):
                    latest_by_country[country] = forecast

        return latest_by_country

    def get_available_periods(self) -> List[Dict[str, int]]:
        """
        Return sorted list of distinct forecast periods as
        [{'year': YYYY, 'month': M}, ...].
        """
        periods = set()
        for forecast in self.data["forecasts"]:
            periods.add((forecast["year"], forecast["month"]))
        sorted_periods = sorted(periods, key=lambda t: (t[0], t[1]))
        return [{"year": y, "month": m} for (y, m) in sorted_periods]

    def get_forecasts_for_period(self, month: int, year: int) -> Dict[str, Dict]:
        """
        Return dict[country_code] -> forecast dict for the given month/year.
        """
        forecasts_for_period: Dict[str, Dict] = {}
        for forecast in self.data["forecasts"]:
            if forecast["year"] == year and forecast["month"] == month:
                forecasts_for_period[forecast["country_code"]] = forecast
        return forecasts_for_period

    def get_metadata(self) -> Dict:
        return self.data.get("metadata", {})


_loader: Optional[ForecastDataLoader] = None


def get_loader() -> ForecastDataLoader:
    global _loader
    if _loader is None:
        _loader = ForecastDataLoader()
    return _loader
