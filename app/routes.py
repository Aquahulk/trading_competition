from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from app.services.alpaca_service import AlpacaService
from app.models import User, Tournament, Trade
from app.forms import RegistrationForm, LoginForm, TournamentForm, TradeForm
from app import db
from dotenv import load_dotenv

load_dotenv()

# Define Blueprints
main_routes = Blueprint('main', __name__)
auth_routes = Blueprint('auth', __name__)
tournament_routes = Blueprint('tournament', __name__)
profile_routes = Blueprint('profile', __name__)
chat_routes = Blueprint('chat', __name__)
admin_routes = Blueprint('admin', __name__)

# Main Routes
@main_routes.route('/')
def home():
    return render_template('index.html')

@main_routes.route('/dashboard')
@login_required
def dashboard():
    alpaca = AlpacaService()
    account = alpaca.get_account()
    positions = alpaca.get_positions()
    orders = alpaca.get_orders()
    portfolio_history = alpaca.get_portfolio_history()

    return render_template('dashboard.html', account=account, positions=positions, orders=orders, portfolio_history=portfolio_history)

# Auth Routes
@auth_routes.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)  # No bcrypt hashing
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:  # No bcrypt checking
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

@auth_routes.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

# Tournament Routes
@tournament_routes.route('/tournaments')
@login_required
def tournaments():
    tournaments = Tournament.query.all()
    return render_template('tournament.html', tournaments=tournaments)

@tournament_routes.route('/join_tournament/<int:tournament_id>', methods=['POST'])
@login_required
def join_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    current_user.tournaments.append(tournament)
    db.session.commit()
    flash('You have joined the tournament!', 'success')
    return redirect(url_for('tournament.tournaments'))

# Profile Routes
@profile_routes.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

# Chat Routes
@chat_routes.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

# Admin Routes
@admin_routes.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    return render_template('admin.html')
