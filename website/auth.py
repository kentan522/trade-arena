from flask import Blueprint, render_template, request, flash
from .db_man import Arena_DB_Manager

# Blueprints specifies that this files contains url routes
auth = Blueprint('auth', __name__)

# Initialise a database manager object
db_path = 'website/databases/arena.db'
dbm = Arena_DB_Manager(db_path)
dbm.init_arena_db()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")

@auth.route('/logout')
def logout():
    return render_template("logout.html")

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        # Obtain sign-up data from the form
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Some constraints for checking for the validity of the email/username/password
        if len(username) < 3:
            flash('Username must be more than 2 characters!', category='error')

        elif password1 != password2:
            flash('Password do not match!', category='error')

        elif len(password1) < 7:
            flash('Password must be at least 7 characters long!.', category='error')

        else:
            flash('Account successfully created!', category='success')

            # Package data, allow the db manager to add it to the database
            user_data = (username, email, password1)
            dbm.add_user_credentials(user_data)

    return render_template("signup.html")


