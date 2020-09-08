"""Dashboard main app"""

import os
from datetime import datetime, timedelta
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd


FILE_NAME = '/home/edgar/Desktop/Projects/Garmin_test/garmin/hb_logs/6c8b2c15-540f-4214-b93b-993ab5b660aa_2020_09_03_.csv'
DF_GARMIN = pd.read_csv(FILE_NAME, index_col=0).tail(300)

GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 5000)

APP_COLOR = {"graph_bg": "#1f1f1f", "graph_line": "#007ACE"}

# Initiate df_garmin dataframe
PATH = '/home/edgar/Desktop/Projects/Garmin_test/garmin/hb_logs/c3fc108a-adbc-4807-ba65-1bccc0672cea_2020_09_08_.csv'
DF_GARMIN = pd.read_csv(PATH, index_col=0)


trace_heart_rate = go.Scatter(
    x=list(DF_GARMIN['date']),
    y=list(DF_GARMIN['hb']),
    name='Heart Rate',
    line=dict(color="#f44242")
)

trace_distance = go.Scatter(
    x=list(DF_GARMIN['date']),
    y=list(DF_GARMIN['distance']),
    name='Distance',
    line=dict(color="#f44242")
)

APP = dash.Dash(
    __name__,
    external_stylesheets=[
        'https://codepen.io/chriddyp/pen/bWLwgP.css'
    ]
)

APP.layout = html.Div(
    [
        html.Div(
            [
                html.H2("Garmin Health Data"),
                html.Img(src="./assets/stock-icon.png"),
            ], 
            className="banner"
        ),
        html.Div(
            [
                html.H2("Test box"),
            ],
            className='box'
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H3("Heart Rate"), 
                        dcc.Graph(
                            id="graph_heart_bit",
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=APP_COLOR["graph_bg"],
                                    paper_bgcolor=APP_COLOR["graph_bg"],
                                )
                            ),
                        )
                    ],
                    className="graph_left",
                ),
        html.Div(
                    [   
                        html.H3("Distance"),
                        dcc.Graph(
                            id='graph_distance',
                            figure={
                                "data": [trace_distance],
                                "layout": {
                                    "title": "Distance"
                                }
                            }
                        )
                    ],
                    className="graph_right",
        )
            ],
            className="graph_container"
        ), 
        dcc.Interval(
            id="heart-bit-update",
            interval=int(GRAPH_INTERVAL),
            n_intervals=0,
        ),
    ],
    className="row"
)

@APP.callback(
    Output("graph_heart_bit", "figure"), [Input("heart-bit-update", "n_intervals")],
)
def gen_heart_rate_graph(value):
    """
    Generate the heart rate graph.

    :params interval: update the graph based on an interval
    """
    global DF_GARMIN
    DF_GARMIN = pd.read_csv(PATH, index_col=0)

    if len(DF_GARMIN) > 100:
        DF_GARMIN = DF_GARMIN.tail(300)
    else:
        DF_GARMIN = DF_GARMIN

    trace = [dict(
        type="scatter",
        y=DF_GARMIN['hb'],
        x=DF_GARMIN["date"],
        line={"color": "#f44242"},
        name="TEST_GRAPH",
        hovermode="closest",
        mode="lines",
        )
    ]

    layout = dict(
        plot_bgcolor="#333333",
        paper_bgcolor="#3d3d3d",
        font={"color": "#fff"},
        xaxis={
            "showline": True,
            "showline": True,
            "showgrid": True,
            "gridcolor": "#D3D3D3",
            "zeroline": False,
            "title": "Measurement Timestamp",
        },
        yaxis={
            "showgrid": True,
            "gridcolor": "#D3D3D3",
        }
        
            )

    return dict(data=trace, layout=layout)

@APP.callback(
    Output("graph_distance", "figure"), [Input("heart-bit-update", "n_intervals")],
)
def gen_distance_graph(value):
    """
    Generate the heart rate graph.

    :params interval: update the graph based on an interval
    """
    global DF_GARMIN
    DF_GARMIN = pd.read_csv(PATH, index_col=0)

    if len(DF_GARMIN) > 100:
        df_distance = DF_GARMIN.tail(300)
    else:
        df_distance = DF_GARMIN

    trace = [dict(
        type="scatter",
        y=df_distance['distance'],
        x=DF_GARMIN["date"],
        line={"color": "#f44242"},
        name="TEST_GRAPH",
        hovermode="closest",
        mode="lines",
        )
    ]

    layout = dict(
        plot_bgcolor="#333333",
        paper_bgcolor="#3d3d3d",
        font={"color": "#fff"},
        xaxis={
            "showline": True,
            "showline": True,
            "showgrid": True,
            "gridcolor": "#D3D3D3",
            "zeroline": False,
            "title": "Measurement Timestamp",
        },
        yaxis={
            "showgrid": True,
            "gridcolor": "#D3D3D3",
        }
        
            )

    return dict(data=trace, layout=layout)



if __name__ == "__main__":
    APP.run_server(debug=True)