from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from json import dumps


e = create_engine("sqlite:////home/edgar/Desktop/Projects/Garmin_test/garmin/garmin.db")

app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////home/edgar/Desktop/Projects/Garmin_test/garmin/garmin.db"

db = SQLAlchemy(app)


# TODO:
# GET DB Functions into garmin class                                [ ]
# Check if a event is currently ongoing                             [ ]
# Update event when finished                                        [ ]
# Save path of csv and json to be queried later on (?)              [ ]
# Start email fetcher by request                                    [ ]
# Stop script by request                                            [ ]

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    starting_date = db.Column(db.DateTime)
    finished_date = db.Column(db.DateTime)
    ongoing_event = db.Column(db.Boolean)
    data_path = db.Column(db.String(50))
    user_id = db.Column(db.Integer)

@app.route("/user", methods=['GET'])
def get_all_users():
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
def get_one_user(public_id):
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
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method="sha256")

    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'New user created!'})

@app.route("/user/<public_id>", methods=['PUT'])
def promote_user(public_id):
    return ""

@app.route("/users/<public_id>", methods=['DELETE'])
def delete_user(public_id):
    return ""

if __name__ == "__main__":
    app.run(debug=True)