"""Dashboard main app"""
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd

FILE_NAME = '/home/edgar/Desktop/Projects/Garmin_test/garmin/hb_logs/6c8b2c15-540f-4214-b93b-993ab5b660aa_2020_09_03_.csv'
DF_GARMIN = pd.read_csv(FILE_NAME, index_col=0).tail(300)


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
                html.Img(src="./assets/stock-icon.png")  
            ], 
            className="banner"
        ),
        html.Div(
            [
                html.H3("Heart Rate"), 
                dcc.Graph(
                    id='graph_close',
                    figure={
                        "data": [trace_heart_rate],
                        "layout": {
                            "title": "Heart Rate"
                        }
                    }
                )
            
            ],
            className="five columns",
        ),
        html.Div(
            [   
                html.H3("Distance"),
                dcc.Graph(
                    id='graph_speed',
                    figure={
                        "data": [trace_distance],
                        "layout": {
                            "title": "Distance"
                        }
                    }
                )
            ],
            className="five columns",
        )
    ],
    className="column"
)

if __name__ == "__main__":
    APP.run_server(debug=True)

