#!/usr/bin/env python
# coding: utf-8

# In[55]:


import streamlit as st
import pandas as pd
import pandas_datareader as pdr
from pandas_datareader import data as web
import pandas as pd
import datetime
import itertools
from datetime import date, timedelta, datetime, time


# In[66]:


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

dataInicialExibida = date.today() - timedelta(60)

dataInicial = st.sidebar.date_input('Selecione a data inicial:', dataInicialExibida)

variacao = st.sidebar.slider('Selecione o intervalo da variação:', -15.0, 15.0, [-9.7, -0.9])

variacao_min = variacao[0]
variacao_max = variacao[1]

botao = st.sidebar.button('Calcular')

if(datetime.today().time().hour > 18):
    
    dataFinal = date.today()
    
else:
    
    if(datetime.today().time().hour > 18 and datetime.today().time().minutes >= 30):
        
        dataFinal = date.today()
    
    else:
    
        dataFinal = date.today() - timedelta(1)

#Cria as abas
qtdAbas = 0

if botao:   
    
    if(len(acoes_selecionadas)> 0):
        
        if(dataInicial<date.today()):
    
            for acao in acoes_selecionadas:

                st.session_state['tabs'].append(acao)    

            tabs = st.tabs(st.session_state['tabs'])

            for acao in acoes_selecionadas:

                codigoYahoo = pd.DataFrame(acoes_completo.loc[(acoes_completo['Codigo'] == acao), 'Codigo_Yahoo'])

                codigoYahoo = codigoYahoo.iloc[0, 0]

                #dadosAcao = yahooFinance.Ticker(codigoYahoo)

                with tabs[qtdAbas+1]:

                    dados_acao_tabela = pd.DataFrame(web.DataReader(codigoYahoo, data_source='yahoo', start=dataInicial, end = dataFinal))
                    dados_acao_tabela = dados_acao_tabela.reset_index()
                    
                    dados_acao_tabela.rename(columns={'Date': 'Data'}, inplace = True)
                    dados_acao_tabela.rename(columns={'Open': 'Abertura'}, inplace = True)
                    dados_acao_tabela.rename(columns={'High': 'Máxima'}, inplace = True)
                    dados_acao_tabela.rename(columns={'Low': 'Mínima'}, inplace = True)
                    dados_acao_tabela.rename(columns={'Close': 'Fechamento'}, inplace = True)
                    dados_acao_tabela.rename(columns={'Adj Close': 'Fech. Ajustado'}, inplace = True)
                    
                    dados_acao_tabela['Data'] = dados_acao_tabela['Data'].dt.strftime('%d/%m/%Y')
                    
                    dados_acao_tabela = dados_acao_tabela[['Data', 'Abertura', 'Mínima', 'Máxima', 'Fechamento', 'Fech. Ajustado']]
                    
                    st.dataframe(dados_acao_tabela)
                    qtdAbas = qtdAbas + 1
                    
        else:
            
            st.sidebar.error("Selecione uma data menor do que a data atual!")
        
    else:
        
        st.sidebar.error("Selecione pelo menos uma ação!")


# In[ ]:




