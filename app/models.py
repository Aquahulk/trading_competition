from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)  # ✅ Secure hashed password
    avatar = db.Column(db.String(20), nullable=False, default='default.jpg')
    bio = db.Column(db.Text, nullable=True)
    suspended = db.Column(db.Boolean, default=False)
    # ✅ Relationships
    tournaments = db.relationship('Tournament', secondary='user_tournament', back_populates='participants')
    trades = db.relationship('Trade', backref='trader', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)  # ✅ Added Order relationship

    # ✅ Profit/Loss Tracking
    total_equity = db.Column(db.Float, default=10000.0)  # Starting balance
    daily_drawdown = db.Column(db.Float, default=0.0)
    last_trade_date = db.Column(db.Date, default=date.today)
    is_suspended = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def calculate_profit_loss_percentage(self):
        """Calculate realized P/L based on total equity."""
        initial_equity = 10000.0
        profit_loss = self.total_equity - initial_equity
        return (profit_loss / initial_equity) * 100

    def check_drawdown(self):
        """Enforce 8% daily drawdown limit."""
        if self.daily_drawdown <= -8.0:
            self.is_suspended = True
        db.session.commit()

class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    entry_fee = db.Column(db.Float, nullable=False, default=0.0)
    prize_pool = db.Column(db.Float, nullable=False, default=0.0)

    # ✅ Many-to-Many Relationship (Users <-> Tournaments)
    participants = db.relationship('User', secondary='user_tournament', back_populates='tournaments')

# ✅ Many-to-Many Table (Users <-> Tournaments)
user_tournament = db.Table('user_tournament',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('tournament_id', db.Integer, db.ForeignKey('tournament.id'), primary_key=True)
)

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_open = db.Column(db.Boolean, default=True)

    def calculate_unrealized_pnl(self, current_price):
        """Calculate P/L percentage for open trades."""
        price_change = (current_price - self.price) / self.price
        return price_change * 100

# ✅ FIX: Added the `Order` Model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    order_type = db.Column(db.String(10), nullable=False)  # "buy" or "sell"
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def profit_or_loss(self):
        """Calculate profit/loss for completed orders."""
        return self.quantity * self.price  # Simplified for example
