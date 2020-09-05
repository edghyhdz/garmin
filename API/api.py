from flask import Flask, request, jsonify, make_response
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


e = create_engine("sqlite:////home/edgar/Desktop/Projects/Garmin_test/garmin/garmin_db.db")

app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////home/edgar/Desktop/Projects/Garmin_test/garmin/garmin_db.db"

db = SQLAlchemy(app)


# TODO:
# GET DB Functions into garmin class                                [X]
# Check if a event is currently ongoing                             [X]
# Update event when finished                                        [X]
# Save path of csv and json to be queried later on (?)              [X]
# Start email fetcher by request                                    [X]
# Stop script by API request                                        [ ]
# Stop event based on session id? return it with request            [ ]
# How to pass it into the main script as args?                      [ ]
# How to let request run script and let it running outside 
# of the shell, to not block other scripts inside API               [ ]

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)


class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    starting_date = db.Column(db.DateTime)
    finished_date = db.Column(db.DateTime)
    ongoing_event = db.Column(db.Boolean)
    data_path = db.Column(db.String(50))
    user_id = db.Column(db.Integer)
    session_id = db.Column(db.String(50))
    event_type = db.Column(db.Integer)


def token_required(f): 
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "x-access-token" in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': "Token is invalid"}), 401
        
        return f(current_user, *args, **kwargs)

    return decorated

@app.route("/api/start", methods=['POST'])
@token_required
def start_event(current_user): 
    """[summary]

    Args:
        current_user ([type]): [description]

    Returns:
        [type]: [description]
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

@app.route("/api/stop_event", methods=['POST'])
@token_required
def stop_event(current_user): 
    """[summary]

    Args:
        current_user ([type]): [description]

    Returns:
        [type]: [description]
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
        print("OUTPUT: ", check_output)
        if 'ps ax' not in check_output:
            pid = subprocess.getoutput(["ps ax | grep main.py | grep python | grep -P -o -e  '[0-9]+' | head -1"])
        else:
            return jsonify({'message': 'No event to terminate'})
        # Kill process from retrieved PID
        subprocess.getoutput(['kill -15 {}'.format(pid)])
        # If process was killed succesfully DB should be updated with ongoing_event=False for corresponding event
        logging.info("Stoping event")
        return jsonify({'message': 'Stoping event at: {}'.format(datetime.now())})


@app.route("/user", methods=['GET'])
@token_required
def get_all_users(current_user):
    """[summary]

    Returns:
        [type]: [description]
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
    
@app.route("/user/<public_id>", methods=['GET'])
@token_required
def get_one_user(current_user, public_id):
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

@app.route('/user', methods=['POST'])
@token_required
def create_user(current_user):
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method="sha256")

    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'New user created!'})

@app.route("/user/<public_id>", methods=['PUT'])
@token_required
def promote_user(current_user, public_id):

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': "No user found!"})

    user.admin = True
    db.session.commit()
    
    return jsonify({"message": "user has been promoted"})

@app.route("/users/<public_id>", methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': "No user found!"})
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': "user has been deleted"})

@app.route("/login", methods=['GET'])
def login():
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
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.utcnow() + timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response("Could not verify", 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

if __name__ == "__main__":
    app.run(debug=True)