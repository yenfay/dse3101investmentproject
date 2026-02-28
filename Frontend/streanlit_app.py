import duckdb

con = duckdb.connect("Datasets/investment.duckdb")
top_holdings = con.execute("""
    SELECT * FROM holdings
    WHERE quarter = '2025Q1'
    ORDER BY value DESC
    LIMIT 20
""").fetchdf()