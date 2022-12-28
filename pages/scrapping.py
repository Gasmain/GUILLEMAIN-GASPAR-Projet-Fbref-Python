import dash
from dash import html, dcc, Output, Input
import dash_bootstrap_components as dbc

from scrapping.fbref import Scrapper
from utils import shared_functions as sf


dash.register_page(__name__)

layout = html.Div(children=[
    html.Div([dash.html.H2(children='Scrapping')], style={}, className="heading"),
    html.Div([
        html.Button("Scrap", id="scrap", className="btn btn-primary"),
        html.Div([
            dcc.Interval(id="progress-interval", n_intervals=0, interval=4000),
            dbc.Progress(label="0%", value=0,id="progress_scrap", striped=True, style={"margin":"0px 10px", "width":"400px"}),
            html.Span(id="scrap_progress_span")
        ], style={"background-color":"white", "padding":"8px", "display":"flex", "align-items":"center", "width":"max-content"}),
    ], style={"padding":"20px", "display":"flex", "align-items":"center", "gap":"20px"}),

    html.Div([
        html.Button("Build Data base", id="build_df", className="btn btn-primary"),
        html.Div([
            dbc.Progress(label="0%", value=0, color="success", id="progress_build",striped=True, style={"margin": "0px 10px", "width": "400px"}),
        ], style={"background-color": "white", "padding": "8px", "display": "flex", "align-items": "center",
                  "width": "max-content"}),
    ], style={"padding": "20px", "display": "flex", "align-items": "center", "gap": "20px"})

])


@dash.callback(
    Output("progress_scrap", "color"),
    Input("scrap", "n_clicks"),
    prevent_initial_call= True
)
def start_scrapping(n_clicks):
    Scrapper.scrap()
    return "success"


@dash.callback(
    Output("progress_build", "value"),
    Output("progress_build", "label"),
    Input("build_df", "n_clicks"),
    prevent_initial_call= True
)
def start_scrapping(n_clicks):
    sf.build_data_frame()
    return 100, "100%"


@dash.callback(
    [Output("progress_scrap", "value"), Output("progress_scrap", "label"), Output("scrap_progress_span", "children")],
    [Input("progress-interval", "n_intervals")],
    prevent_initial_call=True

)
def update_progress(n):
    print("progress : "+str(Scrapper.progress))
    return Scrapper.progress, str(Scrapper.progress)+" %", str(round(Scrapper.progress, 2))+" %"