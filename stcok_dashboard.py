import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import date, timedelta, datetime

#FUNCTIONS

def flatten_multiindex(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [''.join([str(c) for c in col if c]).strip() for col in df.columns.values]
    return df

def pull_default_price(ticker, buy_date):
    data = yf.download(ticker, start=buy_date, end=buy_date + timedelta(days=1))
    default_price = float(round(data["Open"], 2).iloc[0].iloc[0])
    return default_price

def get_bought_market_value(ticker, buy_date, quantity, buy_price=None):
    if buy_price:
        market_value = quantity * buy_price
    else:
        market_value = quantity * pull_default_price(ticker, buy_date)
    return market_value

def add_to_portfolio(ticker, buy_date, quantity, portfolio, buy_price = None):
    if not buy_price:
        buy_price = pull_default_price(ticker=ticker, buy_date=buy_date)
    new_buy = pd.DataFrame({"Ticker":[ticker], 'Buy Date' : [buy_date],  'Quantity' : [quantity], 'Buy Price' : [buy_price], 'Buy MV' : [buy_price * quantity]})
    portfolio = pd.concat([portfolio, new_buy], ignore_index=True)
    return portfolio

def generate_pnl(portfolio):

    pnl_list = []

    end_date = datetime.today().strftime('%Y-%m-%d')
    
    for idx, row in portfolio.iterrows():
        ticker = row['Ticker']
        start_date = row['Buy Date']
        buy_price = row['Buy Price']
        quantity = row['Quantity']

        data = yf.download(ticker, start=start_date, end=end_date)
        data = flatten_multiindex(data)
        
        close_col = [col for col in data.columns if col.startswith('Close')]
        data = data[[close_col[0]]].rename(columns={close_col[0]: 'Close'})

        data = data[['Close']]


        # Calculate cumulative PnL
        data['cum_pnl'] = (data['Close'] - buy_price) * quantity
        
        # Daily PnL change
        data['daily_change'] = data['cum_pnl'].diff()
        
        # Add quantity and ticker info
        data['ticker'] = ticker
        data['quantity'] = quantity
        
        # Reset index and rename date column
        data = data.reset_index().rename(columns={'Date': 'date'})
        
        pnl_list.append(data)

    # Combine all transactions
    pnl = pd.concat(pnl_list, ignore_index=True)

    pnl = pnl[['date', 'ticker', 'Close', 'quantity', 'cum_pnl', 'daily_change']]
    print(pnl.index)

    if not pnl_list:
        return pd.DataFrame(columns=['date', 'ticker', 'Close', 'quantity', 'cum_pnl', 'daily_change'])
 
    return pd.DataFrame(pnl)


st.title("Portfolio PnL Dashboard")
st.set_page_config(page_title="Portfolio PnL", page_icon="📈", layout='wide')

if "portfolio" not in st.session_state:
    st.session_state.portfolio = pd.DataFrame(columns=["Ticker", "Buy Date", "Buy Price", "Quantity"])

# Portfolio Entry
st.sidebar.header("Add to Portfolio")
ticker = st.sidebar.text_input("Stock Ticker (e.g., AAPL)")
buy_date = st.sidebar.date_input("Buy Date", date(2023, 2, 1))
quantity = st.sidebar.number_input("Quantity", 1, step=1)

default_price = 0.0
if ticker and buy_date:
    try:
        default_price = pull_default_price(ticker=ticker, buy_date=buy_date)
    except Exception as e:
        st.sidebar.warning(f"Could not fetch price: {e}")

# Allow user to override default price
buy_price = st.sidebar.number_input("Buy Price", value=default_price)

if st.sidebar.button("Add to Portfolio"):
    if ticker and buy_price:
        st.session_state.portfolio = add_to_portfolio(ticker=ticker, buy_date=buy_date, quantity=quantity, buy_price=buy_price, portfolio=st.session_state.portfolio)




#***************POST STOCK ADDITION PNL CHARTING***********************


PnL = generate_pnl(st.session_state.portfolio)

initial_investment = st.session_state.portfolio['Buy MV'].sum()
latest_prices = PnL.groupby('ticker').apply(lambda x: x.iloc[-1])  
current_market_value = (latest_prices['Close'] * latest_prices['quantity']).sum()
total_pnl = current_market_value - initial_investment

pnl_color = "#28B463" if total_pnl > 0 else "#C0392B" if total_pnl < 0 else "#7F8C8D"


col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
            <div style='text-align: center;'>
                <h3 style='color:#2E86C1;'>Initial Investment</h3>
                <h2>${initial_investment:,.2f}</h2>
            </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
            <div style='text-align: center;'>
                <h3 style='color:#2E86C1;'>Current Market Value</h3>
                <h2>${current_market_value:,.2f}</h2>
            </div>
        """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
            <div style='text-align: center;'>
                <h3 style='color:{pnl_color};'>PnL</h3>
                <h2 style='color:{pnl_color};'>${total_pnl:,.2f}</h2>
            </div>
        """, unsafe_allow_html=True)

# Show current portfolio
st.subheader("Current Portfolio")
st.dataframe(st.session_state.portfolio)

#Chart PNL
if not st.session_state.portfolio.empty:
    # Plot
    fig = px.line(
    PnL,
    x='date',
    y='cum_pnl',
    color='ticker',
    title='Cumulative PnL per Ticker',
    markers=True,
    hover_data=['Close', 'quantity', 'daily_change']
    )

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Cumulative PnL ($)',
        hovermode='x unified'
    )

    st.plotly_chart(fig)

    st.subheader("Current PnL")
    st.dataframe(PnL)