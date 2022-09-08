from flask import Blueprint, render_template

# Blueprints specifies that this files contains url routes
views = Blueprint('views', __name__)

@views.route('/')
def home():
    print('hello')
    return render_template("home.html")



