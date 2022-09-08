from flask import Flask, g 
from .db_man import Arena_DB_Manager
import sys

def create_app():
    app = Flask(__name__)

    # Define secret key to ensure that signed cookies are not tampered with
    app.config['SECRET_KEY'] = 'aKMBk3GQILmWrTFY6fJNeA'

    # To close the database connection when the app closes
    @app.teardown_appcontext
    def close_connection(exception):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

    from .views import views 
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Initialise a database manager object
    db_path = 'website/databases/arena.db'
    dbm = Arena_DB_Manager(db_path)

    
    if sys.argv[-1] == 'reset':
        # If the CL arg 'reset' is passed, the databases will be reset
        dbm.init_arena_db(reset=True)

    else:
        # Otherwise, just initialise it normally
        dbm.init_arena_db()

    return app
