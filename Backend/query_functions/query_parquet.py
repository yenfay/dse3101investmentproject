# this file is basic functions for standard quieries of form13f parquet files (tbc, i just directly copy and paste from chatgpt, we can edit later. -sarah)

from pathlib import Path
import duckdb
import pandas as pd

# ==========================================================
# Paths
# ==========================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PARQUET_DIR = PROJECT_ROOT / "Datasets/13F_clean_files"
PARQUET_PATTERN = str(PARQUET_DIR / "*_clean_df.parquet")

# note: maybe we shld make a config file for paths. -sarah

# ==========================================================
# Core functions
# ==========================================================

def load_all_data(columns=None):
    """
    Load all Parquet files into a single DataFrame.
    Optionally select only specific columns.
    """
    cols_sql = f"SELECT {', '.join(columns)}" if columns else "SELECT *"
    query = f"{cols_sql} FROM '{PARQUET_PATTERN}'"
    df = duckdb.query(query).to_df()
    return df

def filter_by_quarter(quarter):
    """
    Return DataFrame filtered for a specific quarter.
    """
    query = f"""
        SELECT *
        FROM '{PARQUET_PATTERN}'
        WHERE quarter = '{quarter}'
    """
    return duckdb.query(query).to_df()

def top_n_holdings(quarter, n=20):
    """
    Return top N holdings by value for a specific quarter.
    """
    query = f"""
        SELECT *
        FROM '{PARQUET_PATTERN}'
        WHERE quarter = '{quarter}'
        ORDER BY value DESC
        LIMIT {n}
    """
    return duckdb.query(query).to_df()

def aggregate_holdings(ticker_list=None, min_value=None):
    """
    Aggregate holdings across all quarters.
    Can filter by tickers or minimum value.
    Returns total value per ticker.
    """
    where_clauses = []
    if ticker_list:
        tickers = ",".join(f"'{t}'" for t in ticker_list)
        where_clauses.append(f"ticker IN ({tickers})")
    if min_value:
        where_clauses.append(f"value >= {min_value}")
    
    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    
    query = f"""
        SELECT ticker, SUM(value) AS total_value
        FROM '{PARQUET_PATTERN}'
        {where_sql}
        GROUP BY ticker
        ORDER BY total_value DESC
    """
    return duckdb.query(query).to_df()

def pivot_holdings(min_value=None):
    """
    Return a pivot table: rows=quarter, columns=ticker, values=value.
    Optional: filter out holdings below min_value.
    """
    where_sql = f"WHERE value >= {min_value}" if min_value else ""
    
    query = f"""
        SELECT quarter, ticker, value
        FROM '{PARQUET_PATTERN}'
        {where_sql}
    """
    df = duckdb.query(query).to_df()
    
    pivot_df = df.pivot(index='quarter', columns='ticker', values='value').fillna(0)
    return pivot_df

def join_with_prices(price_parquet_pattern, min_value=None):
    """
    Join holdings with price data for analysis/backtesting.
    price_parquet_pattern: glob pattern for Parquet files with 'ticker', 'quarter', 'price' columns
    Returns a merged DataFrame.
    """
    where_sql = f"WHERE h.value >= {min_value}" if min_value else ""
    
    query = f"""
        WITH holdings AS (
            SELECT quarter, ticker, value
            FROM '{PARQUET_PATTERN}'
            {where_sql}
        )
        SELECT h.quarter, h.ticker, h.value, p.price
        FROM holdings h
        LEFT JOIN '{price_parquet_pattern}' p
        ON h.ticker = p.ticker AND h.quarter = p.quarter
    """
    return duckdb.query(query).to_df()

