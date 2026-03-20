from pathlib import Path 
import logging
import pandas as pd
import numpy as np
import time
from Backend.backtesting.filter_institutions_and_prices_helper_functions import (
    filter_form13f_for_top_institutions,
    filter_prices_for_top_institutions,
)
from Backend.backtesting.rank_stocks_helper_functions import (
    load_holdings,
    load_prices,
    filter_dates,
    aggregate_stock_weights,
    rank_top10,
    apply_filing_lag_and_get_trade_prices,
    extract_price_subset,
    run_backtest,
)
from Backend.backtesting.evaluation_portfolio_helper_functions import (
    load_spy,
    get_comparison_df,
    compute_metrics,
)

# ==========================================================
# PATHS
# ==========================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2] #dse3101investmentproject
DATA_DIR = PROJECT_ROOT / "Datasets"

FORM13F_FOLDER_PATH = DATA_DIR / "13F_filtered_and_mapped_files"
PRICES_FILE_FULL = DATA_DIR / "stock_price_data" / "stock_prices_all.parquet"
OUTPUT_FOLDER = DATA_DIR / "final_files"

HOLDINGS_FILE = OUTPUT_FOLDER / "final_form13f.parquet"
PRICES_FILE = OUTPUT_FOLDER / "final_prices.parquet"

# ==========================================================
# CONFIG
# ==========================================================
TOP_N_INSTITUTIONS = ["0001135121", "0001346824", "0001387322", "0001112325", "0001354590", "0001352342", "0001647251", "0001398825", "0000911270", "0001425649"]

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ===========================================================
# 1. Get final form13f files and final price files (filtered to contain only top 20 institutions)
# ===========================================================
def get_final_files(top_n_institutions: list[str], form13f_folder_path: Path, prices_file_path: Path, output_folder: Path):
    logger.info("[INFO] Filtering full form13f data and stock price data for TOP N Institutions")
    filter_form13f_for_top_institutions(form13f_folder_path, top_n_institutions, output_folder)
    final_form13f_file = f"{output_folder}/final_form13f.parquet"
    filter_prices_for_top_institutions(prices_file_path, final_form13f_file, output_folder)
    logger.info("[INFO] Filtering DONE.")

# ===========================================================
# 2. Run strategy
# ===========================================================
def run_strategy(
    holdings_file_path: str,
    prices_file_path: str,
    start_date: str,
    end_date: str,
    initial_capital: float,
    lag: int = 47,             
) -> "pd.DataFrame":
    """
    End-to-end 13F copycat back-test.

    Parameters
    ----------
    holdings_file_path   : path to file containing form13f holdings data for all top institutions
    prices_file_path     : path to consolidated stock-price parquet file
    start_date           : inclusive start of PERIODOFREPORT filter  (YYYY-MM-DD)
    end_date             : inclusive end   of PERIODOFREPORT filter  (YYYY-MM-DD)
    initial_capital      : starting portfolio value in dollars
    lag                  : calendar days after PERIODOFREPORT before we trade (default 47)
                           trade_date = PERIODOFREPORT + lag, snapped back to prev trading day

    Returns
    -------
    DataFrame with columns:
        date             -- daily price observation dates
        quarter          -- PERIODOFREPORT the row belongs to
        trade_date       -- the actual date we execute the trade and the rebalance for that quarter (PERIODOFREPORT + lag, snapped forward)
        holding_period   -- period we hold the stocks for that quarter (e.g. "2020-02-15 to 2020-05-14")
        tickers          -- list of top-10 tickers held in that quarter
        portfolio_value  -- end-of-day mark-to-market value (shares * adj_close)
        daily_return     -- pct change vs previous trading day (NaN on first row)
        cum_return       -- cumulative return from inception
        quarter_return   -- total return for that quarter (repeated for every day in quarter)
    """
    logger.info("[INFO] Running strategy START")
    # 1. Load raw data
    holdings = load_holdings(holdings_file_path)
    logger.info("[INFO] Holdings loaded")
    prices   = load_prices(prices_file_path)
    logger.info("[INFO] Prices loaded")

    # 2. Filter holdings to the requested date range
    holdings = filter_dates(holdings, start_date, end_date)
    logger.info("[INFO] Filtered holdings to userinput dates")

    # 3. Aggregate cross-institution weights and pick top 10 per quarter
    agg   = aggregate_stock_weights(holdings)
    logger.info("[INFO] Stock weights aggregated")
    top10 = rank_top10(agg)
    logger.info("[INFO] Stocks ranked and top10 extracted per quarter")

    # 4. Compute candidate trade_date = earliest FILING_DATE + lag + get trade prices
    top10 = apply_filing_lag_and_get_trade_prices(top10, prices, lag_days=lag)
    logger.info("[INFO] Lagging applied and trade prices obtained")

    # 6. Narrow prices to only the tickers we actually hold (memory efficiency)
    prices_subset = extract_price_subset(prices, top10)
    logger.info("[INFO] Extracted price subset")

    # 7. Run the back-test
    logger.info("[INFO] Backtesting START")

    portfolio = run_backtest(top10, prices_subset, initial_capital)

    logger.info("[INFO] Backtesting END")
    logger.info("[INFO] Portoflio dataframe obtained")


    return portfolio

