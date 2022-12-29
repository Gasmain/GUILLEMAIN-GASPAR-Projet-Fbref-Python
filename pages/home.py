import dash
import pandas as pd
from dash import html, dcc, Output, Input, callback, State
import plotly.express as px
import plotly.graph_objects as go
import app
from utils import Constants

dash.register_page(__name__, path='/')
columns = app.df_best_role.filter(like='_per90').columns


def build_scatter_plot(x, y):
    fig = px.scatter(app.df_best_role, x=x, y=y, hover_data=['name'], color='roles')
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    return fig


def build_histogram(metric):
    fig = px.histogram(app.df_best_role, x=metric)
    return fig


def build_map():
    nation_df = pd.read_csv(Constants.MAP_CSV)

    fig = go.Figure(data=go.Choropleth(
        locations=nation_df['code'],
        z=nation_df["player_nb"],
        text=nation_df["name"],
        colorscale=["rgb(214,214,255)", 'rgb(0,2,113)'],
        autocolorscale=False,
        reversescale=False,
        marker_line_color='darkgray',
        marker_line_width=0.5,
        colorbar_title='Number of players',
    ))

    fig.update_layout(
        title_text='Number of football players in top 5 leagues by country',
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
        ),
    )

    return fig


layout = html.Div(children=[
    html.Div([dash.html.H2(children='Dashboard')], style={"flex": "0 1 auto"}, className="heading"),
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Span("Y : "),
                    dcc.Dropdown(
                        columns,
                        "stats.Assists_per90",
                        id="dropdown-y",
                        style={"border": "solid 0px", "width": "200px"}
                    ),
                ], style={"display": "flex", "align-items": "center"}),
                html.Div([
                    html.Span("X : "),
                    dcc.Dropdown(
                        columns,
                        "stats.Goals_per90",
                        id="dropdown-x",
                        style={"border": "solid 0px", "width": "200px"}
                    ),
                ], style={"display": "flex", "align-items": "center"}),
            ], style={"display": "flex", "gap": "40px", "margin-bottom": "30px"}),

            html.Div([
                dcc.Graph(figure=build_scatter_plot("stats.Goals_per90", "stats.Assists_per90"), config={
                    "displaylogo": False,
                    'displayModeBar': False,
                }),
            ], id="scatter-ctn")
        ], className="dash_block", style={"flex-direction": "column", }),
        html.Div([
            dcc.Graph(figure=build_map(), config={
                "displaylogo": False,
                'displayModeBar': False,
            }),
        ], className="dash_block"),

        html.Div([
            html.Div([
                html.Div([
                    html.Span("Metric : "),
                    dcc.Dropdown(
                        columns,
                        "stats.Assists_per90",
                        id="dropdown-metric",
                        style={"border": "solid 0px", "width": "200px"}
                    ),
                ], style={"display": "flex", "align-items": "center"}),
            ], style={"display": "flex", "gap": "40px", "margin-bottom": "30px"}),

            html.Div([
                dcc.Graph(figure=build_histogram("stats.Goals_per90"), config={
                    "displaylogo": False,
                    'displayModeBar': False,
                }),
            ], id="histo-ctn")
        ], className="dash_block", style={"flex-direction": "column", }),
    ], style={"padding": "20px", "flex": "1 1 auto", "display": "flex", "gap": "20px", "overflow-y": "scroll"},
        className="graph_holder")
], style={"height": "calc(100vh - 4rem)", "display": "flex", "flex-direction": "column"})


@dash.callback(
    Output("scatter-ctn", "children"),
    Input("dropdown-x", "value"),
    Input("dropdown-y", "value"),
    State("dropdown-x", "value"),
    State("dropdown-y", "value"),
    prevent_initial_call=True)
def change_scatter_plot_axis(new_value_x, new_value_y, current_value_x, current_value_y):
    return dcc.Graph(figure=build_scatter_plot(current_value_x, current_value_y), config={
        "displaylogo": False,
        'displayModeBar': False,
    })


@dash.callback(
    Output("histo-ctn", "children"),
    Input("dropdown-metric", "value"),
    prevent_initial_call=True
)
def change_histogram_axis(new_value):
    return dcc.Graph(figure=build_histogram(new_value), config={
        "displaylogo": False,
        'displayModeBar': False,
    })
