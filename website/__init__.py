from flask import Flask, g 
import sqlite3
from .init_db import create_user_db, create_watch_db

def create_app():
    app = Flask(__name__)

    # Define secret key to ensure that signed cookies are not tampered with
    app.config['SECRET_KEY'] = 'aKMBk3GQILmWrTFY6fJNeA' 

    def get_db():
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(DATABASE)
        return db

    @app.teardown_appcontext
    def close_connection(exception):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app