# ===========================================================
# 3. Run evaluation
# ===========================================================
def run_evaluation(portfolio_df, start_date, end_date, initial_capital):

    logger.info("[INFO] Running evaluation START")
    # 1. Get SPY data as benchmark for comparison, to evaluate our strategy performance against the overall market.
    spy_df = load_spy(start_date, end_date)
    logger.info("[INFO] SPY data loaded")

    # 2. Get comparison data (portfolio + SPY)
    comparison = get_comparison_df(portfolio_df, spy_df)

    # 3. Compute 13F Copycat strategy metrics
    strategy_metrics = compute_metrics(
        returns          = comparison["daily_return"].dropna(),
        label            = "13F Copycat",
        initial_capital  = initial_capital,
        portfolio_values = comparison["portfolio_value"],
    )
    logger.info("[INFO] 13F copycat strategy metrics computed")

    # 4. Compute SPY metrics
    spy_metrics = compute_metrics(
        returns          = comparison["spy_daily_return"].dropna(),
        label            = "SPY",
        initial_capital  = initial_capital,
        portfolio_values = comparison["spy_adj_close"] / comparison["spy_adj_close"].iloc[0] * initial_capital,
    )
    logger.info("[INFO] SPY data metrics computed")

    # return metrics_df
    metrics_df = pd.DataFrame([strategy_metrics, spy_metrics]).set_index("label")

    logger.info("[INFO] Evaluation of portfolio END.")
    logger.info("[INFO] Metrics dataframe obtained")

    return metrics_df


# ===========================================================
# MAIN RUN
# ===========================================================
def main(userinput_start_date, 
         userinput_end_date, 
         userinput_initial_capital,
         userinput_lag = 47):
    
    # To track time taken to run main()
    start = time.perf_counter()

    # 1. run strategy
    portfolio_df = run_strategy(
        holdings_file_path=HOLDINGS_FILE,
        prices_file_path=PRICES_FILE,
        start_date=userinput_start_date,
        end_date=userinput_end_date,
        initial_capital = userinput_initial_capital,
        lag=userinput_lag,
    )

    # 2. run evaluation
    metrics_df = run_evaluation(
        portfolio_df,
        start_date=userinput_start_date,
        end_date=userinput_end_date,
        initial_capital=userinput_initial_capital
    )
    
    logging.info(f"Time taken to run main(): {time.perf_counter() - start:.2f}s")

    return portfolio_df, metrics_df
# ---------------------------------------------------------------------------
# Quick smoke-test  (edit paths before running)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Inital step. Get final form13f files and final price files (filtered to contain only top 20 institutions)
    # get_final_files(TOP_N_INSTITUTIONS, FORM13F_FOLDER_PATH, PRICES_FILE_FULL, OUTPUT_FOLDER)
    # Note: One time use. To be commented when final form13f and final prices files are obtained

    # Change user inputs here:
    userinput_start_date = '2022-04-19' 
    userinput_end_date = '2024-05-23'
    userinput_initial_capital = 10_000
    userinput_lag = 47
    
    portfolio_df, metric_df = main(userinput_start_date, 
                                    userinput_end_date, 
                                    userinput_initial_capital,
                                    userinput_lag)
    
    portfolio_df.to_csv((DATA_DIR / "data_for_frontend" / "portfolio.csv"))
    metric_df.to_csv((DATA_DIR / "data_for_frontend" / "metrics.csv"))
