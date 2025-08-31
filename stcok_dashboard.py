import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

st.title("Portfolio PnL Dashboard")
st.set_page_config(page_title="Portfolio PnL", page_icon="📈")

if "portfolio" not in st.session_state:
    st.session_state.portfolio = pd.DataFrame(columns=["Ticker", "Buy Date", "Buy Price", "Quantity"])

# Portfolio Entry
st.header("Add to Portfolio")
ticker = st.text_input("Stock Ticker (e.g., AAPL)")
buy_date = st.date_input("Buy Date", date(2023, 1, 1))
quantity = st.number_input("Quantity", 1, step=1)