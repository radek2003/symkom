import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import main
st.set_page_config(layout="wide")


df = pd.read_csv('csv/tickers.csv')
edited_df = st.data_editor(df)
if st.button('Save changed df'):
    edited_df.to_csv('csv/tickers.csv', index=False)

option = st.selectbox("Select ticker for symulation", df["ticker"].to_list())
k = st.number_input("Number of symulations", 1, 900000000000, 1000, step=1000)
if st.button('Start symulation'):
    denst = main.get_valuationDistribution(df, [option], 10, k)
    st.write(denst)
    fig = px.bar(x = denst[1], y = denst[0])
    st.plotly_chart(fig)