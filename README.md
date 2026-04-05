# DSE3101 Investment Project

## Prerequisites

- Python 3.x
- A virtual environment 
- Kaggle account with API credentials
- OpenFIGI API key

---

## Quick Start (Development)
1. Clone the repo and set up `.env` with `DEBUG=true`
2. Activate your virtual environment
3. `pip install -r requirements.txt`
4. `python -m Backend.transform.batch_run.batch_process_form13f`

---

## Getting Started

### 1. Set Working Directory

Ensure your current working directory is the project root:

```
dse3101investmentproject/
```

### 2. Configure the `.env` File

Create a `.env` file at the project root (same level as this `README.md`) with the following contents:

```dotenv
# App config
DEBUG=true               # true = development mode | false = production mode (for prof)

# Kaggle
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key

# OpenFIGI
OPENFIGI_API_KEY=your_openfigi_api_key
OPENFIGI_URL=https://api.openfigi.com/v3/mapping
```

> **`DEBUG=true` (Development):** Automatically downloads the latest dataset from Kaggle on first run.
>
> **`DEBUG=false` (Production):** Downloads only the raw zip files required for the pipeline.


### 3. Install Dependencies

Ensure your virtual environment is activated, then run:
```bash
pip install -r requirements.txt
```

> **Note:** If you do not have a virtual environment set up yet:
> ```bash
> # Create virtual environment
> python -m venv venv
>
> # Activate it
> # Windows:
> venv\Scripts\activate
> # Mac/Linux:
> source venv/bin/activate
> ```
> Then run `pip install -r requirements.txt` again.

---

## Running the Pipeline

### Step 4 — Transformation 
### Step 4.1 — Transform Form13F data

#### Production (`DEBUG=false`)

Processes raw data through the full transformation pipeline:

```
13F_zip_files → 13F_clean_files → 13F_filtered_and_mapped_files → 13F_filtered_and_mapped_and_screened_files
```

**Run:**

```bash
python -m Backend.transform.batch_run.batch_process_form13f
```

---

#### Development (`DEBUG=true`)

Downloads all data from Kaggle and runs the pipeline locally.

**Steps:**

1. Set `DEBUG=true` in your `.env` file.
2. Run the transform module:
   ```bash
   python -m Backend.transform.batch_run.batch_process_form13f
   ```
3. Verify that a `Datasets/` folder has been created containing the latest data files.

---
### Step 4.2 — Transform Stock Price data
#### Production (`DEBUG=false`)

Download stock price data from Yahoo Finance API using stock_market_price.py and consolidate the files into one combined using consolidate_stock_price.py.

```
Data found in: Datasets/stock_price_data folder
Combined stock price data: Datasets/stock_price_data/stock_prices_all.parquet
```

**Run:**

```bash
python -m Backend.transform.batch_run.batch_process_stock_price
```

### Step 5 — Backtesting
#### 5a. Get Top N Institutions
Returns files in Datasets/best_institutions_ranking folder.

**Run (to get files in best_institutions_ranking):**

```bash
python -m Backend.backtesting.batch_process_rank_institutions
```

---

#### 5b. Get Top M Stocks

Returns `portfolio_df` and `metrics_df` for the top M stocks. This step runs in conjunction with the frontend.

**Run (for testing):**

```bash
python -m Backend.backtesting.batch_process_rank_stocks
```

**Frontend Integration:**

Import and call `main()` from `Backend.backtesting.batch_process_rank_stocks` in your frontend script, passing the user inputs as arguments:

```python
from Backend.backtesting.batch_process_rank_stocks import main

portfolio_df, metrics_df = main(
    userinput_start_date='2013-12-31',
    userinput_end_date='2025-05-23',
    userinput_initial_capital=10_000,
    userinput_topN=10,
    userinput_topN_institutions=10,
    userinput_lag=47,
    userinput_cost_rate=0.001,
)
```

**User Input Parameters:**

| Parameter                   | Default        | Description                                              |
|-----------------------------|----------------|----------------------------------------------------------|
| `userinput_start_date`      | `'2013-12-31'` | Backtest start date                                      |
| `userinput_end_date`        | `'2025-05-23'` | Backtest end date                                        |
| `userinput_initial_capital` | `10_000`       | Starting capital (USD)                                   |
| `userinput_topN`            | `10`           | Number of top stocks to hold per quarter                 |
| `userinput_topN_institutions` | `10`         | Number of top institutions to track (`10`, `20`, or `30`) |
| `userinput_lag`             | `47`           | Lag in days between filing date and portfolio rebalancing |
| `userinput_cost_rate`       | `0.001`        | Transaction cost as a fraction of traded value (0.1%)    |

## Project Structure

```
dse3101investmentproject/
├── .env                         ← secrets and config (never commit this)
├── .gitignore
├── README.md
├── config.py                    ← all paths and env variables
├── Datasets/
│   ├── 13F_zip_files/
│   ├── 13F_clean_files/
│   ├── 13F_filtered_and_mapped_files/
│   ├── 13F_filtered_and_mapped_and_screened_files/
│   ├── data_for_frontend/
│   ├── final_files/                    ← tracked by Git LFS
│   │   ├── final_top10_form13f.parquet
│   │   ├── final_top10_prices.parquet
│   │   ├── final_top20_form13f.parquet
│   │   ├── final_top20_prices.parquet
│   │   ├── final_top30_form13f.parquet
│   │   └── final_top30_prices.parquet
│   ├── others/
│   └── stock_price_data/
├── Backend/
│   ├── transform/
│   │   ├── batch_run/
│   │   │   ├── batch_process_stock_price.py ← main run function for transform of stock price data
│   │   │   └── batch_process_form13f.py     ← main run function for transform of form13f data
│   │   └── download_data_from_kaggle.py     ← helper to download latest data from kaggle
│   └── backtesting/
│       └── batch_process_rank_stocks.py     ← main run function for backtesting of topN stocks (integration with frontend)
├── Frontend/
│   ├── app.py                               ← main file to run dashboard
│   ├── components/                          
│   │   ├── cumulative_returns.py            ← user input functions
│   │   ├── daily_returns.py                 ← user input functions
│   │   ├── performance_metrics.py           ← user input functions
│   │   ├── portfolio_performance.py         ← functions for left panel of dashboard
│   │   └── top_20.py                        ← functions for right panel of dashboard
│   ├── streamlit/
│   │   └── config.toml                      ← customise theme 
```
