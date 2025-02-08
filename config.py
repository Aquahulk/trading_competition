import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'q4asd3d33r3d3ed'
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:monusinghamit10@localhost/trading_competition"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALPACA_API_KEY = os.environ.get('ALPACA_API_KEY') or 'PKQ5BKJB3EF7BZGSXOAS'
    ALPACA_SECRET_KEY = os.environ.get('ALPACA_SECRET_KEY') or 'aG0Zs8mfn3QLsuK7AOaiqw4Rd0To0q4udTMR5lmb'
    ALPACA_PAPER_TRADING = True  # Use paper trading environment