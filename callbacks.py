from dash import Input, Output, State, callback, ctx
from dash.exceptions import PreventUpdate
import layout
from data_loader import get_loader

from app import app

@callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname is None or pathname == "/":
        return layout.create_landing_page()
    
    if pathname.startswith("/country/"):
        parts = pathname.split("/")
        if len(parts) >= 4:
            country_code = parts[2]
            month_year = parts[3]
            
            try:
                month, year = month_year.split("-")
                month = int(month)
                year = int(year)
                return layout.create_detail_page(country_code, month, year)
            except:
                return layout.create_landing_page()
    
    return layout.create_landing_page()

@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("main-map", "clickData"),
    prevent_initial_call=True
)
def map_click(clickData):
    if clickData is None:
        raise PreventUpdate
    
    try:
        country_code = clickData['points'][0]['location']
        return f"/country/{country_code}/12-2025"
    except:
        raise PreventUpdate

@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("month-selector", "value"),
    State("url", "pathname"),
    prevent_initial_call=True
)
def month_change(month_year_value, current_pathname):
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
)
def update_main_map(scale_mode):
    """
    Rebuild the main map when the user toggles between
    absolute and log fatality scales.
    """
    if scale_mode is None:
        raise PreventUpdate

    loader = get_loader()
    latest_forecasts = loader.get_latest_forecast_for_map()
    return layout.create_map_figure(latest_forecasts, scale_mode=scale_mode)
