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

from flask import Flask, request, jsonify, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
import uuid
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from json import dumps
from functools import wraps
import os
import logging
import subprocess
from time import sleep
import pandas as pd



FILE_NAME = '/home/edgar/Desktop/Projects/Garmin_test/garmin/hb_logs/8e893ff5-45fa-4e73-bc55-6681b2e366c8_2020_09_09_.csv'
DF_GARMIN = pd.read_csv(FILE_NAME, index_col=0).tail(300)

GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 5000)

APP_COLOR = {"graph_bg": "#1f1f1f", "graph_line": "#007ACE"}

# Initiate df_garmin dataframe
PATH = '/home/edgar/Desktop/Projects/Garmin_test/garmin/hb_logs/8e893ff5-45fa-4e73-bc55-6681b2e366c8_2020_09_09_.csv'
DF_GARMIN = pd.read_csv(PATH, index_col=0)


e = create_engine("sqlite:////home/edgar/Desktop/Projects/Garmin_test/garmin/garmin_db.db")

server = Flask(__name__)
APP = dash.Dash(__name__, server=server, url_base_pathname='/test/')

# APP = dash.Dash(__name__, server=server, url_base_pathname='/path_name/')

server.config['SECRET_KEY'] = 'thisissecret'
server.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////home/edgar/Desktop/Projects/Garmin_test/garmin/garmin_db.db"

db = SQLAlchemy(server)


# TODO:
# Add filtering based on dates      [ ]

class User(db.Model):
    """User db table"""
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)


class Events(db.Model):
    """Events db table"""
    id = db.Column(db.Integer, primary_key=True)
    starting_date = db.Column(db.DateTime)
    finished_date = db.Column(db.DateTime)
    ongoing_event = db.Column(db.Boolean)
    data_path = db.Column(db.String(50))
    user_id = db.Column(db.Integer)
    session_id = db.Column(db.String(50))
    event_type = db.Column(db.Integer)


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

def token_required(f): 
    @wraps(f)
    def decorated(*args, **kwargs):
        """
        Makes function require token to authenticae
        """
        token = None

        if "x-access-token" in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try: 
            data = jwt.decode(token, server.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': "Token is invalid"}), 401
        
        return f(current_user, *args, **kwargs)

    return decorated

@server.route("/dash")
def render_dashboard():
    return APP.index()
    # return redirect('/test/')

@server.route("/api/start", methods=['POST'])
@token_required
def start_event(current_user): 
    """Starts logging event data

    Args:
        current_user (str): current user id, used to find details in db

    Returns:
        json: Message json, whether transaction was successful or not
    """
    if not current_user.admin:
        return jsonify({'message': "You have no authorization to start an event"})
    
    payload = None

    data = request.get_json()
    if 'payload' in data.keys():
        payload = data.get('payload')

    if not payload:
        return jsonify({'message': "Incorrect data provided"})
    
    if not 'activity' in data.keys():
        return jsonify({'message': "Incorrect data provided"})

    activity = data.get('activity')

    if 'start_race' in payload:
        text = open('/home/edgar/Desktop/Projects/Garmin_test/listener', 'w')
        text.write('{}'.format(activity))
        logging.info("Starting event")

        return jsonify({'message': 'Starting event at: {}'.format(datetime.now())})


@server.route("/api/stop_event", methods=['POST'])
@token_required
def stop_event(current_user): 
    """Stops current event

    Args:
        current_user (str): current user id, used to find details in db]
        
    Returns:
        json: Message, whether transaction was successful or not
    """
    if not current_user.admin:
        return jsonify({'message': "You have no authorization to start an event"})
    
    payload = None

    data = request.get_json()
    if 'payload' in data.keys():
        payload = data.get('payload')

    if not payload:
        return jsonify({'message': "Incorrect data provided"})

    if 'stop_event' in payload:
        text = open('/home/edgar/Desktop/Projects/Garmin_test/listener', 'w')

        # Listener script uses ok to continue looping forever
        text.write('ok')
        check_output = subprocess.getoutput(["ps ax | grep -m1 main.py | grep python"])

        if 'ps ax' not in check_output:
            pid = subprocess.getoutput(["ps ax | grep main.py | grep python | grep -P -o -e  '[0-9]+' | head -1"])
        else:
            return jsonify({'message': 'No event to terminate'})
        # Kill process from retrieved PID
        subprocess.getoutput(['kill -15 {}'.format(pid)])
        # If process was killed succesfully DB should be updated with ongoing_event=False for corresponding event
        logging.info("Stoping event")
        return jsonify({'message': 'Stoping event at: {}'.format(datetime.now())})

@server.route("/api/list_events", methods=['GET'])
@token_required
def get_all_events(current_user):
    """Get all events from db

    Args:
        current_user (str): current logged user

    Returns:
        json: all events in json format
    """
    events = Events.query.all()
    temp_dict = {}
    for event in events:
        event_id = event.id

        event_dict = event.__dict__.copy()

        # Remove isinstance and data_path dict key
        event_dict.pop('_sa_instance_state')
        event_dict.pop('data_path')

        temp_dict[event_id] = event_dict
    
    return jsonify({'events': temp_dict})

@server.route("/api/event/<session_id>", methods=['GET'])
@token_required
def get_event(current_user, session_id):
    """Get specific event time series

    Args:
        current_user (str): Current logged user
        session_id (str): Event to search for with given session id

    Returns:
        json: Data time series from given session_id event
    """
    event = Events.query.filter_by(session_id=session_id).first()

    if not event:
        return jsonify({'message': "No event found!"})
    
    # Get file path from db
    file_path = event.data_path
    event_df = pd.read_csv(file_path, index_col=0)

    # Jsonify that mofo
    event_dict = eval(event_df.T.to_json())

    return jsonify({'data': event_dict})

@server.route("/user", methods=['GET'])
@token_required
def get_all_users(current_user):
    """Queries all users from db

    Returns:
        json: all users
    """
    users = User.query.all()
    output = []

    for user in users:
        user_data = {}
        user_data['public_id'] =user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)

    return jsonify({'users': output})
    
@server.route("/user/<public_id>", methods=['GET'])
@token_required
def get_one_user(current_user, public_id):
    """Queries single user

    Args:
        current_user (str): current logged in user
        public_id (str): public id of user to be used to 
        search for user data

    Returns:
        json: returns user data
    """

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': "No user found!"})
    
        output = []

    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin

    return jsonify({'user': user_data})

@server.route('/user', methods=['POST'])
@token_required
def create_user(current_user):
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method="sha256")

    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'New user created!'})

@server.route("/user/<public_id>", methods=['PUT'])
@token_required
def promote_user(current_user, public_id):

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': "No user found!"})

    user.admin = True
    db.session.commit()
    
    return jsonify({"message": "user has been promoted"})

@server.route("/users/<public_id>", methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': "No user found!"})
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': "user has been deleted"})

@server.route("/login", methods=['GET'])
def login():
    """Logs user in, and generates authentication token valid for 30 min

    Returns:
        json: Message, whether transaction was successfull or not
    """
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response("Could not verify", 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(name=auth.username).first()
    is_admin = user.admin

    if not is_admin:
        return make_response("You have no authorization to request a token", 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if not user: 
        return make_response("Could not find user", 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password) and is_admin: 
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.utcnow() + timedelta(minutes=30)}, server.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response("Could not verify", 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

if __name__ == "__main__":
    server.run(debug=True)