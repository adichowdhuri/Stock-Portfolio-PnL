import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import date

st.title("Portfolio PnL Dashboard")
st.set_page_config(page_title="Portfolio PnL", page_icon="📈")


st.session_state.portfolio = pd.DataFrame(columns=["Ticker", "Buy Date", "Buy Price", "Quantity"])

# Portfolio Entry
st.header("Add to Portfolio")
ticker = st.text_input("Stock Ticker (e.g., AAPL)")
buy_date = st.date_input("Buy Date", date(2023, 1, 1))
quantity = st.number_input("Quantity", 1, step=1)

default_price = None
if ticker and buy_date:
    data = yf.download(ticker, start=buy_date, end=buy_date)
    if not data.empty:
        default_price = round(data.iloc[0]["Open"], 2)

buy_price = st.number_input("Buy Price", value=default_price if default_price else 0.0)

if st.button("Add to Portfolio"):
    if ticker and buy_price:
        new_row = {"Ticker": ticker, "Buy Date": buy_date, "Buy Price": buy_price, "Quantity": quantity}
        st.session_state.portfolio = st.session_state.portfolio.append(new_row, ignore_index=True)

# Show current portfolio
st.subheader("Current Portfolio")
st.dataframe(st.session_state.portfolio)