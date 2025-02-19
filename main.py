from typing import Annotated
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from trade_simulator import TradingModule
import requests
import json
import redis

# Initialize Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
KRAKEN_API_URL = "https://api.kraken.com/0/public/Assets"
FAV_PATH = 'static/favicon.ico'
# Cache expiry times
TICKER_CACHE_EXPIRY = 600  # 10 minutes
PRICE_CACHE_EXPIRY = 30  # 30 seconds

# Initialize FastAPI application
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize trading module with a default balance
trading_module = TradingModule(initial_balance=10000)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Renders the main trading dashboard."""
    context = {
        "request": request,
        "wallet_balance": trading_module.compute_wallet_usdc(),
        "total_value": trading_module.compute_ticker_sum_usdc(),
    }
    
    return templates.TemplateResponse("dashboard.html", context)

@app.get("/wallet_usdc")
async def wallet_usdc():
    """Handles asset purchase requests and updates the dashboard."""
    return JSONResponse({"wallet_usdc": trading_module.compute_wallet_usdc()}, 200)

@app.get("/ticker_sum_usdc")
async def ticker_sum_usdc():
    """Handles asset purchase requests and updates the dashboard."""
    return JSONResponse({"total_value": trading_module.compute_ticker_sum_usdc()}, 200)

@app.get("/ticker_prices_usdc")
async def ticker_prices_usdc():
    """Fetches and caches ticker prices from Kraken."""
    cache_key = "ticker_prices_usdc2"
    
    # Check Redis cache first
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return JSONResponse(json.loads(cached_data))

    try:
        prices = trading_module.fetch_kraken_prices()
        # Cache for 30 seconds
        redis_client.setex(cache_key, PRICE_CACHE_EXPIRY, json.dumps(prices))
        return JSONResponse(prices)
    except requests.RequestException as e:
        return JSONResponse({"error": str(e)}, 500)

@app.post("/buy", response_class=HTMLResponse)
async def buy_asset(request: Request, ticker:Annotated[str, Form()], amount:Annotated[float, Form()]):
    """Handles asset purchase requests and updates the dashboard."""
    trading_module.buy(ticker, amount)
    return await home(request)

@app.post("/sell", response_class=HTMLResponse)
async def sell_asset(request: Request, ticker:Annotated[str, Form()], amount:Annotated[float, Form()]):
    """Handles asset selling requests and updates the dashboard."""
    trading_module.sell(ticker, amount)
    return await home(request)

# corriger
@app.get("/status", response_class=HTMLResponse)
async def get_status(request: Request):
    """Renders a status page with current holdings."""
    context = {"request": request, "status": trading_module.get_status()}
    return templates.TemplateResponse("status.html", context)

@app.post("/export_json")
async def export_json():
    """Exports trading data to a JSON file."""
    trading_module.export_to_json()
    return JSONResponse({"message": "Data exported to JSON"}, 200)

@app.get("/kraken_tickers")
async def get_kraken_tickers():
    """Fetches the list of tradable assets from Kraken and caches the response in Redis."""
    cache_key = "kraken_tickers2"

    # Check if the ticker list is cached
    cached_data = redis_client.get(cache_key)
    if cached_data:
        print("cached")
        return {"tickers": json.loads(cached_data)} 

    try:
        response = requests.get(KRAKEN_API_URL)
        response.raise_for_status()  # Raise an error for non-200 responses
        data = response.json()

        # Extract asset pairs
        tickers = list(data["result"].keys())

        # Cache the data for 10 minutes
        redis_client.setex(cache_key, TICKER_CACHE_EXPIRY, json.dumps(tickers))

        return JSONResponse({"tickers": tickers}, 200)
    except requests.RequestException as e:
        return JSONResponse({"error": str(e)}, 500)

@app.get("/wallet_holding")
async def wallet_holding():
    """current holdings."""
    return trading_module.holdings

@app.post("/import_json")
async def import_json():
    """Imports trading data from a JSON file."""
    trading_module.import_from_json()
    return JSONResponse({"message": "Data imported from JSON", "status": trading_module.get_status()}, 200)


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    """Serves the favicon.ico file."""
    return FileResponse(FAV_PATH)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)