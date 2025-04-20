# Sets up the Flask application and SocketIO for real-time updates.
from flask import Flask
from flask_socketio import SocketIO

socketio= SocketIO()

#new flask app instance
def create_app():
    #flask object
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'sfgreg@343324#@EEC' 

    from app.routes import bp
    app.register_blueprint(bp)

    socketio.init_app(app)
    return app