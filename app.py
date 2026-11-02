import streamlit as st
import yfinance as yf
import pandas as pd

st.title("My Portfolio Tracker")

holdings = {
    "AAPL": {"shares": 5, "cost_basis": 180},
    "MSFT": {"shares": 3, "cost_basis": 350},
    "SPY":  {"shares": 10, "cost_basis": 500},
    "NVDA": {"shares": 4, "cost_basis": 120},
}

@st.cache_data(ttl=600)
def get_prices(tickers, period):
    return yf.download(tickers, period=period, auto_adjust=True)["Close"]

tickers = list(holdings)
prices = get_prices(sorted(set(tickers + ["SPY"])), "1y")

df = pd.DataFrame(holdings).T.astype(float)
df["price"] = prices.iloc[-1][df.index]
df["value"] = df["shares"] * df["price"]
df["gain_pct"] = (df["price"] / df["cost_basis"] - 1) * 100
df["weight_pct"] = df["value"] / df["value"].sum() * 100

st.metric("Total value", f"${df['value'].sum():,.2f}")
st.dataframe(df.round(2))
st.bar_chart(df["weight_pct"])

st.subheader("Me vs. the S&P 500 (past year)")
portfolio = (prices[tickers] * df["shares"]).sum(axis=1)
comparison = pd.DataFrame({
    "My portfolio": portfolio / portfolio.iloc[0] * 100,
    "S&P 500": prices["SPY"] / prices["SPY"].iloc[0] * 100,
})
st.line_chart(comparison)

st.subheader("Growth projector")
monthly = st.slider("Monthly investment ($)", 25, 1000, 100, step=25)
years = st.slider("Years", 5, 40, 30)
rate = st.slider("Yearly return (%)", 1, 12, 7) / 100

balance = 0
history = []
for month in range(years * 12):
    balance = balance * (1 + rate / 12) + monthly
    history.append(balance)

chart = pd.Series(history)
chart.index = chart.index / 12
st.line_chart(chart)
st.write(f"You put in ${monthly * 12 * years:,} and end with about ${balance:,.0f}")
