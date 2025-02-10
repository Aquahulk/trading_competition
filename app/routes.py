from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask import Blueprint
from app import db
from app.models import User, Tournament, Order
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from app.forms import LoginForm 

# Create Blueprints for different route groups
main_routes = Blueprint('main', __name__)
auth_routes = Blueprint('auth', __name__)
tournament_routes = Blueprint('tournament', __name__)
profile_routes = Blueprint('profile', __name__)
chat_routes = Blueprint('chat', __name__)
admin_routes = Blueprint('admin', __name__)

# --------------------- HOME ROUTE ---------------------
@main_routes.route('/')
def home():
    return render_template('index.html')

# --------------------- USER REGISTRATION ---------------------
@auth_routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))
        
        new_user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

# --------------------- USER LOGIN ---------------------
@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # ✅ Create a form instance

    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()  # ✅ Correct
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)  # ✅ Pass 'form' to templat
# --------------------- USER LOGOUT ---------------------
@auth_routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

# --------------------- USER DASHBOARD ---------------------
@main_routes.route('/dashboard')
@login_required
def dashboard():
    # Fetch user's account details (Modify based on your database schema)
    account = current_user.account if hasattr(current_user, 'account') else None

    return render_template('dashboard.html', user=current_user, account=account)  # ✅ Correct indentation


# --------------------- TOURNAMENT PAGE ---------------------
@tournament_routes.route('/tournament')
@login_required
def tournament():
    tournament = Tournament.query.all()
    return render_template('tournament.html', tournament=tournament)

# --------------------- 8% DAILY DRAWDOWN RULE ---------------------
def check_drawdown(user):
    today = datetime.utcnow().date()
    orders = Order.query.filter_by(user_id=user.id).filter(Order.date >= today).all()

    if not orders:
        return False  # No trades today

    start_balance = user.starting_balance
    current_balance = start_balance

    for order in orders:
        current_balance += order.profit_or_loss()

    drawdown = ((start_balance - current_balance) / start_balance) * 100

    if drawdown >= 8:  # 8% drawdown exceeded
        user.suspended = True
        db.session.commit()
        return True

    return False

# --------------------- ORDER PLACEMENT ---------------------
@main_routes.route('/place_order', methods=['POST'])
@login_required
def place_order():
    if current_user.suspended:
        return jsonify({'error': 'You have exceeded the 8% daily drawdown and are suspended for the day'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data received'}), 400
    
    required_fields = ['symbol', 'order_type', 'quantity', 'price']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    new_order = Order(
        user_id=current_user.id,
        symbol=data['symbol'],
        order_type=data['order_type'],
        quantity=data['quantity'],
        price=data['price'],
        date=datetime.utcnow()
    )

    db.session.add(new_order)
    db.session.commit()

    # Check if drawdown rule is violated
    if check_drawdown(current_user):
        return jsonify({'message': 'Order placed, but you have been suspended due to 8% drawdown'}), 403

    return jsonify({'message': 'Order placed successfully'}), 201

# --------------------- VIEW ORDER HISTORY ---------------------
@main_routes.route('/order_history')
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('order_history.html', orders=orders)

# --------------------- ADMIN: VIEW ALL USERS ---------------------
@admin_routes.route('/admin/users')
@login_required
def view_users():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    users = User.query.all()
    return render_template('users.html', users=users)

@profile_routes.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@chat_routes.route('/chat')
def chat():
    return render_template('chat.html')