import streamlit as st
import pandas as pd
from ta.momentum import RSIIndicator
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, date

# Ustawienia strony
st.set_page_config(layout="wide")
st.title('Global economy indicators tech analyse dashboard')

# Definicje i słowniki
today = date.today()
comm_dict = {'^GSPC': 'SP_500', '^DJI': 'DJI30', '^IXIC': 'NASDAQ', 
             '000001.SS': 'SSE Composite Index', '^HSI': 'HANG SENG INDEX', '^VIX': 'CBOE Volatility Index', 
             '^RUT': 'Russell 2000', '^BVSP': 'IBOVESPA', '^FTSE': 'FTSE 100', '^GDAXI': 'DAX PERFORMANCE-INDEX', 
             '^N100': 'Euronext 100 Index', '^N225': 'Nikkei 225','EURUSD=X': 'EUR_USD', 'EURCHF=X': 'EUR_CHF', 
             'CNY=X': 'USD/CNY', 'GBPUSD=X': 'USD_GBP', 'JPY=X': 'USD_JPY', 'EURPLN=X': 'EUR/PLN', 'PLN=X': 'PLN/USD',
             'RUB=X': 'USD/RUB', 'DX-Y.NYB': 'US Dollar Index', '^XDE': 'Euro Currency Index', '^XDN': 'Japanese Yen Currency Index', 
             '^XDA': 'Australian Dollar Currency Index','^XDB': 'British Pound Currency Index', '^FVX': '5_YB', '^TNX': '10_YB',
             '^TYX': '30_YB', 'CL=F': 'Crude_Oil', 'BZ=F': 'Brent_Oil', 'GC=F': 'Gold','HG=F': 'Copper', 'PL=F': 'Platinum', 
             'SI=F': 'Silver', 'NG=F': 'Natural Gas', 'ZR=F': 'Rice Futures', 'ZS=F': 'Soy Futures', 'BTC-USD': 'Bitcoin USD','ETH-USD': 'Ethereum USD'}

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
    close_max = "{:.2f}".format(comm_entry['Close'].max())
    close_min = "{:.2f}".format(comm_entry['Close'].min())
    last_close = "{:.2f}".format(comm_entry['Close'].iloc[-1])
    v = (comm, sh, start_date, end_date, close_max, close_min, last_close)
    shape_test.append(v)
    Tab_length = pd.DataFrame(shape_test, columns=['Name', 'Rows', 'Start_Date', 'End_Date', 'Close_max', 'Close_min', 'Last_close'])
    Tab_his = Tab_length[['Start_Date', 'End_Date', 'Close_max', 'Close_min', 'Last_close']]
    Tab_his['Start_Date'] = Tab_his['Start_Date'].dt.strftime('%Y-%m-%d')
    Tab_his['End_Date'] = Tab_his['End_Date'].dt.strftime('%Y-%m-%d')
    return Tab_his

comm = st.radio('', list(comm_dict.values()), horizontal=True)
comm_f(comm)

# Styl zakładki bocznej
st.html("""<style>[data-testid="stSidebarContent"] {color: black; background-color: #F6BE00} </style>""")
st.sidebar.subheader('Choose tech analyse tool') #('Indexies, Currencies, Bonds, Commodities & Crypto', divider="grey")
checkbox_value1 = st.sidebar.checkbox('Do you want to see short and long term averages ?', key="<aver1>")
checkbox_value2 = st.sidebar.checkbox('Do you want to see Stochastic oscillator signals ?', key="<aver2>")
checkbox_value_rsi = st.sidebar.checkbox('Show Relative Strength Index (RSI)', key="<rsi>")
#comm = st.sidebar.radio('', list(comm_dict.values()))
#comm_f(comm)
st.sidebar.write('© Michał Leśniewski')

# Deskryptor desktopu
st.subheader(f'Base quotations for -> {comm}', divider='blue')
col1, col2 = st.columns([0.5, 0.5])
with col1:
    side_tab = pd.DataFrame(comm_data(comm))
    st.write('Main Metrics:')
    st.markdown(side_tab.to_html(escape=False, index=False), unsafe_allow_html=True)
    #checkbox_value1 = st.checkbox('Do you want to see short and long term averages ?', key="<aver1>")
    #checkbox_value2 = st.checkbox('Do you want to see Stochastic oscillator signals ?', key="<aver2>")
    
with col2:
    xy = (list(comm_entry.index)[-1])
    st.write('\n')
    entry_p = st.slider('How long prices history you need?', 1, xy, 200, key="<commodities>")
    
comm_entry_XDays = comm_entry.iloc[xy - entry_p:xy]
# Base Chart
fig_base = px.line(comm_entry_XDays, x='Date', y=['Close'], color_discrete_map={'Close':'black'}, width=1000, height=500)  

