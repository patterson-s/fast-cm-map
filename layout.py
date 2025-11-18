from typing import Dict, List

from dash import html, dcc
import plotly.graph_objects as go
import math

from data_loader import get_loader
import temporal_viz
import covariate_viz
import symlog_viz


def get_month_name(month: int) -> str:
    month_map = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }
    return month_map.get(month, str(month))


def create_map_figure(
    forecasts_by_country: Dict[str, Dict],
    scale_mode: str = "absolute",
) -> go.Figure:
    """
    Build the main choropleth map for a given set of forecasts.
    forecasts_by_country: dict[country_code] -> forecast dict.
    scale_mode: 'absolute' or 'log'.
    """
    country_codes: List[str] = []
    country_names: List[str] = []
    predicted_fatalities: List[float] = []

    for country_code, forecast in forecasts_by_country.items():
        country_codes.append(country_code)
        country_names.append(forecast["country_name"])
        pf = forecast.get("forecast", {}).get("predicted_fatalities", 0.0) or 0.0
        predicted_fatalities.append(pf)

    if scale_mode == "log":
        # log1p so zero stays at 0
        z_values = [math.log1p(v) if v > 0 else 0 for v in predicted_fatalities]
        colorbar_title = "log(1 + predicted fatalities)"
    else:
        z_values = predicted_fatalities
        colorbar_title = "Predicted fatalities"

    fig = go.Figure(
        go.Choropleth(
            locations=country_codes,
            z=z_values,
            text=country_names,
            locationmode="ISO-3",
            colorscale="Reds",
            autocolorscale=False,
            marker_line_color="darkgray",
            marker_line_width=0.5,
            colorbar=dict(title=colorbar_title, thickness=12, len=0.6),
            customdata=predicted_fatalities,
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Predicted fatalities: %{customdata:.1f}"
                "<extra></extra>"
            ),
        )
    )

    # Simple, stable world view – no manual projection scale so it doesn't jump
    fig.update_layout(
    margin=dict(l=0, r=0, t=10, b=0),
    geo=dict(
        showframe=False,
        showcoastlines=True,
        coastlinecolor="rgba(0,0,0,0.3)",
        projection_type="natural earth",
        # Center roughly on Sudan
        center=dict(lat=12, lon=30),
        # Zoom level – increase/decrease to taste
        projection_scale=1.7,
        ),
    )
    return fig


def create_landing_page():
    loader = get_loader()

    # Build forecast-period selector options (latest period as default)
    periods = loader.get_available_periods()
    if periods:
        default_period = periods[-1]
        default_month = default_period["month"]
        default_year = default_period["year"]
        period_value = f"{default_month}-{default_year}"
        period_options = [
            {
                "label": f"{get_month_name(p['month'])} {p['year']}",
                "value": f"{p['month']}-{p['year']}",
            }
            for p in periods
        ]
        forecasts_for_period = loader.get_forecasts_for_period(default_month, default_year)
    else:
        # Fallback to "latest" behaviour if something is odd with metadata
        period_value = None
        period_options = []
        forecasts_for_period = loader.get_latest_forecast_for_map()

    fig = create_map_figure(forecasts_for_period, scale_mode="absolute")

    return html.Div(
        [
            html.H1(
                "FAST Conflict Forecasts",
                style={"textAlign": "center", "marginTop": "20px"},
            ),
            html.P(
                "Click on a country to view detailed forecasts",
                style={"textAlign": "center", "color": "#666"},
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
                    "marginBottom": "5px",
                },
            ),
            # Controls block: forecast period on first line, fatality scale under it
            html.Div(
                [
                    html.Div(
                        [
                            html.Label(
                                "Forecast period:",
                                style={
                                    "fontWeight": "bold",
                                    "marginRight": "8px",
                                },
                            ),
                            dcc.Dropdown(
                                id="forecast-period-selector",
                                options=period_options,
                                value=period_value,
                                clearable=False,
                                placeholder="Select forecast period",
                                style={"width": "260px"},
                            ),
                        ],
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "marginBottom": "6px",
                        },
                    ),
                    html.Div(
                        [
                            html.Label(
                                "Fatality scale:",
                                style={
                                    "fontWeight": "bold",
                                    "marginRight": "10px",
                                },
                            ),
                            dcc.RadioItems(
                                id="fatality-scale-mode",
                                options=[
                                    {
                                        "label": html.Span(
                                            "Absolute",
                                            style={"marginLeft": "4px"},
                                        ),
                                        "value": "absolute",
                                    },
                                    {
                                        "label": html.Span(
                                            "Log",
                                            style={"marginLeft": "4px"},
                                        ),
                                        "value": "log",
                                    },
                                ],
                                value="absolute",
                                inputStyle={"marginRight": "6px"},
                                labelStyle={
                                    "display": "flex",
                                    "alignItems": "center",
                                    "marginRight": "12px",
                                },
                                inline=True,
                            ),
                        ],
                        style={
                            "display": "flex",
                            "alignItems": "center",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "alignItems": "center",
                    "marginTop": "10px",
                    "marginBottom": "10px",
                },
            ),
            dcc.Graph(
                id="main-map",
                figure=fig,
                style={"height": "800px"},
            ),
        ]
    )


