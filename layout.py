from dash import html, dcc
import plotly.graph_objects as go
from data_loader import get_loader
import temporal_viz
import covariate_viz
import symlog_viz

def create_landing_page():
    loader = get_loader()
    latest_forecasts = loader.get_latest_forecast_for_map()
    
    fig = create_map_figure(latest_forecasts)
    
    return html.Div([
        html.H1("FAST Conflict Forecasts", 
                style={"textAlign": "center", "marginTop": "20px"}),
        html.P("Click on a country to view detailed forecasts",
               style={"textAlign": "center", "color": "#666"}),
        dcc.Graph(
            id="main-map",
            figure=fig,
            style={"height": "700px"}
        )
    ])

def create_map_figure(latest_forecasts):
    country_codes = []
    country_names = []
    predicted_fatalities = []
    risk_categories = []
    colors = []
    
    color_map = {
        "Near-certain no conflict": "#ADD8E6",
        "Improbable conflict": "#FFFF00",
        "Probable conflict": "#FFA500",
        "Near-certain conflict": "#FF0000"
    }
    
    for country_code, forecast in latest_forecasts.items():
        country_codes.append(country_code)
        country_names.append(forecast['country_name'])
        predicted_fatalities.append(forecast['forecast']['predicted_fatalities'])
        risk_category = forecast['forecast']['risk_category']
        risk_categories.append(risk_category)
        colors.append(color_map.get(risk_category, "#CCCCCC"))
    
    fig = go.Figure(data=go.Choropleth(
        locations=country_codes,
        z=predicted_fatalities,
        text=country_names,
        locationmode='ISO-3',
        colorscale='Reds',
        autocolorscale=False,
        marker_line_color='darkgray',
        marker_line_width=0.5,
        colorbar_title="Predicted<br>Fatalities",
        hovertemplate='<b>%{text}</b><br>Predicted: %{z:.1f}<extra></extra>'
    ))
    
    fig.update_geos(
        showframe=False,
        showcoastlines=True,
        projection_type='natural earth',
        lataxis_range=[-40, 40],
        lonaxis_range=[-20, 60]
    )
    
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        geo=dict(
            center=dict(lat=5, lon=25),
            projection_scale=0.8
        )
    )
    
    return fig

def create_detail_page(country_code: str, month: int, year: int):
    loader = get_loader()
    forecast = loader.get_forecast(country_code, month, year)
    
    if not forecast:
        return html.Div([
            html.H2("Forecast not found"),
            html.A("← Back to map", href="/")
        ])
    
    country_name = forecast['country_name']
    available_forecasts = loader.get_country_forecasts(country_code)
    
    month_options = []
    for f in available_forecasts:
        month_name = {12: "December", 3: "March", 9: "September"}[f['month']]
        label = f"{month_name} {f['year']}"
        value = f"{f['month']}-{f['year']}"
        month_options.append({"label": label, "value": value})
    
    current_value = f"{month}-{year}"
    
    return html.Div([
        html.Div([
            html.A("← Back to map", href="/", 
                   style={"fontSize": "14px", "marginBottom": "10px", "display": "inline-block"}),
        ]),
        
        html.Div([
            html.H1(f"{country_name}, {get_month_name(month)} {year}", 
                    style={"display": "inline-block", "marginRight": "20px"}),
            dcc.Dropdown(
                id="month-selector",
                options=month_options,
                value=current_value,
                clearable=False,
                style={"width": "200px", "display": "inline-block"}
            )
        ], style={"marginBottom": "20px"}),
        
        html.Div([
            html.Div([
                html.H3("Summary", style={"marginTop": "0", "marginBottom": "10px"}),
                html.P(forecast['bluf'], style={
                    "fontSize": "18px",
                    "lineHeight": "1.6",
                    "textAlign": "justify"
                })
            ], style={"border": "1px solid #ddd", "padding": "15px", "height": "400px", "overflowY": "auto"}),
            
            html.Div([
                html.H3("Violence trend"),
                dcc.Graph(
                    figure=temporal_viz.create_temporal_chart(forecast),
                    config={'displayModeBar': False},
                    style={"height": "350px"}
                )
            ], style={"border": "1px solid #ddd", "padding": "15px", "height": "400px"})
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px", "marginBottom": "20px"}),
        
        html.Div([
            html.Div([
                html.H3("Structural risk factors"),
                dcc.Graph(
                    figure=covariate_viz.create_covariate_chart(forecast),
                    config={'displayModeBar': False},
                    style={"height": "350px"}
                )
            ], style={"border": "1px solid #ddd", "padding": "15px", "height": "400px"}),
            
            html.Div([
                html.H3("Comparable cases"),
                dcc.Graph(
                    figure=symlog_viz.create_symlog_chart(forecast),
                    config={'displayModeBar': False},
                    style={"height": "350px"}
                )
            ], style={"border": "1px solid #ddd", "padding": "15px", "height": "400px"})
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"})
    ], style={"padding": "20px"})

def get_month_name(month: int) -> str:
    return {12: "December", 3: "March", 9: "September"}.get(month, str(month))