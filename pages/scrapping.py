import dash
from dash import html, dcc, Output, Input
import dash_bootstrap_components as dbc
from scrapping.fbref import Scrapper
from utils import shared_functions as sf

dash.register_page(__name__)

# TODO : ADD ANOTHER CALLBACK WITH INPUT SCRAP BUTTON TO START DCC.INTERVAL

def layout():
    """
    Builds the layout of the dash page
    :return: returns the content of the layout
    """
    content = html.Div(children=[
        # Triggers a callback every 4 seconds to check if scrapping has progressed
        dcc.Interval(id="progress-interval", n_intervals=0, interval=4000),
        html.Div([dash.html.H2(children='Scrapping')], style={}, className="heading"),
        build_button_progress("Scrap", "scrap"),
        build_button_progress("Build database", "build_df"),
    ])
    return content


def build_button_progress(text, component_id):
    """
    Builds a button and a progress bar
    :param text: the text on the button
    :param component_id: the id of the component
    :return: the component
    """
    component = html.Div([
                    html.Button(text, id=component_id, className="btn btn-primary"),
                    html.Div([
                        dbc.Progress(label="0%", value=0, id="progress_" + component_id, striped=True,
                                     style={"margin": "0px 10px", "width": "400px"}),
                        html.Span(id=component_id + "_span")
                    ], style={"background-color": "white", "padding": "8px", "display": "flex", "align-items": "center",
                              "width": "max-content"}),
    ], style={"padding": "20px", "display": "flex", "align-items": "center", "gap": "20px"})
    return component


@dash.callback(
    Output("progress_scrap", "color"),
    Input("scrap", "n_clicks"),
    prevent_initial_call=True
)
def start_scrapping(n_clicks):
    Scrapper.scrap()  # Call the static method scrap of the scrapper class
    return "success"  # Change progress bar to green when done


@dash.callback(
    Output("progress_build_df", "value"),
    Output("progress_build_df", "label"),
    Output("build_df_span", "children"),
    Input("build_df", "n_clicks"),
    prevent_initial_call=True
)
def start_building_df(n_clicks):
    sf.build_data_frame()
    return 100, "100%", "100%"


@dash.callback(
    Output("progress_scrap", "value"),
    Output("progress_scrap", "label"),
    Output("scrap_span", "children"),
    Input("progress-interval", "n_intervals"),
    prevent_initial_call=True

)
def update_progress(n):
    progress_str = str(round(Scrapper.progress, 2)) + " %"
    return Scrapper.progress, progress_str, progress_str  # Returns the current progress of the scrap
