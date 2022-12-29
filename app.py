import pandas as pd
import dash
import dash_bootstrap_components as dbc
from utils import Constants

df_best_role = pd.read_csv(Constants.PLAYER_BEST_ROLE_FILE_CSV)
df_all_role = pd.read_csv(Constants.PLAYER_ALL_ROLE_FILE_CSV)

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.icons.FONT_AWESOME, "https://rsms.me/inter/inter.css"],
    suppress_callback_exceptions=True,
    # Loads icons css and Inter font
)


def create():
    """
    Creates a plotly dashboard on port 8050
    """
    app.layout = serve_layout
    app.run_server(debug=True, port=8050)


def serve_layout():
    navbar = create_nav_bar()
    content = dash.html.Div([dash.page_container], id="pages-content", style={"flex": "1 1 auto"})
    return dash.html.Div([dash.dcc.Location(id="url"), navbar, content],
                         style={"display": "flex", "flex-flow": "column", "height": "100%"})


def create_nav_bar():
    navbar = dbc.NavbarSimple(
        children=[
            dash.html.A(
                [dash.html.Img(src=Constants.MY_LOGO, height="40px")],
                href="/",
                style={"textDecoration": "none"},
            ),
            dbc.NavLink([dash.html.I(className="fa-solid fa-house", style={"margin-right": "10px"}), "Dashboard"],
                        href="/", active="exact"),
            dbc.NavLink([dash.html.I(className="fa-solid fa-user", style={"margin-right": "10px"}), "Players"],
                        href="/players", active="exact"),
            dbc.NavLink(
                [dash.html.I(className="fa-solid fa-people-group", style={"margin-right": "10px"}), "Squad Builder"],
                href="/squad-builder", active="exact"),
            dbc.NavLink([dash.html.I(className="fa-solid fa-circle-down", style={"margin-right": "10px"}), "Scrapping"],
                        href="/scrapping", active="exact"),

        ],
        color="dark",
        dark=True,
        style={"flex": " 0 1 4rem"}
    )

    return navbar

