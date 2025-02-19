from pydantic import BaseModel

class TradeRequest(BaseModel):
    "simple request model to trade on simulator"
    ticker: str
    amount: float
