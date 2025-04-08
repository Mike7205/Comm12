import streamlit as st
import pandas as pd
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
from datetime import date

# Ustawienia strony
st.set_page_config(layout="wide")
st.title('Global economy indicators tech analyse dashboard')

# Definicje
today = date.today()
comm_dict = {
    '^GSPC': 'SP_500', '^DJI': 'DJI30', '^IXIC': 'NASDAQ', 
    '000001.SS': 'SSE Composite Index', '^HSI': 'HANG SENG INDEX', '^VIX': 'CBOE Volatility Index',
    '^RUT': 'Russell 2000', '^BVSP': 'IBOVESPA', '^FTSE': 'FTSE 100', '^GDAXI': 'DAX PERFORMANCE-INDEX',
    '^N100': 'Euronext 100 Index', '^N225': 'Nikkei 225', '^FCHI':'CAC 40','^AXJO':'S&P/ASX 200',
    'EURUSD=X': 'EUR_USD', 'EURCHF=X': 'EUR_CHF', 'CNY=X': 'USD/CNY', 'GBPUSD=X': 'USD_GBP', 
    'JPY=X': 'USD_JPY', 'EURPLN=X': 'EUR/PLN', 'PLN=X': 'PLN/USD', 'GBPPLN=X':'PLN/GBP',
    'RUB=X': 'USD/RUB','EURRUB=X':'EUR/RUB','MXN=X':'USD/MXN', 'EURJPY=X':'EUR/JPY',
    'EURSEK=X':'EUR/SEK','DX-Y.NYB': 'US Dollar Index', '^XDE': 'Euro Currency Index', 
    '^XDN': 'Japanese Yen Currency Index', '^XDA': 'Australian Dollar Currency Index',
    '^XDB': 'British Pound Currency Index', '^FVX': '5_YB', '^TNX': '10_YB','^TYX': '30_YB', 
    'CL=F': 'Crude_Oil', 'BZ=F': 'Brent_Oil', 'GC=F': 'Gold','HG=F': 'Copper', 'PL=F': 'Platinum', 
    'SI=F': 'Silver', 'NG=F': 'Natural Gas', 'ZR=F': 'Rice Futures', 'ZS=F': 'Soy Futures', 
    'BTC-USD': 'Bitcoin USD','ETH-USD': 'Ethereum USD'
}

#@st.cache_data
def get_data(comm_label):
    df = yf.download(comm_label, start='2000-09-01', end=today, interval='1d')
    return df.reset_index()

def describe_data(df, comm_name):
    if df.empty:
        return pd.DataFrame()
    
    sh = df.shape[0]
    start_date = df['Date'].min().strftime('%Y-%m-%d')
    end_date = df['Date'].max().strftime('%Y-%m-%d')
    max_close = "{:.2f}".format(df['Close'].max())
    min_close = "{:.2f}".format(df['Close'].min())
    last_close = "{:.2f}".format(df['Close'].iloc[-1])
    
    return pd.DataFrame([{
        'Start_Date': start_date, 'End_Date': end_date,
        'Close_max': max_close, 'Close_min': min_close, 'Last_close': last_close
    }])

# Wybór indeksu
comm_name = st.radio('', list(comm_dict.values()), horizontal=True)
comm_label = list(comm_dict.keys())[list(comm_dict.values()).index(comm_name)]
comm_df = get_data(comm_label)

# Styl boczny
st.markdown("""
    <style>
        [data-testid="stSidebarContent"] {
            background-color: #F6BE00;
            color: black;
        }
    </style>
""", unsafe_allow_html=True)

st.sidebar.subheader('Choose tech analyse tool')
show_avg = st.sidebar.checkbox('Show moving averages')
show_stoch = st.sidebar.checkbox('Show stochastic oscillator')
show_rsi = st.sidebar.checkbox('Show RSI')
show_candle = st.sidebar.checkbox('Show candlestick')
show_atr = st.sidebar.checkbox('Show ATR')

# Panel główny
st.subheader(f'Base quotations for → {comm_name}', divider='blue')
col1, col2 = st.columns([0.6, 0.4])

with col1:
    st.write('Main Metrics:')
    side_tab = describe_data(comm_df, comm_name)
    st.markdown(side_tab.to_html(escape=False, index=False), unsafe_allow_html=True)

with col2:
    max_slider = len(comm_df)
    slider_val = st.slider('How long prices history you need?', 1, max_slider, 200)
    df_window = comm_df.iloc[-slider_val:]

# Wykres bazowy
fig = px.line(df_window, x='Date', y='Close', title="", width=1100, height=600)

if show_avg:
    short = st.sidebar.number_input("Short-term average (days)", value=5)
    long = st.sidebar.number_input("Long-term average (days)", value=15)
    df_window['Short_SMA'] = df_window['Close'].rolling(window=short).mean()
    df_window['Long_SMA'] = df_window['Close'].rolling(window=long).mean()
    fig.add_trace(go.Scatter(x=df_window['Date'], y=df_window['Short_SMA'], name='Short_SMA', line=dict(dash='dot')))
    fig.add_trace(go.Scatter(x=df_window['Date'], y=df_window['Long_SMA'], name='Long_SMA', line=dict(dash='dot')))

if show_stoch:
    K = st.sidebar.number_input("Stochastic %K window", value=14)
    D = st.sidebar.number_input("Stochastic %D window", value=3)
    low_min = df_window['Low'].rolling(window=K).min()
    high_max = df_window['High'].rolling(window=K).max()
    df_window['%K'] = 100 * (df_window['Close'] - low_min) / (high_max - low_min)
    df_window['%D'] = df_window['%K'].rolling(window=D).mean()
    df_window['Buy'] = np.where((df_window['%K'] < 20) & (df_window['%K'] > df_window['%D']), df_window['Close'], np.nan)
    df_window['Sell'] = np.where((df_window['%K'] > 80) & (df_window['%K'] < df_window['%D']), df_window['Close'], np.nan)
    fig.add_trace(go.Scatter(x=df_window['Date'], y=df_window['Buy'], mode='markers', name='Buy', marker=dict(color='green', symbol='triangle-up')))
    fig.add_trace(go.Scatter(x=df_window['Date'], y=df_window['Sell'], mode='markers', name='Sell', marker=dict(color='red', symbol='triangle-down')))

if show_rsi:
    rsi_win = st.sidebar.slider("RSI window", 5, 30, 14)
    rsi = RSIIndicator(df_window['Close'], window=rsi_win)
    df_window['RSI'] = rsi.rsi()
    fig.add_trace(go.Bar(x=df_window['Date'], y=df_window['RSI'], name='RSI', yaxis='y2', marker_color='orange'))
    fig.update_layout(yaxis2=dict(title='RSI', overlaying='y', side='right'))

if show_candle:
    fig.add_trace(go.Candlestick(x=df_window['Date'], open=df_window['Open'], high=df_window['High'], 
                                 low=df_window['Low'], close=df_window['Close'], name='Candlestick'))

if show_atr:
    atr_window = st.sidebar.slider('ATR window', 5, 50, 14)
    atr = AverageTrueRange(high=df_window['High'], low=df_window['Low'], close=df_window['Close'], window=atr_window)
    df_window['ATR'] = atr.average_true_range()
    fig.add_trace(go.Bar(x=df_window['Date'], y=df_window['ATR'], name='ATR', yaxis='y2', marker_color='blue'))
    fig.update_layout(yaxis2=dict(title='ATR/RSI', overlaying='y', side='right'))

st.plotly_chart(fig, use_container_width=True)
st.sidebar.write('© Michał Leśniewski')
