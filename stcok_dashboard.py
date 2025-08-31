import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import date, timedelta

st.title("Portfolio PnL Dashboard")
st.set_page_config(page_title="Portfolio PnL", page_icon="📈")


st.session_state.portfolio = pd.DataFrame(columns=["Ticker", "Buy Date", "Buy Price", "Quantity"])

# Portfolio Entry
st.header("Add to Portfolio")
ticker = st.text_input("Stock Ticker (e.g., AAPL)")
buy_date = st.date_input("Buy Date", date(2023, 2, 1))
quantity = st.number_input("Quantity", 1, step=1)

default_price = 0.0
if ticker and buy_date:
    try:
        data = yf.download(ticker, start=buy_date, end=buy_date + timedelta(days=1), progress=False)
        if not data.empty:
            print(data)
            default_price = float(round(data["Open"], 2).iloc[0].iloc[0])
    except Exception as e:
        st.warning(f"Could not fetch price: {e}")

# Allow user to override default price
buy_price = st.number_input("Buy Price", value=default_price)

if st.button("Add to Portfolio"):
    if ticker and buy_price:
        new_row = pd.DataFrame({"Ticker": [ticker], "Buy Date": [buy_date], "Buy Price": [buy_price], "Quantity": [quantity]})
        st.session_state.portfolio = st.session_state.portfolio.append(new_row, ignore_index=True)

# Show current portfolio
st.subheader("Current Portfolio")
st.dataframe(st.session_state.portfolio)