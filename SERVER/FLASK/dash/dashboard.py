
import os
from datetime import datetime, timedelta
from dash import Dash
import dash_html_components as html
import dash
import dash_core_components as dcc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import pandas as pd


FILE_NAME = '/home/edgar/Desktop/Projects/Garmin_test/garmin/hb_logs/8e7b382d-3271-4f2a-a38f-a31b17f592c7_2020_09_10_.csv'
DF_GARMIN = pd.read_csv(FILE_NAME, index_col=0).tail(300)

GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 10000)

APP_COLOR = {"graph_bg": "#1f1f1f", "graph_line": "#007ACE"}

# Initiate df_garmin dataframe
PATH = '/home/edgar/Desktop/Projects/Garmin_test/garmin/hb_logs/8e7b382d-3271-4f2a-a38f-a31b17f592c7_2020_09_10_.csv'
DF_GARMIN = pd.read_csv(PATH, index_col=0)


def init_dashboard(server):
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[
            '/static/dist/css/stylessheet.css',
            'https://fonts.googleapis.com/css?family=Lato'
        ]
    )

    dash_app.layout = html.Div(
        [
            html.Div(
                [
                    html.H2("Garmin Health Data"),
                    html.Img(src="./static/img/stock-icon.png"),
                ], 
                className="banner"
            ),
            
            html.Div(
                [
                    # html.Embed(src="./static/html/test.html"),
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
                                figure=dict(
                                    layout=dict(
                                        plot_bgcolor=APP_COLOR["graph_bg"],
                                        paper_bgcolor=APP_COLOR["graph_bg"],
                                    )
                                )
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
    init_callbacks(dash_app)
    
    return dash_app.server

def init_callbacks(dash_app):

    @dash_app.callback(
    Output("graph_heart_bit", "figure"), [Input("heart-bit-update", "n_intervals")],
    )
    def gen_heart_rate_graph(value):
        """
        Generate the heart rate graph.

        :params interval: update the graph based on an interval
        """
        global DF_GARMIN
        DF_GARMIN = pd.read_csv(PATH, index_col=0)
        print('UPDATING!!!!!')

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


    @dash_app.callback(
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