if checkbox_value1:
    st.subheader(f'{comm} Short and long term averages', divider='red')
    col3, col4, _ = st.columns([0.3, 0.3, 0.4])
    with col3:
        nums = st.number_input('Enter the number of days for short average', value=5, key="<m30>")
    with col4:
        numl = st.number_input('Enter the number of days for long average', value=15, key="<m35>")
    
    comm_entry_XDays['Short_SMA'] = comm_entry_XDays['Close'].rolling(window=nums).mean()
    comm_entry_XDays['Long_SMA'] = comm_entry_XDays['Close'].rolling(window=numl).mean()
    comm_entry_XDays['Buy_Signal'] = (comm_entry_XDays['Short_SMA'] > comm_entry_XDays['Long_SMA']).astype(int).diff()
    comm_entry_XDays['Sell_Signal'] = (comm_entry_XDays['Short_SMA'] < comm_entry_XDays['Long_SMA']).astype(int).diff()
    
    fig_base.add_trace(go.Scatter(x=comm_entry_XDays['Date'], y=comm_entry_XDays['Short_SMA'],
                             mode='lines', name='Short_SMA', line=dict(color='#00873E', dash='dot')))
    fig_base.add_trace(go.Scatter(x=comm_entry_XDays['Date'], y=comm_entry_XDays['Long_SMA'],
                             mode='lines', name='Long_SMA', line=dict(color='#A60A3D', dash='dot')))
    fig_base.add_trace(go.Scatter(x=comm_entry_XDays[comm_entry_XDays['Buy_Signal'] == 1].Date, 
                                  y=comm_entry_XDays[comm_entry_XDays['Buy_Signal'] == 1]['Short_SMA'], 
                              name='Buy_Signal', mode='markers', marker=dict(color='green', size=12, symbol='triangle-up')))
    fig_base.add_trace(go.Scatter(x=comm_entry_XDays[comm_entry_XDays['Sell_Signal'] == 1].Date, 
                                  y=comm_entry_XDays[comm_entry_XDays['Sell_Signal'] == 1]['Short_SMA'], 
                              name='Sell_Signal', mode='markers', marker=dict(color='red', size=12, symbol='triangle-down')))
    
if checkbox_value2:
    st.subheader(f'{comm} Stochastic oscillator signals', divider='red')
    col5, col6, _ = st.columns([0.3, 0.3, 0.4])
    with col5:
        K_num = st.number_input('Enter the number of days for %K parameter',value=10, key = "<k14>")
    with col6:
        D_num = st.number_input('Enter the number of days for %D parameter',value=10, key = "<d14>")

    low_min  = comm_entry_XDays['Low'].rolling(window = K_num).min()
    high_max = comm_entry_XDays['High'].rolling(window = D_num).max()
    comm_entry_XDays['%K'] = (100*(comm_entry_XDays['Close'] - low_min) / (high_max - low_min)).fillna(0)
    comm_entry_XDays['%D'] = comm_entry_XDays['%K'].rolling(window = 3).mean()

    # Generowanie sygnałów kupna/sprzedaży
    comm_entry_XDays['Buy_Signal'] = np.where((comm_entry_XDays['%K'] < 20) & (comm_entry_XDays['%K'] > comm_entry_XDays['%D']), 
                                              comm_entry_XDays['Close'], np.nan)
    comm_entry_XDays['Sell_Signal'] = np.where((comm_entry_XDays['%K'] > 80) & (comm_entry_XDays['%K'] < comm_entry_XDays['%D']),
                                               comm_entry_XDays['Close'], np.nan)
    fig_base.add_trace(go.Scatter(x=comm_entry_XDays['Date'], y=comm_entry_XDays['Buy_Signal'], mode='markers', name='Buy Signal', 
                                  marker=dict(color='#FEDD00', size=12, symbol='triangle-up')))
    fig_base.add_trace(go.Scatter(x=comm_entry_XDays['Date'], y=comm_entry_XDays['Sell_Signal'], mode='markers', name='Sell Signal', 
                              marker=dict(color='#C724B1', size=12, symbol='triangle-down')))

if checkbox_value_rsi:
    st.subheader(f'{comm} Relative Strength Index (RSI)', divider='red')
    col7, _ = st.columns([0.3, 0.6])
    with col7:
      rsi_entry = st.slider('How big window you need ?', 14, 30, 14, key="<rsi_window>")
    
    rsi = RSIIndicator(close=comm_entry_XDays['Close'], window = rsi_entry)
    comm_entry_XDays['RSI'] = rsi.rsi()
    fig_base.add_trace(go.Bar(x=comm_entry_XDays['Date'], y= comm_entry_XDays['RSI'], name='RSI', marker_color='rgba( 0, 135, 62, 0.5)', yaxis='y2'))  # Zmiana koloru na półprzezroczysty
    fig_base.update_layout(yaxis2=dict(title='RSI', overlaying='y', side='right'), legend=dict( x=1.1, y=1 ), width=1000, height=500) # Pozycja legendy, aby przesunąć ją w prawo
    
st.plotly_chart(fig_base, use_container_width=True)
