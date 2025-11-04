import plotly.graph_objects as go
from typing import Dict

def create_temporal_chart(forecast: Dict) -> go.Figure:
    historical_data = forecast['historical']['monthly_data']
    country_name = forecast['country_name']
    target_month = forecast['month']
    target_year = forecast['year']
    
    dates = [d['date'] for d in historical_data]
    fatalities = [d['fatalities'] for d in historical_data]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=fatalities,
        mode='lines+markers',
        name='Historical (all months)',
        line=dict(color='darkgray', width=2),
        marker=dict(size=4)
    ))
    
    if len(fatalities) >= 6:
        rolling_mean = []
        rolling_dates = []
        for i in range(len(fatalities)):
            if i >= 5:
                mean_val = sum(fatalities[max(0, i-5):i+1]) / min(6, i+1)
                rolling_mean.append(mean_val)
                rolling_dates.append(dates[i])
        
        if rolling_mean:
            fig.add_trace(go.Scatter(
                x=rolling_dates,
                y=rolling_mean,
                mode='lines',
                name='6-Month Rolling Average',
                line=dict(color='darkblue', width=2)
            ))
    
    forecast_dates = []
    forecast_values = []
    
    from data_loader import get_loader
    loader = get_loader()
    country_code = forecast['country_code']
    
    for month_config in [(12, 2025), (3, 2026), (9, 2026)]:
        month, year = month_config
        forecast_obj = loader.get_forecast(country_code, month, year)
        if forecast_obj:
            forecast_dates.append(f"{year}-{month:02d}")
            forecast_values.append(forecast_obj['forecast']['predicted_fatalities'])
    
    if forecast_dates:
        fig.add_trace(go.Scatter(
            x=forecast_dates,
            y=forecast_values,
            mode='lines+markers',
            name='Forecast',
            line=dict(color='steelblue', width=2),
            marker=dict(size=8)
        ))
    
    target_date = f"{target_year}-{target_month:02d}"
    target_value = forecast['forecast']['predicted_fatalities']
    
    fig.add_trace(go.Scatter(
        x=[target_date],
        y=[target_value],
        mode='markers+text',
        name=f'Target ({get_month_name(target_month)})',
        marker=dict(size=12, color='steelblue', symbol='diamond'),
        text=[f"{int(target_value)}"],
        textposition='top center',
        textfont=dict(size=11, color='steelblue')
    ))
    
    fig.update_layout(
        title=f'{country_name} - Complete Monthly Fatalities',
        xaxis_title='',
        yaxis_title='Fatalities',
        hovermode='x unified',
        height=350,
        margin=dict(l=40, r=20, t=60, b=40),
        legend=dict(
            orientation='h',
            yanchor='top',
            y=1.15,
            xanchor='left',
            x=0,
            font=dict(size=9)
        )
    )
    
    return fig

def get_month_name(month: int) -> str:
    return {12: "December", 3: "March", 9: "September"}.get(month, str(month))