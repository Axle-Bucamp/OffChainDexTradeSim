import json
import redis
import requests

# Initialize Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
KRAKEN_API_URL = "https://api.kraken.com/0/public/Ticker"

class TradingModule:
    """ 
    A trading module that interacts with the Kraken API to fetch prices, buy, and sell assets.
    It maintains balance and holdings, storing data persistently in Redis.
    """
    def __init__(self, initial_balance, trading_fee=0.001):
        """
        Initializes the trading module.
        
        :param initial_balance: Initial balance in USDC.
        :param trading_fee: Trading fee as a fraction (default: 0.001).
        """
        self.balance = initial_balance  # Stored in USDC
        self.trading_fee = trading_fee
        self.holdings = {}  # Dictionary to track holdings per ticker
        self.load_from_redis()

    def save_to_redis(self):
        """Saves the current trading data to Redis."""
        data = {
            "balance": self.balance,
            "holdings": self.holdings
        }
        redis_client.set("trading_data", json.dumps(data))

    def load_from_redis(self):
        """Loads trading data from Redis."""
        data = redis_client.get("trading_data")
        if data:
            parsed_data = json.loads(data)
            self.balance = parsed_data.get("balance", self.balance)
            self.holdings = parsed_data.get("holdings", {})

    def export_to_json(self, filename="trading_data.json"):
        """Exports trading data to a JSON file."""
        with open(filename, "w") as file:
            json.dump({"balance": self.balance, "holdings": self.holdings}, file)

    def import_from_json(self, filename="trading_data.json"):
        """Imports trading data from a JSON file."""
        with open(filename, "r") as file:
            data = json.load(file)
            self.balance = data.get("balance", self.balance)
            self.holdings = data.get("holdings", {})
            self.save_to_redis()

    def fetch_kraken_prices(self):
        """Fetches the latest prices for all held tickers from Kraken API."""
        prices = {}
        if self.holdings :
            tickers = ",".join([f"{ticker}USDC" for ticker in self.holdings.keys()])
            response = requests.get(f"{KRAKEN_API_URL}?pair={tickers}")
            
            if response.status_code == 200:
                data = response.json()
                for ticker, info in data["result"].items():
                    prices[ticker.replace("USDC", "")] = float(info["c"][0])

        return prices
    
    def fetch_kraken_ticker_price(self, ticker: str):
        """Fetches the current price of a specific ticker from Kraken API."""
        response = requests.get(f"{KRAKEN_API_URL}?pair={ticker}USDC")
        if response.status_code == 200:
            try:
                data = response.json()
                return float(data["result"][f"{ticker}USDC"]["c"][0])
            except (KeyError, ValueError):
                return None
        return None

    def compute_wallet_usdc(self):
        """Returns the available USDC balance."""
        return self.balance

    def compute_ticker_sum_usdc(self):
        """Computes the total portfolio value in USDC based on current market prices."""
        prices = self.fetch_kraken_prices()
        total_value = self.balance
        for ticker, amount in self.holdings.items():
            if ticker in prices:
                total_value += amount * prices[ticker]
        return total_value

    def get_status(self):
        """Returns the current status of balance and holdings."""
        return {
            'balance': self.balance,
            'holdings': self.holdings
        }
    
    def buy(self, ticker: str, amount: float):
        """Attempts to buy a specified amount of a ticker using USDC."""
        price = self.fetch_kraken_ticker_price(ticker)
        if price is None:
            return "Error: Failed to fetch price"
        
        cost = amount * price * (1 + self.trading_fee)
        if cost > self.balance:
            return "Error: Insufficient balance"
        
        self.balance -= cost
        self.holdings[ticker] = self.holdings.get(ticker, 0) + amount
        self.save_to_redis()
        return f"Bought {amount} {ticker} for {cost} USDC"

    def sell(self, ticker: str, amount: float):
        """Attempts to sell a specified amount of a ticker for USDC."""
        price = self.fetch_kraken_ticker_price(ticker)
        if price is None:
            return "Error: Failed to fetch price"
        
        if ticker not in self.holdings or self.holdings[ticker] < amount:
            return "Error: Insufficient holdings"
        
        revenue = amount * price * (1 - self.trading_fee)
        self.balance += revenue
        self.holdings[ticker] -= amount
        if self.holdings[ticker] == 0:
            del self.holdings[ticker]
        
        self.save_to_redis()
        return f"Sold {amount} {ticker} for {revenue} USDC"

