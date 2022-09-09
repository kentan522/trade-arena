from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from .db_man import Arena_DB_Manager

# Blueprints specifies that this files contains url routes
views = Blueprint('views', __name__)

# Initialise a database manager object
db_path = 'website/databases/arena.db'
dbm = Arena_DB_Manager(db_path)
dbm.init_arena_db()

@views.route('/')
def home():

    if not session.get('name'):
        return render_template("home.html", logged_in=False)

    return render_template("home.html", logged_in=True)

@views.route('/user_home', methods=['GET', 'POST'])
def user_home():

    username = session.get('name')

    # Load current watchlist
    coin_names, coin_prices = dbm.get_coin_watchlist_data(username)

    if request.method == 'POST':
        coin_name = request.form.get('coin_name')
        coin_is_added = dbm.add_coin_data(username, coin_name)

        if coin_is_added:
            flash('Coin successfully added to your watchlist!', category='success')

            # Return coin list and updated coin prices
            coin_names, coin_prices = dbm.get_coin_watchlist_data(username)

        else:
            flash(f'Coin by the name {coin_name} was not found!', category='error')

    if not session.get('name'):
        return redirect(url_for('views.home'))

    return render_template("user_home.html", logged_in=True, username=session.get('name'), coin_names=coin_names, coin_prices=coin_prices, col_length=len(coin_prices))