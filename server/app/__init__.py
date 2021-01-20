from flask import Flask
from flask_socketio import SocketIO, join_room, leave_room
from flask_cors import CORS

app = Flask(__name__)
socketio = SocketIO(app)

cors = CORS(app)

ACTIVE_USERS = {}

if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")
elif app.config["ENV"] == "development":
    app.config.from_object("config.DevelopmentConfig")
elif app.config["ENV"] == "testing":
    app.config.from_object("config.TestingConfig")


from app import sockets_io
from app import student_views
from app import teacher_views
from app import public_views