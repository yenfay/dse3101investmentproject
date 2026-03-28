import duckdb
import pandas as pd
import numpy as np
import os

# Create a connection
con = duckdb.connect()

def filter_form13f_for_top_institutions(folder_path: str, institution_list: list[str], form13f_output: str):
    """
    Filters 13F files by CIK and saves directly to a new parquet file 
    without loading everything into memory.
    """
    # Get length of institutions list
    num_institutions = len(institution_list)

    # Format the CIK list for the SQL IN clause
    cik_filter = ", ".join(f"'{c}'" for c in institution_list)
    
    # Define the query to filter and select columns
    query = f"""
        COPY (
            SELECT
                CIK,
                FILINGMANAGER_NAME,
                CAST(PERIODOFREPORT AS DATE) AS PERIODOFREPORT,
                CAST(FILING_DATE AS DATE) AS FILING_DATE,
                TABLEVALUETOTAL,
                VALUE,
                CAST(CUSIP AS VARCHAR) AS CUSIP,
                CAST(ticker AS VARCHAR) AS ticker,
                name,      
                exchCode,
                equity_portfolio_total,
                equity_weight
            FROM read_parquet('{folder_path}/**/*.parquet', hive_partitioning = false)
            WHERE CIK IN ({cik_filter})
            AND exchCode IN ('US')
        )
        TO '{form13f_output}/final_top{num_institutions}_form13f.parquet' (FORMAT PARQUET)
    """
    
    # Execute the copy command
    con.execute(query)
    print(f"Filtered holdings saved to {form13f_output}/final_top{num_institutions}_form13f.parquet")


def filter_prices_for_top_institutions(institution_list: list[str], prices_file: str, holdings_file: str, prices_output_dir: str):
    """
    Filters the full stock price data to only include stocks held by the top_N institutions.
    """
    # Get length of institutions list
    num_institutions = len(institution_list)

    query = f"""
        COPY (
            SELECT p.*
            FROM read_parquet('{prices_file}') AS p
            WHERE p.ticker IN (
                SELECT DISTINCT ticker  
                FROM read_parquet('{holdings_file}')
                WHERE ticker IS NOT NULL
            )
        )
        TO '{prices_output_dir}/final_top{num_institutions}_prices.parquet' (FORMAT PARQUET);
    """

    con.execute(query)
    print(f"Filtered price data saved to: {prices_output_dir}/final_top{num_institutions}_prices.parquet")



