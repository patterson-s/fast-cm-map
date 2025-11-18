from dash import html, dcc
import plotly.graph_objects as go
import math
from data_loader import get_loader
import temporal_viz
import covariate_viz
import symlog_viz

def create_landing_page():
    loader = get_loader()
    latest_forecasts = loader.get_latest_forecast_for_map()

    fig = create_map_figure(latest_forecasts, scale_mode="absolute")

    return html.Div([
        html.H1(
            "FAST Conflict Forecasts",
            style={"textAlign": "center", "marginTop": "20px"}
        ),

        html.P(
            "Click on a country to view detailed forecasts",
            style={"textAlign": "center", "color": "#666"}
        ),

        html.P(
            [
                html.A(
                    "Feature Requests",
                    href=(
                        "https://docs.google.com/forms/d/e/"
                        "1FAIpQLSfMafhy-6XGAMGXSmumQUO3NCZSmBa_b1kGJ_Sx8KcSaZnyDA/"
                        "viewform?usp=dialog"
                    ),
                    target="_blank",
                    style={"fontSize": "12px", "color": "#999"},
                )
            ],
            style={
                "textAlign": "center",
                "marginTop": "-10px",
                "marginBottom": "10px"
            }
        ),

        # Toggle + map container
        html.Div([
            # Toggle row aligned near the colorbar
            html.Div(
                [
                    html.Div(style={"flex": 1}),  # left spacer

                    html.Div(
                        [
                            html.Label(
                                "Fatality scale:",
                                style={
                                    "fontWeight": "bold",
                                    "marginRight": "10px"
                                }
                            ),

                            dcc.RadioItems(
                                id="fatality-scale-mode",
                                options=[
                                    {
                                        "label": html.Span(
                                            "Absolute",
                                            style={"marginLeft": "4px"}
                                        ),
                                        "value": "absolute"
                                    },
                                    {
                                        "label": html.Span(
                                            "Log",
                                            style={"marginLeft": "4px"}
                                        ),
                                        "value": "log"
                                    },
                                ],
                                value="absolute",
                                inputStyle={"marginRight": "6px"},
                                labelStyle={
                                    "display": "flex",
                                    "alignItems": "center",
                                    "marginRight": "12px"
                                },
                                inline=True,
                            ),
                        ],
                        style={
                            "display": "flex",
                            "alignItems": "center"
                        }
                    )
                ],
                style={
                    "display": "flex",
                    "flexDirection": "row",
                    "justifyContent": "flex-end",
                    "marginBottom": "5px",
                    "marginRight": "80px"  # adjust horizontal positioning
                }
            ),

            # Map below the toggle
            dcc.Graph(
                id="main-map",
                figure=fig,
                style={"height": "1000px"}
            )
        ])
    ])


def create_map_figure(latest_forecasts, scale_mode: str = "absolute"):
    """
    Build the main choropleth map. `scale_mode` can be "absolute" or "log".
    """
    country_codes = []
    country_names = []
    predicted_fatalities = []
    risk_categories = []

    color_map = {
        "Near-certain no conflict": "#ADD8E6",
        "Improbable conflict": "#FFFF00",
        "Probable conflict": "#FFA500",
        "Near-certain conflict": "#FF0000",
    }

    for country_code, forecast in latest_forecasts.items():
        country_codes.append(country_code)
        country_names.append(forecast["country_name"])
        pf = forecast.get("forecast", {}).get("predicted_fatalities", 0.0) or 0.0
        predicted_fatalities.append(pf)
        risk_category = forecast.get("forecast", {}).get("risk_category", "")
        risk_categories.append(risk_category)

    # Choose z values and colorbar based on scale mode
    if scale_mode == "log":
        z_values = [math.log1p(v) for v in predicted_fatalities]
        max_abs = max(predicted_fatalities) if predicted_fatalities else 0.0

        tick_candidates_abs = [0, 1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000]
        tick_abs = [v for v in tick_candidates_abs if v <= max_abs] or (
            [0, max_abs] if max_abs > 0 else [0]
        )
        tick_vals = [math.log1p(v) for v in tick_abs]
        tick_text = [str(int(v)) for v in tick_abs]

        colorbar = dict(
            title="Predicted fatalities (log scale)",
            tickvals=tick_vals,
            ticktext=tick_text,
        )
    else:
        z_values = predicted_fatalities
        max_abs = max(predicted_fatalities) if predicted_fatalities else 0.0

        if max_abs <= 0:
            tick_abs = [0]
        else:
            step = max_abs / 4.0
            tick_abs = [round(step * i) for i in range(5)]

        colorbar = dict(
            title="Predicted fatalities",
            tickvals=tick_abs,
            ticktext=[str(int(v)) for v in tick_abs],
        )

    fig = go.Figure(
        data=go.Choropleth(
            locations=country_codes,
            z=z_values,
            text=country_names,
            locationmode="ISO-3",
            colorscale="Reds",
            autocolorscale=False,
            marker_line_color="darkgray",
            marker_line_width=0.5,
            colorbar=colorbar,
            # pass absolute fatalities separately for hover
            customdata=predicted_fatalities,
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Predicted fatalities: %{customdata:.1f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_geos(
        showframe=False,
        showcoastlines=True,
        projection_type="natural earth",
        lataxis_range=[-40, 40],
        lonaxis_range=[-20, 60],
    )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        geo=dict(
            center=dict(lat=5, lon=25),
            projection_scale=0.7,
        ),
    )

    return fig


def create_detail_page(country_code: str, month: int, year: int):
    loader = get_loader()
    forecast = loader.get_forecast(country_code, year, month)
    
    if forecast is None:
        return html.Div([
            html.H1("Data not available"),
            html.P("No forecast data is available for the selected country and date."),
            html.A("← Back to map", href="/", 
                   style={"fontSize": "14px", "marginTop": "20px", "display": "inline-block"})
        ], style={"padding": "20px"})
    
    country_name = forecast['country_name']
    
    metadata = loader.get_metadata()
    available_months = metadata.get('months', [])
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
                    "fontSize": "13px",
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
        ], style={"display": "grid", "gridTemplateColumns": "1.5fr 1fr", "gap": "20px", "marginBottom": "20px"}),
        
        html.Div([
            html.Div([
                html.H3("Forecast drivers"),
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
