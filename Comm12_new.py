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

# Pobieranie danych
def comm_f(comm):
    global comm_entry
    for label, name in comm_dict.items():
        if name == comm:
            df_c = pd.DataFrame(yf.download(f'{label}', start='2000-09-01', end=today, interval='1d'))
            comm_entry = df_c.reset_index()
            return comm_entry

def comm_data(comm):
    global Tab_his
    shape_test = []
    sh = comm_entry.shape[0]
    start_date = comm_entry.Date.min()
    end_date = comm_entry.Date.max()

    # Pobranie maksymalnej, minimalnej i ostatniej wartości jako liczby
    max_close_value = comm_entry['Close'].max() #.iloc[0]
    min_close_value = comm_entry['Close'].min() #.iloc[0]
    last_close_value = comm_entry['Close'].iloc[-1] #.iloc[0]

    # Sprawdzenie braków danych i formatowanie wartości
    close_max = "{:.2f}".format(float(max_close_value)) if pd.notna(max_close_value) else "NaN"
    close_min = "{:.2f}".format(float(min_close_value)) if pd.notna(min_close_value) else "NaN"
    last_close = "{:.2f}".format(float(last_close_value)) if pd.notna(last_close_value) else "NaN"
  
    v = (comm, sh, start_date, end_date, close_max, close_min, last_close)
    shape_test.append(v)
    Tab_length = pd.DataFrame(shape_test, columns=['Name', 'Rows', 'Start_Date', 'End_Date', 'Close_max', 'Close_min', 'Last_close'])
    Tab_his = Tab_length[['Start_Date', 'End_Date', 'Close_max', 'Close_min', 'Last_close']]
    Tab_his['Start_Date'] = Tab_his['Start_Date'].dt.strftime('%Y-%m-%d')
    Tab_his['End_Date'] = Tab_his['End_Date'].dt.strftime('%Y-%m-%d')
    return Tab_his

#comm = st.radio('', list(comm_dict.values()), horizontal=True)
#comm_f(comm)

# Styl zakładki bocznej
st.html("""<style>[data-testid="stSidebarContent"] {color: black; background-color: #F6BE00} </style>""")
st.sidebar.subheader('Choose tech analyse tool') #('Indexies, Currencies, Bonds, Commodities & Crypto', divider="red")
checkbox_value1 = st.sidebar.checkbox('Do you want to see short and long term averages ?', key="<aver1>")
checkbox_value2 = st.sidebar.checkbox('Do you want to see Stochastic oscillator signals ?', key="<aver2>")
checkbox_value_rsi = st.sidebar.checkbox('Show Relative Strength Index (RSI)', key="<rsi>")
show_candlestick = st.sidebar.checkbox('Show Candlestick Chart', value=False, key="<candlestick>")
show_atr = st.sidebar.checkbox('Show Average True Range (ATR)', value=False, key="<atr>")
comm = st.sidebar.radio('', list(comm_dict.values()))
comm_f(comm)

# Deskryptor desktopu
st.subheader(f'Base quotations for -> {comm}', divider='blue')
col1, col2 = st.columns([0.6, 0.4])
with col1:
    side_tab = pd.DataFrame(comm_data(comm))
    st.write('Main Metrics:')
    st.markdown(side_tab.to_html(escape=False, index=False), unsafe_allow_html=True)
    #checkbox_value1 = st.checkbox('Do you want to see short and long term averages ?', key="<aver1>")
    #checkbox_value2 = st.checkbox('Do you want to see Stochastic oscillator signals ?', key="<aver2>")
    
with col2:
    #xy = (list(comm_entry.index)[-1])
    #st.write('\n')
    #entry_p = st.slider('How long prices history you need?', 1, xy, 200, key="<commodities>")

    xy = comm_entry.shape[0]
    entry_p = st.slider('How long prices history you need?', 1, xy, 200, key="<commodities>")
       
comm_entry_XDays = comm_entry.iloc[xy - entry_p:xy]
# Base Chart
fig_base = px.line(comm_entry_XDays, x='Date', y=['Close'], color_discrete_map={'Close':'black'}, width=1100, height=600)  
