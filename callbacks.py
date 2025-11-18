from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

import layout
from data_loader import get_loader
from app import app  # noqa: F401  (ensures app is created before callbacks)


@callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def display_page(pathname):
    """
    Simple router between landing page and country detail pages.
    """
    if pathname is None or pathname == "/":
        return layout.create_landing_page()

    if pathname.startswith("/country/"):
        parts = pathname.split("/")
        if len(parts) >= 4:
            country_code = parts[2]
            month_year = parts[3]
            try:
                month_str, year_str = month_year.split("-")
                month = int(month_str)
                year = int(year_str)
            except Exception:
                return layout.create_landing_page()

            return layout.create_detail_page(country_code, month, year)

    return layout.create_landing_page()


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("main-map", "clickData"),
    State("forecast-period-selector", "value"),
    prevent_initial_call=True,
)
def map_click(clickData, period_value):
    """
    When the user clicks a country on the map, navigate to
    /country/{CODE}/{month}-{year} using the selected forecast period.
    """
    if clickData is None or period_value is None:
        raise PreventUpdate

    try:
        country_code = clickData["points"][0]["location"]
    except Exception:
        raise PreventUpdate

    try:
        month_str, year_str = period_value.split("-")
        month = int(month_str)
        year = int(year_str)
    except Exception:
        raise PreventUpdate

    return f"/country/{country_code}/{month}-{year}"


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("month-selector", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def month_change(month_year_value, current_pathname):
    """
    On the detail page, update the URL when the month dropdown changes.
    """
    if month_year_value is None or current_pathname is None:
        raise PreventUpdate

    if not current_pathname.startswith("/country/"):
        raise PreventUpdate

    parts = current_pathname.split("/")
    if len(parts) >= 3:
        country_code = parts[2]
        return f"/country/{country_code}/{month_year_value}"

    raise PreventUpdate


@callback(
    Output("main-map", "figure"),
    Input("fatality-scale-mode", "value"),
    Input("forecast-period-selector", "value"),
)
def update_main_map(scale_mode, period_value):
    """
    Rebuild the main map when the user changes the fatality scale
    or the forecast period.
    """
    if scale_mode is None or period_value is None:
        raise PreventUpdate

    try:
        month_str, year_str = period_value.split("-")
        month = int(month_str)
        year = int(year_str)
    except Exception:
        raise PreventUpdate

    loader = get_loader()
    forecasts_for_period = loader.get_forecasts_for_period(month=month, year=year)
    return layout.create_map_figure(forecasts_for_period, scale_mode=scale_mode)
