import streamlit as st
import pandas as pd
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from datetime import date

# Ustawienia strony
st.set_page_config(layout="wide")
st.title('📈 Global Economy Indicators Tech Analysis Dashboard')

# Data dzisiejsza
today = date.today()

# Słownik symboli
comm_dict = {
    '^GSPC': 'SP_500', '^DJI': 'DJI30', '^IXIC': 'NASDAQ', '000001.SS': 'SSE Composite Index',
    '^HSI': 'HANG SENG INDEX', '^VIX': 'CBOE Volatility Index', '^RUT': 'Russell 2000',
    '^BVSP': 'IBOVESPA', '^FTSE': 'FTSE 100', '^GDAXI': 'DAX PERFORMANCE-INDEX',
    '^N100': 'Euronext 100 Index', '^N225': 'Nikkei 225', '^FCHI': 'CAC 40', '^AXJO': 'S&P/ASX 200',
    'EURUSD=X': 'EUR_USD', 'EURCHF=X': 'EUR_CHF', 'CNY=X': 'USD/CNY', 'GBPUSD=X': 'USD_GBP',
    'JPY=X': 'USD_JPY', 'EURPLN=X': 'EUR/PLN', 'PLN=X': 'PLN/USD', 'GBPPLN=X': 'PLN/GBP',
    'RUB=X': 'USD/RUB', 'EURRUB=X': 'EUR/RUB', 'MXN=X': 'USD/MXN', 'EURJPY=X': 'EUR/JPY',
    'EURSEK=X': 'EUR/SEK', 'DX-Y.NYB': 'US Dollar Index', '^XDE': 'Euro Currency Index',
    '^XDN': 'Japanese Yen Currency Index', '^XDA': 'Australian Dollar Currency Index',
    '^XDB': 'British Pound Currency Index', '^FVX': '5_YB', '^TNX': '10_YB', '^TYX': '30_YB',
    'CL=F': 'Crude_Oil', 'BZ=F': 'Brent_Oil', 'GC=F': 'Gold', 'HG=F': 'Copper', 'PL=F': 'Platinum',
    'SI=F': 'Silver', 'NG=F': 'Natural Gas', 'ZR=F': 'Rice Futures', 'ZS=F': 'Soy Futures',
    'BTC-USD': 'Bitcoin USD', 'ETH-USD': 'Ethereum USD'
}

# Funkcja pobierania danych
@st.cache_data(show_spinner=False)
def get_data(symbol):
    df = yf.download(symbol, start='2000-09-01', end=today, interval='1d')
    return df.reset_index()

# Sidebar – wybór instrumentu
st.sidebar.subheader("Wybierz instrument")
selected_comm = st.sidebar.radio('', list(comm_dict.values()), index=0)

# Znajdź symbol z dict
selected_symbol = [k for k, v in comm_dict.items() if v == selected_comm][0]

# Pobieranie danych
data = get_data(selected_symbol)

# Sprawdź czy dane nie są puste
if data.empty:
    st.error("Brak danych do wyświetlenia. Spróbuj później lub wybierz inny instrument.")
    st.stop()

# Panel danych podstawowych
st.subheader(f'📊 Notowania: {selected_comm}')
col1, col2 = st.columns([0.6, 0.4])

with col1:
    start_date = data['Date'].min().strftime('%Y-%m-%d')
    end_date = data['Date'].max().strftime('%Y-%m-%d')
    close_max = data['Close'].max()
    close_min = data['Close'].min()
    last_close = data['Close'].iloc[-1]

    st.metric("📅 Data początkowa", start_date)
    st.metric("📅 Data końcowa", end_date)
    st.metric("🔼 Maksimum", f"{close_max:.2f}")
    st.metric("🔽 Minimum", f"{close_min:.2f}")
    st.metric("📌 Ostatnie zamknięcie", f"{last_close:.2f}")

with col2:
    history_length = st.slider("Długość historii (dni):", 30, len(data), 200)
    data = data.tail(history_length)

# Wykres bazowy
fig = go.Figure()
fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='Close', line=dict(color='black')))

# Średnie kroczące
if st.sidebar.checkbox("Pokaż średnie kroczące"):
    short = st.sidebar.number_input("Okres krótkoterminowy", 2, 100, 5)
    long = st.sidebar.number_input("Okres długoterminowy", 5, 200, 20)
    data['Short_SMA'] = data['Close'].rolling(window=short).mean()
    data['Long_SMA'] = data['Close'].rolling(window=long).mean()

    fig.add_trace(go.Scatter(x=data['Date'], y=data['Short_SMA'], name='Short SMA', line=dict(color='green', dash='dot')))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Long_SMA'], name='Long SMA', line=dict(color='red', dash='dot')))

# RSI
if st.sidebar.checkbox("Pokaż RSI"):
    rsi_period = st.sidebar.slider("Okres RSI", 5, 30, 14)
    rsi = RSIIndicator(close=data['Close'], window=rsi_period)
    data['RSI'] = rsi.rsi()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['RSI'], name='RSI', yaxis='y2', line=dict(color='orange')))

# ATR
if st.sidebar.checkbox("Pokaż ATR"):
    atr_period = st.sidebar.slider("Okres ATR", 5, 50, 14)
    atr = AverageTrueRange(high=data['High'], low=data['Low'], close=data['Close'], window=atr_period)
    data['ATR'] = atr.average_true_range()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['ATR'], name='ATR', yaxis='y2', line=dict(color='blue')))

# Konfiguracja osi pomocniczej jeśli RSI lub ATR
if 'RSI' in data or 'ATR' in data:
    fig.update_layout(
        yaxis2=dict(title='RSI/ATR', overlaying='y', side='right'),
    )

# Świece
if st.sidebar.checkbox("Pokaż świecowy wykres"):
    fig = go.Figure(data=[go.Candlestick(x=data['Date'],
                                         open=data['Open'],
                                         high=data['High'],
                                         low=data['Low'],
                                         close=data['Close'])])

# Finalny wykres
fig.update_layout(title=f"{selected_comm} - wykres", xaxis_title="Data", yaxis_title="Cena", width=1100, height=600)
st.plotly_chart(fig, use_container_width=True)

# Stopka
st.sidebar.markdown("---")
st.sidebar.write("© Michał Leśniewski")

