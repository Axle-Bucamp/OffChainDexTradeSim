# Bird Eye Trading Module

## Overview
Bird Eye Trading is a FastAPI-based trading simulation module that allows users to perform buy and sell transactions for different tickers while maintaining account balance and holdings. The module includes:
- FastAPI endpoints for trading operations.
- Persistent storage using Redis.
- JSON export/import for long-term data storage.

## Features
- **Buy & Sell**: Trade various tickers with a simulated balance.
- **Wallet Computation**: Compute total holdings in USDC.
- **Persistent Storage**: Uses Redis for long-term data storage.
- **Data Export & Import**: Save and load trading data using JSON.

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/bird-eye-trading.git
   cd bird-eye-trading
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Start Redis (if not running already):
   ```sh
   redis-server
   ```
4. Run the FastAPI server:
   ```sh
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## API Endpoints
### Buy Asset
- **Endpoint**: `/buy`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "ticker": "BTC",
    "price": 50000,
    "amount": 0.01
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "status": {
      "balance": 9999.95,
      "holdings": { "BTC": 0.01 }
    }
  }
  ```

### Sell Asset
- **Endpoint**: `/sell`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "ticker": "BTC",
    "price": 52000,
    "amount": 0.01
  }
  ```

### Get Wallet USDC Balance
- **Endpoint**: `/wallet_usdc`
- **Method**: `GET`

### Compute Total Holdings in USDC
- **Endpoint**: `/ticker_sum_usdc`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "BTC": 52000,
    "ETH": 3500
  }
  ```

### Export Data to JSON
- **Endpoint**: `/export_json`
- **Method**: `POST`

### Import Data from JSON
- **Endpoint**: `/import_json`
- **Method**: `POST`

## License
This project is licensed under the MIT License.

