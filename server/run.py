from app import app, socketio, CORS

cors = CORS(app)

if __name__ == "__main__":
    socketio.run(app)