import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import main
import json
st.set_page_config(layout="wide")


with st.sidebar:
    sidebar = st.selectbox("Select operation", ["Simulations", "Simulations vizualizations"])

df = pd.read_csv('csv/tickers.csv')

if sidebar == "Simulations":
    edited_df = st.data_editor(df)
    if st.button('Save changed df'):
        edited_df.to_csv('csv/tickers.csv', index=False)

    option = st.selectbox("Select ticker for simulation", df["ticker"].to_list())
    k = st.number_input("Number of symulations", 1, 900000000000, 1000, step=1000)
    if st.button('Start single simulation'):
        denst = main.get_valuationDistribution(df, [option], 10, k)
        st.write(denst)
        fig = px.bar(x = denst[1], y = denst[0])
        st.plotly_chart(fig)
        
    if st.button('Start all simulations'):
        denst = main.get_valuationDistribution(df, df["ticker"].to_list(), 10, k)

if sidebar == "Simulations vizualizations":
    f = open('valJSON.json')
    data = json.loads(json.loads(f.read()))
    for ticker in data.keys():
        fig = px.bar(x =data[ticker]["x"], y = data[ticker]["y"], title=ticker)
        st.plotly_chart(fig)