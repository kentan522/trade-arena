from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .db_man import Arena_DB_Manager

# Blueprints specifies that this files contains url routes
auth = Blueprint('auth', __name__)

# Initialise a database manager object
db_path = 'website/databases/arena.db'
dbm = Arena_DB_Manager(db_path)
dbm.init_arena_db()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        login_successful = dbm.check_login_credentials((username, password))

        if login_successful:
            flash('Login successful! Welcome to your homepage', category='success')

            # Store the login in a session
            session['name'] = username

            # Redirect to the user hoempage
            return redirect(url_for('views.user_home'))

        else:
            flash('Login insuccessful! Please check your login credentials!', category='error')

    return render_template("login.html", logged_in=False)

@auth.route('/logout')
def logout():
    # Redirect to the logout page and clear user session
    session['name'] = None
    return render_template("logout.html", logged_in=False)

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        # Obtain sign-up data from the form
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')


        # Some constraints for checking for the validity of the email/username/password
        if dbm.check_exists_credentials(username, email):
            flash('Username or email already exists! Please choose another!', category='error')

        elif len(username) < 3:
            flash('Username must be more than 2 characters!', category='error')

        elif password1 != password2:
            flash('Password do not match!', category='error')

        elif len(password1) < 7:
            flash('Password must be at least 7 characters long!.', category='error')

        else:
            flash('Account successfully created!', category='success')

            # Package data, allow the db manager to add it to the database
            register_data = [username, email, password1]
            dbm.add_user_credentials(register_data)
            return redirect(url_for('auth.login'))

    return render_template("signup.html", logged_in=False)


