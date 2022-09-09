from flask import Blueprint, render_template, redirect, url_for, session

# Blueprints specifies that this files contains url routes
views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html", logged_in=False)

@views.route('/user_home')
def user_home():

    if not session.get('name'):
        return redirect(url_for('views.home'))

    return render_template("user_home.html", logged_in=True)