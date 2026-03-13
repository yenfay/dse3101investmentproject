import streamlit as st
from components.new_backtest import new_backtest_button #for yenfay's code testing, DO NOT OVERWRITE PLEASE! 
from components.top_20 import top_20_table #for yenfay's code testing, DO NOT OVERWRITE PLEASE! 

# page set up and layout
st.set_page_config(
    page_title="dse3101 project",
    layout="wide"
)

# title and new backtest button layout
c_title, c_backtest = st.columns([9, 1], vertical_alignment = "middle")
with c_title: 
    st.title("Beginner Dashboard")
with c_backtest: 
    new_backtest_button()
    
# date layout
c1, c2, c3 = st.columns([0.8, 0.1, 0.1])
with c1: 
    st.write("")
with c2:
    from_date = st.date_input("From:", key="from_date")
with c3:
    to_date = st.date_input("To:", key="to_date")

# configure left column for graph and right column for table
col_left, col_right = st.columns([6, 4])

with col_left:
    st.header("Porfolio performance")
    ### ruiqian add your code here for the metrics ###
    # Placeholder for now
    st.line_chart([1,2,3,2,5])

with col_right:
    st.header("Top 20 Stocks by Institutional Holdings")
    top_20_table()