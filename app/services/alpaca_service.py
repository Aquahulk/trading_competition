from flask import current_app
import os
import alpaca_trade_api as tradeapi

class AlpacaService:
    def __init__(self):
        # Get API keys from environment variables
        self.api_key = os.getenv("ALPACA_API_KEY")
        self.api_secret = os.getenv("ALPACA_API_SECRET")
        self.base_url = "https://paper-api.alpaca.markets"  # Paper Trading URL

        # Debugging
        print("Alpaca API Key:", self.api_key)
        print("Alpaca Secret Key:", self.api_secret)

        # Initialize Alpaca REST API
        self.api = tradeapi.REST(
            self.api_key,
            self.api_secret,
            base_url=self.base_url
        )

    def get_account(self):
        """Fetch account details (balance, equity, etc.)"""
        account = self.api.get_account()
        
        # Convert values to float
        initial_equity = float(account.last_equity)  # Equity at start of the day
        current_equity = float(account.equity)  # Current equity
        cash_balance = float(account.cash)  # Cash balance

        # Calculate P&L
        pnl = current_equity - initial_equity
        pnl_percentage = (pnl / initial_equity) * 100  # Profit/Loss in %

        # Check for daily drawdown disqualification
        drawdown_limit = 0.92 * initial_equity  # 8% loss limit
        disqualified = current_equity < drawdown_limit

        return {
            "initial_equity": initial_equity,
            "current_equity": current_equity,
            "cash_balance": cash_balance,
            "profit_loss": pnl,
            "profit_loss_percentage": pnl_percentage,
            "daily_drawdown_limit": drawdown_limit,
            "disqualified": disqualified
        }

    def get_positions(self):
        """Fetch current positions"""
        return self.api.list_positions()

    def get_orders(self):
        """Fetch all orders"""
        return self.api.list_orders()

    def get_portfolio_history(self):
        """Fetch portfolio history"""
        return self.api.get_portfolio_history()