def create_detail_page(country_code: str, month: int, year: int):
    loader = get_loader()
    # IMPORTANT: (country, month, year) – keep this order
    forecast = loader.get_forecast(country_code, month, year)

    if forecast is None:
        return html.Div(
            [
                html.H1("Data not available"),
                html.P(
                    "No forecast data is available for the selected country and date."
                ),
                html.A(
                    "← Back to map",
                    href="/",
                    style={
                        "fontSize": "14px",
                        "marginTop": "20px",
                        "display": "inline-block",
                    },
                ),
            ],
            style={"padding": "20px"},
        )

    country_name = forecast["country_name"]

    # Build options for the month dropdown specific to this country
    available_forecasts = loader.get_country_forecasts(country_code)
    month_options = []
    for f in available_forecasts:
        month_name = get_month_name(f["month"])
        label = f"{month_name} {f['year']}"
        value = f"{f['month']}-{f['year']}"
        month_options.append({"label": label, "value": value})

    current_value = f"{month}-{year}"

    temporal_fig = temporal_viz.create_temporal_chart(forecast)
    covariate_fig = covariate_viz.create_covariate_chart(forecast)
    symlog_fig = symlog_viz.create_symlog_chart(forecast)

    return html.Div(
        [
            html.Div(
                [
                    html.A(
                        "← Back to map",
                        href="/",
                        style={
                            "fontSize": "14px",
                            "marginBottom": "10px",
                            "display": "inline-block",
                        },
                    ),
                ]
            ),
            html.Div(
                [
                    html.H1(
                        f"{country_name}, {get_month_name(month)} {year}",
                        style={"display": "inline-block", "marginRight": "20px"},
                    ),
                    dcc.Dropdown(
                        id="month-selector",
                        options=month_options,
                        value=current_value,
                        clearable=False,
                        style={"width": "200px", "display": "inline-block"},
                    ),
                ],
                style={"marginBottom": "20px"},
            ),
            # Row 1: Summary + Historical conflict trends
            html.Div(
                [
                    html.Div(
                        [
                            html.H3(
                                "Summary",
                                style={"marginTop": "0", "marginBottom": "10px"},
                            ),
                            html.P(
                                forecast.get("bluf", ""),
                                style={
                                    "fontSize": "13px",
                                    "lineHeight": "1.5",
                                },
                            ),
                        ],
                        style={
                            "border": "1px solid #ddd",
                            "padding": "15px",
                            "height": "350px",
                            "overflowY": "auto",
                        },
                    ),
                    html.Div(
                        [
                            html.H3("Historical conflict trends"),
                            dcc.Graph(
                                figure=temporal_fig,
                                config={"displayModeBar": False},
                                style={"height": "300px"},
                            ),
                        ],
                        style={
                            "border": "1px solid #ddd",
                            "padding": "15px",
                            "height": "350px",
                        },
                    ),
                ],
                style={
                    "display": "grid",
                    "gridTemplateColumns": "1.2fr 2fr",
                    "gap": "20px",
                    "marginBottom": "20px",
                },
            ),
            # Row 2: Structural risk factors + Comparable cases
            html.Div(
                [
                    html.Div(
                        [
                            html.H3("Structural risk factors"),
                            dcc.Graph(
                                figure=covariate_fig,
                                config={"displayModeBar": False},
                                style={"height": "300px"},
                            ),
                        ],
                        style={
                            "border": "1px solid #ddd",
                            "padding": "15px",
                            "height": "350px",
                        },
                    ),
                    html.Div(
                        [
                            html.H3("Comparable cases"),
                            dcc.Graph(
                                figure=symlog_fig,
                                config={"displayModeBar": False},
                                style={"height": "300px"},
                            ),
                        ],
                        style={
                            "border": "1px solid #ddd",
                            "padding": "15px",
                            "height": "350px",
                        },
                    ),
                ],
                style={
                    "display": "grid",
                    "gridTemplateColumns": "1fr 1fr",
                    "gap": "20px",
                },
            ),
        ],
        style={"padding": "20px"},
    )
