#!/usr/bin/env python
# coding: utf-8

# In[2]:


import streamlit as st
import pandas as pd


# In[12]:


acoes_completo = pd.read_csv('acoes.csv', sep=";")
acoes = list(acoes_completo['Codigo'].unique())

st.title('Análise dados da Bolsa')

st.sidebar.multiselect('Selecione uma ou mais ações:', acoes)

st.sidebar.date_input('Selecione a data inicial:')

st.sidebar.slider('Selecione o intervalo da variação:', -15.0, 15.0, [-9.7, -0.9])

st.text('teste')


# In[ ]:





# In[ ]:




