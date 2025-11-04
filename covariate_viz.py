import plotly.graph_objects as go
from typing import Dict

def create_covariate_chart(forecast: Dict) -> go.Figure:
    covariates = forecast['covariates']
    country_name = forecast['country_name']
    
    if not covariates:
        fig = go.Figure()
        fig.add_annotation(
            text="No covariate data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14)
        )
        fig.update_layout(height=350)
        return fig
    
    covariate_labels = {
        'infant_mortality': 'Infant Mortality Rate',
        'military_power': 'Military Executive Power'
    }
    
    categories = []
    percentiles = []
    colors_list = []
    
    for key, label in covariate_labels.items():
        if key in covariates:
            categories.append(label)
            percentile = covariates[key]
            percentiles.append(percentile)
            
            if percentile >= 80:
                color = 'red'
            elif percentile >= 60:
                color = 'orange'
            elif percentile >= 40:
                color = 'yellow'
            else:
                color = 'lightblue'
            colors_list.append(color)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=categories,
        x=percentiles,
        orientation='h',
        marker=dict(color=colors_list),
        text=[f"{int(p)}%" for p in percentiles],
        textposition='outside',
        hovertemplate='%{y}<br>Percentile: %{x:.0f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'{country_name} - Structural Risk Factors',
        xaxis_title='Percentile',
        yaxis_title='',
        height=350,
        margin=dict(l=150, r=40, t=40, b=40),
        xaxis=dict(range=[0, 105])
    )
    
    return fig