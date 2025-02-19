# Trading Simulator API

This project is a FastAPI-based trading simulator that allows users to manage a simulated portfolio by buying and selling assets. It integrates with Kraken's API to fetch asset prices and uses Redis for caching.

## Features
- View trading dashboard with wallet balance and asset value.
- Fetch and cache asset prices from Kraken.
- Buy and sell assets.
- Export and import trading data as JSON.
- View current holdings.
- API caching with Redis.

## Installation

### Prerequisites
- Python 3.8+
- Redis server running on `localhost:6379` or using Docker

### Setup
1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd <project-directory>
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Start the Redis server:
   ```sh
   redis-server
   ```
   **Or using Docker:**
   ```sh
   docker run --name redis -p 6379:6379 -d redis
   ```

4. Run the FastAPI application:
   ```sh
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## Running with Docker
To build and run the application using Docker:
```sh
docker build -t trading-simulator .
docker run -p 8000:8000 trading-simulator
```

To start Redis using Docker:
```sh
docker run --name redis -p 6379:6379 -d redis
```

## Running with Docker Compose
To build and run the application along with Redis using Docker Compose:
```sh
docker-compose up --build
```
This will start both the trading application and the Redis server.

To stop the services:
```sh
docker-compose down
```

## API Endpoints

### GET /
- **Description:** Renders the main trading dashboard.
- **Response:** HTML page with wallet balance and asset value.

### GET /wallet_usdc
- **Description:** Returns the current USDC wallet balance.
- **Response:** `{ "wallet_usdc": float }`

### GET /ticker_sum_usdc
- **Description:** Returns the total value of all held assets in USDC.
- **Response:** `{ "total_value": float }`

### GET /ticker_prices_usdc
- **Description:** Fetches and caches ticker prices from Kraken.
- **Response:** `{ "ticker": price }`

### POST /buy
- **Description:** Buys a specified asset.
- **Parameters:**
  - `ticker`: Asset ticker (str)
  - `amount`: Amount to buy (float)

### POST /sell
- **Description:** Sells a specified asset.
- **Parameters:**
  - `ticker`: Asset ticker (str)
  - `amount`: Amount to sell (float)

### GET /status
- **Description:** Returns the current trading status.
- **Response:** HTML page with holdings.

### POST /export_json
- **Description:** Exports trading data to a JSON file.
- **Response:** `{ "message": "Data exported to JSON" }`

### GET /kraken_tickers
- **Description:** Fetches tradable asset tickers from Kraken and caches them.
- **Response:** `{ "tickers": ["BTC", "ETH", ...] }`

### GET /wallet_holding
- **Description:** Returns current asset holdings.
- **Response:** `{ "holdings": { "ticker": amount } }`

### POST /import_json
- **Description:** Imports trading data from a JSON file.
- **Response:** `{ "message": "Data imported from JSON", "status": { ... } }`

### GET /favicon.ico
- **Description:** Serves the favicon.ico file.

## Technologies Used
- **FastAPI**: Web framework for API development.
- **Redis**: Caching layer for API responses.
- **Jinja2**: Templating engine for rendering HTML pages.
- **Uvicorn**: ASGI server to run the application.
- **Kraken API**: Fetching asset prices.

## License
This project is licensed under the MIT License.
