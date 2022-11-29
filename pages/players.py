import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from database import Database

dash.register_page(__name__)
db = Database()


def layout(player_id=None, **other_unknown_query_strings):
    player_page = ""
    if player_id != None:
        player_page = html.H2(player_id)

    layout = html.Div(children=[
        html.Div([dash.html.H2(children='Players')], style={}, className="heading"),
        html.Div([
            dbc.Input(id="input", placeholder="Search a player ...", type="text"),
            dbc.Collapse(
                [dbc.ListGroup(id="search_result",
                               style={"margin-top": "20px", "height": "300px", "overflow-y": "scroll"})],
                id="collapse",
                is_open=False,
            ),
            player_page

        ], style={"padding": "20px"}),

    ])
    return layout





@callback(
    Output("collapse", "is_open"),
    [Input("input", "value")]
)
def toggle_collapse(val):
    if val == "" or val is None:
        return False
    return True


@callback(
    Output("search_result", "children"),
    [Input("input", "value")]
)
def fill_search_result(val):
    if val == "" or val is None:
        return None

    result = db.df_best_pos[db.df_best_pos['name'].str.contains(val+"|"+val.capitalize())]

    result_hml = [dbc.ListGroupItem([html.A(row["name"], href="/players?player_id="+row["id"])])
              for index, row in result.iterrows()]
    return result_hml
