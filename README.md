# cTrader Trade Analysis

Analyse your cTrader trade history using Jupyter Notebooks. This tool fetches your order history via the cTrader Open API and calculates key performance metrics like Win Rate, Average Win/Loss, and Trade Expectancy.

## Prerequisites

- **Python 3.11+**
- **cTrader Open API Credentials**: Register your application at [openapi.ctrader.com](https://openapi.ctrader.com/apps) to get your Client ID and Secret.

## Setup

1. **Install Dependencies**:
   This project uses `uv` for fast package management.
   ```bash
   uv sync
   ```

2. **Configure Credentials**:
   Create a `credentials.json` file in the root directory:
   ```json
   {
     "accountId": 123456,
     "clientId": "your_client_id",
     "clientSecret": "your_client_secret",
     "accessToken": "your_access_token"
   }
   ```

## How to Run

1. **Fetch Data & Analyse**:
   Open `analysis.ipynb` in Jupyter (or PyCharm).
   - The first cell uses `fetch_orders.py` to download your trade history into `data/orders.json`.
   - Update the `from_ts` variable in the notebook to filter the start date of your analysis.
   - Run the subsequent cells to process the data with `pandas` and view the metrics.

2. **(Optional) Update OA Models**:
   If the cTrader API definitions change, regenerate the local JSON models by running:
   ```bash
   uv run python -c "from oa_model import create_model; create_model()"
   ```

## Project Structure

- `analysis.ipynb`: The main playground for data processing and visualization.
- `fetch_orders.py`: Async client to interface with the cTrader WebSocket API.
- `models/`: Contains custom JSON mappings for Open API messages and payload types.
- `data/`: Local storage for fetched order history.