#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
import yfinance as yahooFinance
import datetime
import itertools
from datetime import date, timedelta


# In[130]:


acoes_completo = pd.read_csv('acoes.csv', sep=";")
acoes_lista = list(acoes_completo['Codigo'])

st.set_page_config(initial_sidebar_state="expanded")

if 'tabs' not in st.session_state:    
    st.session_state['tabs'] = ['Consolidado']
else:
    del st.session_state['tabs']
    st.session_state['tabs'] = ['Consolidado']

st.title('Análise dados da Bolsa')

acoes_selecionadas = list(st.sidebar.multiselect('Selecione uma ou mais ações:', acoes_lista))

dataInicial = st.sidebar.date_input('Selecione a data inicial:')

variacao = st.sidebar.slider('Selecione o intervalo da variação:', -15.0, 15.0, [-9.7, -0.9])

variacao_min = variacao[0]
variacao_max = variacao[1]

botao = st.sidebar.button('Calcular')

dataFinal = date.today() - timedelta(1)

#Cria as abas
qtdAbas = 0

if botao:   
    
    for acao in acoes_selecionadas:
        
        #parametros_aba = st.text_input(acao, acao)  
        
        st.session_state['tabs'].append(acao)    
        
    tabs = st.tabs(st.session_state['tabs'])
    
    for acao in acoes_selecionadas:
        
        codigoYahoo = pd.DataFrame(acoes_completo.loc[(acoes_completo['Codigo'] == acao), 'Codigo_Yahoo'])
        
        codigoYahoo = str(codigoYahoo['Codigo_Yahoo'])
     
        dadosAcao = yahooFinance.Ticker(codigoYahoo)
        
        with tabs[qtdAbas+1]:
            
            dados_acao_tabela = pd.DataFrame(dadosAcao.history(start=dataInicial, end=dataFinal))
            #dados_acao_tabela.rename(columns={'Date': 'Data'}, inplace = True)
            
            st.text(dados_acao_tabela)
            qtdAbas = qtdAbas + 1
        
    


# In[ ]:





# In[ ]:




