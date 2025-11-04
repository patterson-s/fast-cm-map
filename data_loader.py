from pathlib import Path
import json
from typing import Dict, List, Optional

class ForecastDataLoader:
    def __init__(self, data_path: str = "data/forecast_data.json"):
        self.data_path = Path(data_path)
        self.data = None
        self.forecasts_by_country_month = {}
        self.load_data()
    
    def load_data(self):
        with open(self.data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        for forecast in self.data['forecasts']:
            key = (
                forecast['country_code'],
                forecast['month'],
                forecast['year']
            )
            self.forecasts_by_country_month[key] = forecast
    
    def get_forecast(self, country_code: str, month: int, year: int) -> Optional[Dict]:
        key = (country_code, month, year)
        return self.forecasts_by_country_month.get(key)
    
    def get_all_countries(self) -> List[str]:
        countries = set()
        for forecast in self.data['forecasts']:
            countries.add(forecast['country_code'])
        return sorted(list(countries))
    
    def get_country_forecasts(self, country_code: str) -> List[Dict]:
        forecasts = []
        for forecast in self.data['forecasts']:
            if forecast['country_code'] == country_code:
                forecasts.append(forecast)
        return sorted(forecasts, key=lambda x: (x['year'], x['month']))
    
    def get_latest_forecast_for_map(self) -> Dict[str, Dict]:
        latest_by_country = {}
        
        for forecast in self.data['forecasts']:
            country = forecast['country_code']
            month = forecast['month']
            year = forecast['year']
            
            if country not in latest_by_country:
                latest_by_country[country] = forecast
            else:
                existing = latest_by_country[country]
                if (year > existing['year']) or (year == existing['year'] and month > existing['month']):
                    latest_by_country[country] = forecast
        
        return latest_by_country
    
    def get_metadata(self) -> Dict:
        return self.data.get('metadata', {})

_loader = None

def get_loader() -> ForecastDataLoader:
    global _loader
    if _loader is None:
        _loader = ForecastDataLoader()
    return _loader