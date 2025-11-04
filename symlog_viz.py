import plotly.graph_objects as go
from typing import Dict
import numpy as np

def create_symlog_chart(forecast: Dict) -> go.Figure:
    regional_context = forecast['regional_context']
    country_code = forecast['country_code']
    country_name = forecast['country_name']
    month = forecast['month']
    year = forecast['year']
    cohort = forecast['cohort']
    
    color_map = {
        "Near-certain no conflict": "#ADD8E6",
        "Improbable conflict": "#FFFF00",
        "Probable conflict": "#FFA500",
        "Near-certain conflict": "#FF0000"
    }
    
    from data_loader import get_loader
    loader = get_loader()
    
    all_countries_data = []
    for country in regional_context:
        country_forecast = loader.get_forecast(country['country_code'], month, year)
        if country_forecast:
            risk_cat = country_forecast['forecast']['risk_category']
            all_countries_data.append({
                'code': country['country_code'],
                'name': country['country_name'],
                'prob': country['probability'],
                'predicted': country['predicted_fatalities'],
                'risk_category': risk_cat,
                'color': color_map.get(risk_cat, '#CCCCCC')
            })
    
    fig = go.Figure()
    
    for category, color in color_map.items():
        category_data = [d for d in all_countries_data if d['risk_category'] == category]
        if category_data:
            fig.add_trace(go.Scatter(
                x=[d['prob'] for d in category_data],
                y=[d['predicted'] for d in category_data],
                mode='markers',
                name=category,
                marker=dict(size=8, color=color, opacity=0.7, line=dict(color='gray', width=0.5)),
                text=[d['name'] for d in category_data],
                hovertemplate='%{text}<br>Probability: %{x:.3f}<br>Predicted: %{y:.1f}<extra></extra>'
            ))
    
    target_data = [d for d in all_countries_data if d['code'] == country_code]
    if target_data:
        target = target_data[0]
        fig.add_trace(go.Scatter(
            x=[target['prob']],
            y=[target['predicted']],
            mode='markers',
            name=f'{country_name} (target)',
            marker=dict(size=15, color='darkred', symbol='diamond', 
                       line=dict(color='black', width=2)),
            text=[country_name],
            hovertemplate='%{text}<br>Probability: %{x:.3f}<br>Predicted: %{y:.1f}<extra></extra>'
        ))
    
    fig.add_vline(x=0.01, line_dash="dash", line_color="blue", opacity=0.7, line_width=1)
    fig.add_vline(x=0.50, line_dash="dash", line_color="blue", opacity=0.7, line_width=1)
    fig.add_vline(x=0.99, line_dash="dash", line_color="blue", opacity=0.7, line_width=1)
    
    fig.add_hline(y=10, line_dash="dash", line_color="green", opacity=0.7, line_width=1)
    fig.add_hline(y=100, line_dash="dash", line_color="green", opacity=0.7, line_width=1)
    fig.add_hline(y=1000, line_dash="dash", line_color="green", opacity=0.7, line_width=1)
    
    y_min = 0
    y_max = max([d['predicted'] for d in all_countries_data]) * 1.1 if all_countries_data else 1000
    
    fig.update_layout(
        title=f'Regional Conflict Forecast Distribution - {get_month_name(month)} {year}',
        xaxis_title='Probability of ≥25 Fatalities',
        yaxis_title='Predicted Fatalities',
        height=350,
        margin=dict(l=40, r=20, t=40, b=40),
        xaxis=dict(range=[-0.05, 1.05]),
        yaxis=dict(type='linear', range=[y_min, y_max]),
        legend=dict(orientation='v', yanchor='top', y=1, xanchor='left', x=1.02),
        hovermode='closest'
    )
    
    return fig

def get_month_name(month: int) -> str:
    return {12: "December", 3: "March", 9: "September"}.get(month, str(month))