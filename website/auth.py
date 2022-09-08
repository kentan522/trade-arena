from flask import Blueprint, render_template, request, flash

# Blueprints specifies that this files contains url routes
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    data = request.form # 'data' contains the data that was sent as part of the form 
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
            flash('Account created!', category='success')
        
    return render_template("signup.html")


