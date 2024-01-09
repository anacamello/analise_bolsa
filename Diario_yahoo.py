#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, ColumnsAutoSizeMode
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import datetime as dt
from datetime import date
from datetime import timedelta
from datetime import datetime
import pytz
import itertools
from decimal import Decimal
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier 
from yahooquery import Ticker
from binance.client import Client
from time import sleep
import matplotlib.pyplot as plt


# In[4]:


def cria_tabela_resumo_acao():
    
    #Cria a tabela de resumo da ação
    tabela_resumo_acao = pd.DataFrame()
    tabela_resumo_acao.insert(0, "Variação", 0, allow_duplicates = False)
    tabela_resumo_acao.insert(1, "Resultado", 0, allow_duplicates = False)
    tabela_resumo_acao.insert(2, "Qtd. Trades", 0, allow_duplicates = False)
    tabela_resumo_acao.insert(3, "Qtd. Trades Positivos", 0, allow_duplicates = False)
    tabela_resumo_acao.insert(4, "Qtd. Trades Negativos", 0, allow_duplicates = False)
    tabela_resumo_acao.insert(5, "Média Trades Positivos", 0, allow_duplicates = False)
    tabela_resumo_acao.insert(6, "Média Trades Negativos", 0, allow_duplicates = False)
    tabela_resumo_acao.insert(7, "Maior Trade Positivo", 0, allow_duplicates = False)
    tabela_resumo_acao.insert(8, "Menor Trade Positivo", 0, allow_duplicates = False)
    tabela_resumo_acao.insert(9, "Maior Trade Negativo", 0, allow_duplicates = False)
    tabela_resumo_acao.insert(10, "Menor Trade Negativo", 0, allow_duplicates = False)
    tabela_resumo_acao.insert(11, "Ganho", 0, allow_duplicates = False)
    tabela_resumo_acao.insert(12, "Ativo", 0, allow_duplicates = False)
    
    return tabela_resumo_acao


# In[5]:


def cria_dados_acao_tabela (codigo_acao, dataInicial, dataFinal, tipoAtivo):
    
    if(tipoAtivo == "cripto"):
        
        client = Client('LVPuYJqB9rPdBNfMwjJrfYjJaDaO6mkfKTEC4xKeisrVDVNQwcd5kdnhXlLFr4jf', 'NP08r4Sff9vQfkdnO4MHa6SwOf8VWvJwBEidPor58tDmRP7yLBTJ46qNwlykqCky')
        timeframe="1d"
        
        dados_acao_tabela = pd.DataFrame(client.get_historical_klines(codigo_acao, timeframe, dataInicial.strftime("%Y.%m.%d"), dataFinal.strftime("%Y.%m.%d")))
        
        dados_acao_tabela = dados_acao_tabela.iloc[:,:6]
        dados_acao_tabela.columns=["Data","Abertura","Máxima","Mínima","Fechamento","Volume"]
        
        dados_acao_tabela = dados_acao_tabela.set_index("Data")
        dados_acao_tabela.index = pd.to_datetime(dados_acao_tabela.index ,unit="ms")
        dados_acao_tabela = dados_acao_tabela.astype("float")
        
        dados_acao_tabela.reset_index(inplace=True)
        
    else:
        
        codigo_yahoo = Ticker(codigo_acao + ".SA")
        
        dataInicial_truncada = dt.date(dataInicial.year, dataInicial.month, dataInicial.day)
        dataInicial_truncada = dataInicial_truncada.strftime("%Y-%m-%d")
        
        dataFinal_truncada = dt.date(dataFinal.year, dataFinal.month, dataFinal.day)
        dataFinal_truncada = dataFinal_truncada.strftime("%Y-%m-%d")

        dados_acao_tabela = codigo_yahoo.history(start=dataInicial_truncada, end=dataFinal_truncada)
        
        dados_acao_tabela = dados_acao_tabela.reset_index()

        if len(dados_acao_tabela) > 0:

            dados_acao_tabela = dados_acao_tabela.reset_index()

            #dados_acao_tabela['date']=pd.to_datetime(dados_acao_tabela['date'], unit='s')
            dados_acao_tabela.rename(columns={'date': 'Data'}, inplace = True)
            dados_acao_tabela.rename(columns={'open': 'Abertura'}, inplace = True)
            dados_acao_tabela.rename(columns={'high': 'Máxima'}, inplace = True)
            dados_acao_tabela.rename(columns={'low': 'Mínima'}, inplace = True)
            dados_acao_tabela.rename(columns={'adjclose': 'Fechamento'}, inplace = True)
            dados_acao_tabela.rename(columns={'volume': 'Volume'}, inplace = True)
            
            dados_acao_tabela.drop(["symbol", "close"], axis = 1, inplace = True)

        else:

            st.sidebar.error("Erro ao carregar dados da ação: " + codigo_acao)
    
    if len(dados_acao_tabela) > 0:
        
        #dados_acao_tabela['Data'] = dados_acao_tabela['Data'].dt.strftime('%d/%m/%Y')
        dados_acao_tabela.insert(6, "Mínima %", 0, allow_duplicates = False)
        dados_acao_tabela.insert(7, "Máxima %", 0, allow_duplicates = False)
        dados_acao_tabela.insert(8, "Fechamento %", 0, allow_duplicates = False)
        dados_acao_tabela.insert(9, "Ativo", 0, allow_duplicates = False)
        
    return dados_acao_tabela


# In[6]:


def formatar_tabela_resumo_acao(tabela_resumo_acao):

    #Formata a tabela_resumo_acao

    tabela_resumo_acao['Variação'] = pd.Series(["{0:.2f}%".format(val) for val in tabela_resumo_acao['Variação']], index = tabela_resumo_acao.index)
    tabela_resumo_acao['Variação'] = tabela_resumo_acao['Variação'].astype(str)
    tabela_resumo_acao['Variação'] = tabela_resumo_acao['Variação'].str.replace('.', ',')

    tabela_resumo_acao['Resultado'] = pd.Series(["{0:.2f}%".format(val) for val in tabela_resumo_acao['Resultado']], index = tabela_resumo_acao.index)
    tabela_resumo_acao['Resultado'] = tabela_resumo_acao['Resultado'].astype(str)
    tabela_resumo_acao['Resultado'] = tabela_resumo_acao['Resultado'].str.replace('.', ',')

    tabela_resumo_acao['Média Trades Positivos'] = pd.Series(["{0:.2f}%".format(val) for val in tabela_resumo_acao['Média Trades Positivos']], index = tabela_resumo_acao.index)
    tabela_resumo_acao['Média Trades Positivos'] = tabela_resumo_acao['Média Trades Positivos'].astype(str)
    tabela_resumo_acao['Média Trades Positivos'] = tabela_resumo_acao['Média Trades Positivos'].str.replace('.', ',')

    tabela_resumo_acao['Maior Trade Positivo'] = pd.Series(["{0:.2f}%".format(val) for val in tabela_resumo_acao['Maior Trade Positivo']], index = tabela_resumo_acao.index)
    tabela_resumo_acao['Maior Trade Positivo'] = tabela_resumo_acao['Maior Trade Positivo'].astype(str)
    tabela_resumo_acao['Maior Trade Positivo'] = tabela_resumo_acao['Maior Trade Positivo'].str.replace('.', ',')

    tabela_resumo_acao['Menor Trade Positivo'] = pd.Series(["{0:.2f}%".format(val) for val in tabela_resumo_acao['Menor Trade Positivo']], index = tabela_resumo_acao.index)
    tabela_resumo_acao['Menor Trade Positivo'] = tabela_resumo_acao['Menor Trade Positivo'].astype(str)
    tabela_resumo_acao['Menor Trade Positivo'] = tabela_resumo_acao['Menor Trade Positivo'].str.replace('.', ',')
    
    tabela_resumo_acao['Média Trades Negativos'] = pd.Series(["{0:.2f}%".format(val) for val in tabela_resumo_acao['Média Trades Negativos']], index = tabela_resumo_acao.index)
    tabela_resumo_acao['Média Trades Negativos'] = tabela_resumo_acao['Média Trades Negativos'].astype(str)
    tabela_resumo_acao['Média Trades Negativos'] = tabela_resumo_acao['Média Trades Negativos'].str.replace('.', ',')

    tabela_resumo_acao['Maior Trade Negativo'] = pd.Series(["{0:.2f}%".format(val) for val in tabela_resumo_acao['Maior Trade Negativo']], index = tabela_resumo_acao.index)
    tabela_resumo_acao['Maior Trade Negativo'] = tabela_resumo_acao['Maior Trade Negativo'].astype(str)
    tabela_resumo_acao['Maior Trade Negativo'] = tabela_resumo_acao['Maior Trade Negativo'].str.replace('.', ',')

    tabela_resumo_acao['Menor Trade Negativo'] = pd.Series(["{0:.2f}%".format(val) for val in tabela_resumo_acao['Menor Trade Negativo']], index = tabela_resumo_acao.index)
    tabela_resumo_acao['Menor Trade Negativo'] = tabela_resumo_acao['Menor Trade Negativo'].astype(str)
    tabela_resumo_acao['Menor Trade Negativo'] = tabela_resumo_acao['Menor Trade Negativo'].str.replace('.', ',')


    tabela_resumo_acao['Ganho'] = pd.Series(["{0:.2f}%".format(val*100) for val in tabela_resumo_acao['Ganho']], index = tabela_resumo_acao.index)
    tabela_resumo_acao['Ganho'] = tabela_resumo_acao['Ganho'].astype(str)
    tabela_resumo_acao['Ganho'] = tabela_resumo_acao['Ganho'].str.replace('.', ',')

    tabela_resumo_acao = tabela_resumo_acao.set_index('Variação')
    tabela_resumo_acao = tabela_resumo_acao.T

    tabela_resumo_acao = tabela_resumo_acao.style.applymap(cor_ganho)
    
    return tabela_resumo_acao


# In[7]:


def formata_dados_acao_tabela_compra(dados_acao_tabela):

    #formata dados_acao_tabela

    dados_acao_tabela['Abertura'] = pd.Series(["R$ {0: _.2f}".format(val) for val in dados_acao_tabela['Abertura']], index = dados_acao_tabela.index)
    dados_acao_tabela['Abertura'] = dados_acao_tabela['Abertura'].astype(str)
    dados_acao_tabela['Abertura'] = dados_acao_tabela['Abertura'].str.replace('.', ',')
    dados_acao_tabela['Abertura'] = dados_acao_tabela['Abertura'].replace('_', '.')

    dados_acao_tabela['Máxima'] = pd.Series(["R$ {0: _.2f}".format(val) for val in dados_acao_tabela['Máxima']], index = dados_acao_tabela.index)
    dados_acao_tabela['Máxima'] = dados_acao_tabela['Máxima'].astype(str)
    dados_acao_tabela['Máxima'] = dados_acao_tabela['Máxima'].str.replace('.', ',')
    dados_acao_tabela['Máxima'] = dados_acao_tabela['Máxima'].str.replace('_', '.')

    dados_acao_tabela['Mínima'] = pd.Series(["R$ {0: _.2f}".format(val) for val in dados_acao_tabela['Mínima']], index = dados_acao_tabela.index)
    dados_acao_tabela['Mínima'] = dados_acao_tabela['Mínima'].astype(str)
    dados_acao_tabela['Mínima'] = dados_acao_tabela['Mínima'].str.replace('.', ',')
    dados_acao_tabela['Mínima'] = dados_acao_tabela['Mínima'].replace('_', '.')

    dados_acao_tabela['Fechamento'] = pd.Series(["R$ {0: _.2f}".format(val) for val in dados_acao_tabela['Fechamento']], index = dados_acao_tabela.index)
    dados_acao_tabela['Fechamento'] = dados_acao_tabela['Fechamento'].astype(str)
    dados_acao_tabela['Fechamento'] = dados_acao_tabela['Fechamento'].str.replace('.', ',')
    dados_acao_tabela['Fechamento'] = dados_acao_tabela['Fechamento'].str.replace('_', '.')

    dados_acao_tabela['Volume'] = pd.Series(["R$ {0: _.2f}".format(val) for val in dados_acao_tabela['Volume']], index = dados_acao_tabela.index)
    dados_acao_tabela['Volume'] = dados_acao_tabela['Volume'].astype(str)
    dados_acao_tabela['Volume'] = dados_acao_tabela['Volume'].str.replace('.', ',')
    dados_acao_tabela['Volume'] = dados_acao_tabela['Volume'].str.replace('_', '.')

    dados_acao_tabela['Mínima %'] = pd.Series(["{0:.2f}%".format(val) for val in dados_acao_tabela['Mínima %']], index = dados_acao_tabela.index)
    dados_acao_tabela['Mínima %'] = dados_acao_tabela['Mínima %'].astype(str)
    dados_acao_tabela['Mínima %'] = dados_acao_tabela['Mínima %'].str.replace('.', ',')

    dados_acao_tabela['Fechamento %'] = pd.Series(["{0:.2f}%".format(val) for val in dados_acao_tabela['Fechamento %']], index = dados_acao_tabela.index)
    dados_acao_tabela['Fechamento %'] = dados_acao_tabela['Fechamento %'].astype(str)
    dados_acao_tabela['Fechamento %'] = dados_acao_tabela['Fechamento %'].str.replace('.', ',')
    
    return dados_acao_tabela


# In[ ]:


def formata_dados_acao_tabela_venda(dados_acao_tabela):

    #formata dados_acao_tabela

    dados_acao_tabela['Abertura'] = pd.Series(["R$ {0: _.2f}".format(val) for val in dados_acao_tabela['Abertura']], index = dados_acao_tabela.index)
    dados_acao_tabela['Abertura'] = dados_acao_tabela['Abertura'].astype(str)
    dados_acao_tabela['Abertura'] = dados_acao_tabela['Abertura'].str.replace('.', ',')
    dados_acao_tabela['Abertura'] = dados_acao_tabela['Abertura'].replace('_', '.')

    dados_acao_tabela['Máxima'] = pd.Series(["R$ {0: _.2f}".format(val) for val in dados_acao_tabela['Máxima']], index = dados_acao_tabela.index)
    dados_acao_tabela['Máxima'] = dados_acao_tabela['Máxima'].astype(str)
    dados_acao_tabela['Máxima'] = dados_acao_tabela['Máxima'].str.replace('.', ',')
    dados_acao_tabela['Máxima'] = dados_acao_tabela['Máxima'].str.replace('_', '.')

    dados_acao_tabela['Mínima'] = pd.Series(["R$ {0: _.2f}".format(val) for val in dados_acao_tabela['Mínima']], index = dados_acao_tabela.index)
    dados_acao_tabela['Mínima'] = dados_acao_tabela['Mínima'].astype(str)
    dados_acao_tabela['Mínima'] = dados_acao_tabela['Mínima'].str.replace('.', ',')
    dados_acao_tabela['Mínima'] = dados_acao_tabela['Mínima'].replace('_', '.')

    dados_acao_tabela['Fechamento'] = pd.Series(["R$ {0: _.2f}".format(val) for val in dados_acao_tabela['Fechamento']], index = dados_acao_tabela.index)
    dados_acao_tabela['Fechamento'] = dados_acao_tabela['Fechamento'].astype(str)
    dados_acao_tabela['Fechamento'] = dados_acao_tabela['Fechamento'].str.replace('.', ',')
    dados_acao_tabela['Fechamento'] = dados_acao_tabela['Fechamento'].str.replace('_', '.')

    dados_acao_tabela['Volume'] = pd.Series(["R$ {0: _.2f}".format(val) for val in dados_acao_tabela['Volume']], index = dados_acao_tabela.index)
    dados_acao_tabela['Volume'] = dados_acao_tabela['Volume'].astype(str)
    dados_acao_tabela['Volume'] = dados_acao_tabela['Volume'].str.replace('.', ',')
    dados_acao_tabela['Volume'] = dados_acao_tabela['Volume'].str.replace('_', '.')

    dados_acao_tabela['Máxima %'] = pd.Series(["{0:.2f}%".format(val) for val in dados_acao_tabela['Máxima %']], index = dados_acao_tabela.index)
    dados_acao_tabela['Máxima %'] = dados_acao_tabela['Máxima %'].astype(str)
    dados_acao_tabela['Máxima %'] = dados_acao_tabela['Máxima %'].str.replace('.', ',')

    dados_acao_tabela['Fechamento %'] = pd.Series(["{0:.2f}%".format(val) for val in dados_acao_tabela['Fechamento %']], index = dados_acao_tabela.index)
    dados_acao_tabela['Fechamento %'] = dados_acao_tabela['Fechamento %'].astype(str)
    dados_acao_tabela['Fechamento %'] = dados_acao_tabela['Fechamento %'].str.replace('.', ',')
    
    return dados_acao_tabela


# In[8]:


def formata_tabela_relatorio(tabela_relatorio):

    #Formata a tabela Relatório

    tabela_relatorio.sort_values(by=['Ganho', 'Média do Volume no Período'], inplace = True, ascending=False)
    tabela_relatorio = tabela_relatorio.reset_index(drop = True)

    tabela_relatorio['Variação'] = pd.Series(["{0:.2f}%".format(val) for val in tabela_relatorio['Variação']], index = tabela_relatorio.index)
    tabela_relatorio['Variação'] = tabela_relatorio['Variação'].astype(str)
    tabela_relatorio['Variação'] = tabela_relatorio['Variação'].str.replace('.', ',')

    tabela_relatorio['Ganho'] = pd.Series(["{0:.2f}%".format(val * 100) for val in tabela_relatorio['Ganho']], index = tabela_relatorio.index)
    tabela_relatorio['Ganho'] = tabela_relatorio['Ganho'].astype(str)
    tabela_relatorio['Ganho'] = tabela_relatorio['Ganho'].str.replace('.', ',')

    tabela_relatorio['Média dos Trades Positivos'] = pd.Series(["{0:.2f}%".format(val) for val in tabela_relatorio['Média dos Trades Positivos']], index = tabela_relatorio.index)
    tabela_relatorio['Média dos Trades Positivos'] = tabela_relatorio['Média dos Trades Positivos'].astype(str)
    tabela_relatorio['Média dos Trades Positivos'] = tabela_relatorio['Média dos Trades Positivos'].str.replace('.', ',')

    tabela_relatorio['Maior Trade Positivo'] = pd.Series(["{0:.2f}%".format(val) for val in tabela_relatorio['Maior Trade Positivo']], index = tabela_relatorio.index)
    tabela_relatorio['Maior Trade Positivo'] = tabela_relatorio['Maior Trade Positivo'].astype(str)
    tabela_relatorio['Maior Trade Positivo'] = tabela_relatorio['Maior Trade Positivo'].str.replace('.', ',')

    tabela_relatorio['Menor Trade Positivo'] = pd.Series(["{0:.2f}%".format(val) for val in tabela_relatorio['Menor Trade Positivo']], index = tabela_relatorio.index)
    tabela_relatorio['Menor Trade Positivo'] = tabela_relatorio['Menor Trade Positivo'].astype(str)
    tabela_relatorio['Menor Trade Positivo'] = tabela_relatorio['Menor Trade Positivo'].str.replace('.', ',')
    
    tabela_relatorio['Média dos Trades Negativos'] = pd.Series(["{0:.2f}%".format(val) for val in tabela_relatorio['Média dos Trades Negativos']], index = tabela_relatorio.index)
    tabela_relatorio['Média dos Trades Negativos'] = tabela_relatorio['Média dos Trades Negativos'].astype(str)
    tabela_relatorio['Média dos Trades Negativos'] = tabela_relatorio['Média dos Trades Negativos'].str.replace('.', ',')

    tabela_relatorio['Maior Trade Negativo'] = pd.Series(["{0:.2f}%".format(val) for val in tabela_relatorio['Maior Trade Negativo']], index = tabela_relatorio.index)
    tabela_relatorio['Maior Trade Negativo'] = tabela_relatorio['Maior Trade Negativo'].astype(str)
    tabela_relatorio['Maior Trade Negativo'] = tabela_relatorio['Maior Trade Negativo'].str.replace('.', ',')

    tabela_relatorio['Menor Trade Negativo'] = pd.Series(["{0:.2f}%".format(val) for val in tabela_relatorio['Menor Trade Negativo']], index = tabela_relatorio.index)
    tabela_relatorio['Menor Trade Negativo'] = tabela_relatorio['Menor Trade Negativo'].astype(str)
    tabela_relatorio['Menor Trade Negativo'] = tabela_relatorio['Menor Trade Negativo'].str.replace('.', ',')

    tabela_relatorio['Resultado'] = pd.Series(["{0:.2f}%".format(val) for val in tabela_relatorio['Resultado']], index = tabela_relatorio.index)
    tabela_relatorio['Resultado'] = tabela_relatorio['Resultado'].astype(str)
    tabela_relatorio['Resultado'] = tabela_relatorio['Resultado'].str.replace('.', ',')

    tabela_relatorio['Média do Volume no Período'] = pd.Series(["R$ {0:_.2f}".format(val) for val in tabela_relatorio['Média do Volume no Período']], index = tabela_relatorio.index)
    tabela_relatorio['Média do Volume no Período'] = tabela_relatorio['Média do Volume no Período'].astype(str)
    tabela_relatorio['Média do Volume no Período'] = tabela_relatorio['Média do Volume no Período'].str.replace('.', ',')
    tabela_relatorio['Média do Volume no Período'] = tabela_relatorio['Média do Volume no Período'].str.replace('_', '.')

    return tabela_relatorio


# In[ ]:


def cor_ganho(val):
        
        val = str(val)
        val = val.replace('%', '')
        val = val.replace(',', '.')
            
        cor_background = 'forestgreen' if float(val) > 75.00 else 'white'
        cor_letra = 'white' if float(val) > 75.00 else 'black'

        return f'background-color: {cor_background}; color:{cor_letra}'


# In[ ]:


def aggrid_selecao_unica(df: pd.DataFrame):
    
    options = GridOptionsBuilder.from_dataframe(
        df, enableRowGroup=True, enableValue=True, enablePivot=True
    )
    
    options.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=15)
    options.configure_auto_height(autoHeight = False)
    options.configure_side_bar()
    options.configure_default_column(groupable=True, value=True, sortable=True, filterable=True, resizable=True, enableRowGroup=True, aggFunc="sum", editable=False, wrapText=True, autoHeight=True)

    options.configure_selection("single", use_checkbox=True)
    selection = AgGrid(
        df,
        enable_enterprise_modules=True,
        gridOptions=options.build(),
        theme="streamlit",
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        allow_unsafe_jscode=True,
        reload_data=False, 
        use_checkbox=True,  
        header_checkbox= True, 
        groupSelectsChildren=True
    )
    
    return selection


# In[ ]:


def aggrid(df: pd.DataFrame):
    
    options = GridOptionsBuilder.from_dataframe(
        df, enableRowGroup=True, enableValue=True, enablePivot=True
    )
    
    options.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=15)
    options.configure_auto_height(autoHeight = False)
    options.configure_side_bar()
    options.configure_default_column(groupable=True, value=True, sortable=True, filterable=True, resizable=True, enableRowGroup=True, aggFunc="sum", editable=False, wrapText=True, autoHeight=True)

    options.configure_selection("multiple", use_checkbox=True)
    selection = AgGrid(
        df,
        enable_enterprise_modules=True,
        gridOptions=options.build(),
        theme="streamlit",
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        allow_unsafe_jscode=True,
        reload_data=False, 
        use_checkbox=True,  
        header_checkbox= True, 
        groupSelectsChildren=True
    )
    
    return selection


# In[ ]:


def aggrid_sem_selecao(df: pd.DataFrame):
    
    options = GridOptionsBuilder.from_dataframe(df, enableRowGroup=True, enableValue=True, enablePivot=True)
    
    options.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=15)
    options.configure_auto_height(autoHeight = False)
    options.configure_side_bar()
    options.configure_default_column(groupable=True, value=True, sortable=True, filterable=True, resizable=True, enableRowGroup=True, aggFunc="sum", editable=False, wrapText=True, autoHeight=True)
    options.configure_selection("single", use_checkbox=False)
    AgGrid(
        df,
        enable_enterprise_modules=True,
        gridOptions=options.build(),
        theme="streamlit",
        update_mode=GridUpdateMode.NO_UPDATE,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        allow_unsafe_jscode=True,
        reload_data=False, 
        use_checkbox=False,  
        header_checkbox= False, 
        groupSelectsChildren=True
    )


# In[ ]:


@st.cache_data
def calcula_fibonacci(dados_acao_tabela, ultima_data, acao, ultimoFechamentoAjustado):
    
    maior_valor = dados_acao_tabela['Fechamento'].max()
    menor_valor = dados_acao_tabela['Fechamento'].min()
    
    diferenca = maior_valor - menor_valor
    
    fib100 = round(maior_valor, 2)
    fib764 = round(menor_valor + (diferenca * 0.764), 2)
    fib618 = round(menor_valor + (diferenca * 0.618), 2)
    fib50 = round(menor_valor + (diferenca * 0.5), 2)
    fib382 = round(menor_valor + (diferenca * 0.382), 2)
    fib236 = round(menor_valor + (diferenca * 0.236), 2)
    fib0 = round(menor_valor, 2)
    
    fibonacci_acao = pd.DataFrame()
    fibonacci_acao.insert(0, "Ação", 0, allow_duplicates = False)
    fibonacci_acao.insert(1, "Data Referência", 0, allow_duplicates = False)
    fibonacci_acao.insert(2, "Último Fechamento", 0, allow_duplicates = False)
    fibonacci_acao.insert(3, "Fib 100", 0, allow_duplicates = False)
    fibonacci_acao.insert(4, "Dif Fib 100", 0, allow_duplicates = False)
    fibonacci_acao.insert(5, "Fib 76.4", 0, allow_duplicates = False)
    fibonacci_acao.insert(6, "Dif Fib 76.4", 0, allow_duplicates = False)
    fibonacci_acao.insert(7, "Fib 61.8", 0, allow_duplicates = False)
    fibonacci_acao.insert(8, "Dif Fib 61.8", 0, allow_duplicates = False)
    fibonacci_acao.insert(9, "Fib 50", 0, allow_duplicates = False)
    fibonacci_acao.insert(10, "Dif Fib 50", 0, allow_duplicates = False)
    fibonacci_acao.insert(11, "Fib 38.2", 0, allow_duplicates = False)
    fibonacci_acao.insert(12, "Dif Fib 38.2", 0, allow_duplicates = False)
    fibonacci_acao.insert(13, "Fib 23.6", 0, allow_duplicates = False)
    fibonacci_acao.insert(14, "Dif Fib 23.6", 0, allow_duplicates = False)
    fibonacci_acao.insert(15, "Fib 0", 0, allow_duplicates = False)
    fibonacci_acao.insert(16, "Dif Fib 0", 0, allow_duplicates = False)
    
    dif_fib_100 = np.round((1 - (ultimoFechamentoAjustado / fib100)) *100, 2)
    dif_fib_764 = np.round((1 - (ultimoFechamentoAjustado / fib764)) *100, 2)
    dif_fib_618 = np.round((1 - (ultimoFechamentoAjustado / fib618)) *100, 2)
    dif_fib_50 = np.round((1 - (ultimoFechamentoAjustado / fib50)) *100, 2)
    dif_fib_382 = np.round((1 - (ultimoFechamentoAjustado / fib382)) *100, 2)
    dif_fib_236 = np.round((1 - (ultimoFechamentoAjustado / fib236)) *100, 2)
    dif_fib_0 = np.round((1 - (ultimoFechamentoAjustado / fib0)) *100, 2)
    
    novo_registro = pd.DataFrame([{'Ação': acao, 'Data Referência': ultima_data, 'Último Fechamento': ultimoFechamentoAjustado, 'Fib 100': fib100, 'Dif Fib 100': dif_fib_100, 'Fib 76.4': fib764, 'Dif Fib 76.4': dif_fib_764,
                          'Fib 61.8': fib618, 'Dif Fib 61.8': dif_fib_618, 'Fib 50': fib50, 'Dif Fib 50': dif_fib_50, 'Fib 38.2': fib382, 'Dif Fib 38.2': dif_fib_382, 'Fib 23.6': fib236, 'Dif Fib 23.6': dif_fib_236,
                          'Fib 0': fib0, 'Dif Fib 0': dif_fib_0}])
    fibonacci_acao = pd.concat([novo_registro], ignore_index = True)
    
    return fibonacci_acao


# In[ ]:


@st.cache_data
def compra_percFechamentoDiaAnterior(acoes_selecionadas, dataInicial, dataFinal, variacao_min, variacao_max, volume_min, tipoAtivo):
    
    # Cria a variável número de ações, que conta a quantidade de ações selecionadas
    numAcoes = 0
    
    sleep_time = 1

    #Cria a tabela de relatório - Aba Consolidado
    tabela_relatorio_compra = pd.DataFrame()
    tabela_relatorio_compra.insert(0, "Código", 0, allow_duplicates = False)
    tabela_relatorio_compra.insert(1, "Variação", 0, allow_duplicates = False)
    tabela_relatorio_compra.insert(2, "Ganho", 0, allow_duplicates = False)
    tabela_relatorio_compra.insert(3, "Preço de Entrada", 0, allow_duplicates = False)
    tabela_relatorio_compra.insert(4, "Data Referência", 0, allow_duplicates = False)
    tabela_relatorio_compra.insert(5, "Qtd. Trades", 0, allow_duplicates = False)
    tabela_relatorio_compra.insert(6, "Qtd. Trades Positivos", 0, allow_duplicates = False)
    tabela_relatorio_compra.insert(7, "Qtd. Trades Negativos", 0, allow_duplicates = False)
    tabela_relatorio_compra.insert(8, "Média dos Trades Positivos", 0, allow_duplicates = False)
    tabela_relatorio_compra.insert(9, "Média dos Trades Negativos", 0, allow_duplicates = False)
    tabela_relatorio_compra.insert(10, "Maior Trade Positivo", 0, allow_duplicates = False)
    tabela_relatorio_compra.insert(11, "Menor Trade Positivo", 0, allow_duplicates = False)
    tabela_relatorio_compra.insert(12, "Maior Trade Negativo", 0, allow_duplicates = False)
    tabela_relatorio_compra.insert(13, "Menor Trade Negativo", 0, allow_duplicates = False)
    tabela_relatorio_compra.insert(14, "Resultado", 0, allow_duplicates = False)
    tabela_relatorio_compra.insert(15, "Média do Volume no Período", 0, allow_duplicates = False)
    
    tabela_consolidado_dados_acao = pd.DataFrame()
    
    tabela_consolidado_dados_acao.insert(0, 'Data', 0, allow_duplicates = False)
    tabela_consolidado_dados_acao.insert(1, 'Abertura', 0, allow_duplicates = False)
    tabela_consolidado_dados_acao.insert(2, 'Máxima', 0, allow_duplicates = False)
    tabela_consolidado_dados_acao.insert(3, 'Mínima', 0, allow_duplicates = False)    
    tabela_consolidado_dados_acao.insert(4, 'Fechamento', 0, allow_duplicates = False)    
    tabela_consolidado_dados_acao.insert(5, 'Volume', 0, allow_duplicates = False)        
    tabela_consolidado_dados_acao.insert(6, "Mínima %", 0, allow_duplicates = False)
    tabela_consolidado_dados_acao.insert(7, "Fechamento %", 0, allow_duplicates = False)
    tabela_consolidado_dados_acao.insert(8, "Ativo", 0, allow_duplicates = False)
    
    # Cria a aba 'Fibonacci'
    fibonacci_consolidado = pd.DataFrame()
    
    fibonacci_consolidado.insert(0, 'Ação', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(1, 'Data Referência', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(2, 'Último Fechamento', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(3, 'Fib 100', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(4, 'Dif Fib 100', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(5, 'Fib 76.4', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(6, 'Dif Fib 76.4', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(7, 'Fib 61.8', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(8, 'Dif Fib 61.8', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(9, 'Fib 50', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(10, 'Dif Fib 50', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(11, 'Fib 38.2', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(12, 'Dif Fib 38.2', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(13, 'Fib 23.6', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(14, 'Dif Fib 23.6', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(15, 'Fib 0', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(16, 'Dif Fib 0', 0, allow_duplicates = False)

    tabela_consolidado_resumo_acao = cria_tabela_resumo_acao()
    
    tabela_filtrado_dados_acao = pd.DataFrame()
    tabela_filtrado_resumo_acao = pd.DataFrame()
    
    dataInicial_seg = datetime(dataInicial.year, dataInicial.month, dataInicial.day, tzinfo=timezone)
       
    dataFinal_seg = datetime(dataFinal.year, dataFinal.month, dataFinal.day, tzinfo=timezone)
               
    with st.spinner('Analisando os dados das ações. Aguarde...'):
        
        # Para cada ação, dentre as ações selecionadas

        for acao in acoes_selecionadas:

            if(numAcoes>1):

                del tabela_resumo_acao

            # Primeira tabela da aba específica da ação. Contém os campos: Resultado, Qtd. Trades, Qtd. Trades Positivos,
            # Média Trades Positivos, Maior Trade Positivo, Menor Trade Positivo, Ganho e Ativo (é criada com essa informação, para
            # poder filtrar, mas ela é oculta na exibição)
            
            tabela_resumo_acao = cria_tabela_resumo_acao()
            
            # Busca os dados da ação no MT5
                
            dados_acao_tabela = cria_dados_acao_tabela (acao, dataInicial_seg, dataFinal_seg, tipoAtivo)    
                
            ultimoFechamentoAjustado = 0

            # Se a consulta no MT5 trouxe alguma informação, continua
                
            if len(dados_acao_tabela) > 0:
                
                #Verifica a última data enviada pelo MT5
                
                ultima_data = dados_acao_tabela['Data'].values[-1:]
                
                ultimoFechamentoAjustado = dados_acao_tabela['Fechamento'].values[-1:]
                
                dados_acao_tabela.drop(["Máxima %"], axis = 1, inplace = True)
                # Calcula a média do volume no período informado
                    
                mediaVolume = dados_acao_tabela['Volume'].mean() 
                    
                # Verifica se a média do volume no período informado é maior ou igual ao volume mínimo informado
                
                if(mediaVolume >= volume_min):
                        
                    # Conta o número de ações que tem a média do volume maior do que o volume mínimo
                    
                    numAcoes = numAcoes + 1
                    
                    fibonacci_acao = calcula_fibonacci(dados_acao_tabela, ultima_data, acao, ultimoFechamentoAjustado)
                    fibonacci_consolidado = pd.concat([fibonacci_consolidado, fibonacci_acao])
                    
                    # Para cada linha, coloca o nome do ativo na coluna Ativo, para conseguir filtrar depois
                    # e calcula o % Mínima e o Fechamento %

                    for linha in dados_acao_tabela.index:

                        dados_acao_tabela.loc[linha, 'Ativo'] = acao

                        if(linha > 0):

                            dados_acao_tabela.loc[linha, 'Mínima %'] = (dados_acao_tabela.at[linha - 1, 'Fechamento'] - dados_acao_tabela.at[linha, 'Mínima'])/dados_acao_tabela.at[linha - 1, 'Fechamento']*-100
                            dados_acao_tabela.loc[linha, 'Fechamento %'] = (dados_acao_tabela.at[linha - 1, 'Fechamento'] - dados_acao_tabela.at[linha, 'Fechamento'])/dados_acao_tabela.at[linha - 1, 'Fechamento']*-100

                        else:

                            dados_acao_tabela.loc[linha, 'Mínima %'] = 0
                            dados_acao_tabela.loc[linha, 'Fechamento %'] = 0
                        
                    # Arredonda a variação mínima informada para duas casas decimais

                    variacao = round(variacao_min, 2)
                        
                    # Número da coluna que será colocada o valor da variação

                    if(tipoAtivo == "cripto"):
                        
                        coluna = 9
                        
                    else:
                        
                        coluna = 10
                        
                    linha_tabela_resumo_acao = 0

                    # Percorre da variação mínima até a máxima, aumentando em 0.1 em cada iteração

                    while variacao <= variacao_max:

                        # Inclui uma coluna com o valor da variação na tabela dados_acao_tabela

                        dados_acao_tabela.insert(coluna, str(variacao), 0, allow_duplicates = False)

                        #Insere a variação na tabela_resumo_acao também
                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Variação'] = variacao

                        resultado = 0
                        qtdTrades = 0
                        qtdTradesPositivos = 0
                        somaTradesPositivos = 0
                        maiorTradePositivo = 0
                        menorTradePositivo = 0
                        mediaTradesPositivos = 0
                        qtdTradesNegativos = 0
                        somaTradesNegativos = 0
                        maiorTradeNegativo = 0
                        menorTradeNegativo = 0
                        mediaTradesNegativos = 0
                        ganho = 0

                        # Para cada linha da tabela dados_acao_tabela, calcula os resultados

                        for linha in dados_acao_tabela.index:

                            # Caso a Miníma % seja menor do que a variação

                            if(dados_acao_tabela.loc[linha, 'Mínima %'] < variacao):

                                # Calcula o resultado para a variação

                                dados_acao_tabela.loc[linha, str(variacao)] = round((variacao - dados_acao_tabela.loc[linha, 'Fechamento %']) *-1, 2)
                                resultado += dados_acao_tabela.loc[linha, str(variacao)]

                                # Verifica se o trade foi positivo ou negativo e ajusta a variável correspondente.
                                # Guarda se o resultado atual é menor ou maior do que os resultados anteriores

                                if(dados_acao_tabela.loc[linha, str(variacao)] != 0):

                                    qtdTrades += 1

                                    if(dados_acao_tabela.loc[linha, str(variacao)] >= 0):

                                        qtdTradesPositivos += 1
                                        somaTradesPositivos += dados_acao_tabela.loc[linha, str(variacao)]

                                        if(dados_acao_tabela.loc[linha, str(variacao)] > maiorTradePositivo):

                                            maiorTradePositivo = dados_acao_tabela.loc[linha, str(variacao)]

                                        if(menorTradePositivo == 0):

                                            menorTradePositivo = dados_acao_tabela.loc[linha, str(variacao)]

                                        else:

                                            if(dados_acao_tabela.loc[linha, str(variacao)] < menorTradePositivo):

                                                menorTradePositivo = dados_acao_tabela.loc[linha, str(variacao)]
                                                
                                    else:
                                        
                                        qtdTradesNegativos += 1
                                        somaTradesNegativos += dados_acao_tabela.loc[linha, str(variacao)]
                                        
                                        if(maiorTradeNegativo == 0):
                                            
                                            maiorTradeNegativo = dados_acao_tabela.loc[linha, str(variacao)]
                                            
                                        else:

                                            if(dados_acao_tabela.loc[linha, str(variacao)] > maiorTradeNegativo):

                                                maiorTradeNegativo = dados_acao_tabela.loc[linha, str(variacao)]

                                        if(menorTradeNegativo == 0):

                                            menorTradeNegativo = dados_acao_tabela.loc[linha, str(variacao)]

                                        else:

                                            if(dados_acao_tabela.loc[linha, str(variacao)] < menorTradeNegativo):

                                                menorTradeNegativo = dados_acao_tabela.loc[linha, str(variacao)]

                            else:

                                dados_acao_tabela.loc[linha, str(variacao)] = round(0.0, 2)

                        coluna += 1

                        # Depois de percorrer todas as linhas, preenche a tabela_resumo_acao com 
                        # os dados de Resultado, Qtd. Trades e Qtd. Trades Positivos

                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Resultado'] = resultado
                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Qtd. Trades'] = qtdTrades
                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Qtd. Trades Positivos'] = qtdTradesPositivos
                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Qtd. Trades Negativos'] = qtdTradesNegativos

                        if(qtdTradesPositivos > 0):

                            mediaTradesPositivos = somaTradesPositivos/qtdTradesPositivos

                        else:

                            mediaTradesPositivos = 0
                            
                        if(qtdTradesNegativos > 0):

                            mediaTradesNegativos = somaTradesNegativos/qtdTradesNegativos

                        else:

                            mediaTradesNegativos = 0


                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Média Trades Positivos'] = mediaTradesPositivos
                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Maior Trade Positivo'] = maiorTradePositivo
                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Menor Trade Positivo'] = menorTradePositivo
                        
                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Média Trades Negativos'] = mediaTradesNegativos
                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Maior Trade Negativo'] = maiorTradeNegativo
                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Menor Trade Negativo'] = menorTradeNegativo

                        if(qtdTrades > 0):

                             ganho = qtdTradesPositivos/qtdTrades

                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Ganho'] = ganho
                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Ativo'] = acao

                        precoEntrada = np.round((ultimoFechamentoAjustado * (1+variacao/100)), 2)

                        # Se o ganhor for maior do que 75%, inclui na tabela_relatorio_compra

                        if(ganho > 0.75): 

                            tabela_relatorio_compra = pd.DataFrame([tabela_relatorio_compra['Código': acao], tabela_relatorio_compra['Variação': variacao], tabela_relatorio_compra['Ganho': ganho], 
                                                                 tabela_relatorio_compra['Média do Volume no Período': mediaVolume], tabela_relatorio_compra['Preço de Entrada': precoEntrada], tabela_relatorio_compra['Data Referência': ultima_data], 
                                                                 tabela_relatorio_compra['Qtd. Trades': qtdTrades], tabela_relatorio_compra['Qtd. Trades Positivos': qtdTradesPositivos], tabela_relatorio_compra['Qtd. Trades Negativos': qtdTradesNegativos], 
                                                                 tabela_relatorio_compra['Média dos Trades Positivos': mediaTradesPositivos], tabela_relatorio_compra['Média dos Trades Negativos': mediaTradesNegativos], tabela_relatorio_compra['Maior Trade Positivo': maiorTradePositivo],
                                                                 tabela_relatorio_compra['Menor Trade Positivo': menorTradePositivo], tabela_relatorio_compra['Maior Trade Negativo': maiorTradeNegativo], tabela_relatorio_compra['Menor Trade Negativo': menorTradeNegativo], 
                                                                 tabela_relatorio_compra['Resultado': resultado]])

                        variacao = round(variacao + 0.1, 2)
                        linha_tabela_resumo_acao +=1
                    
                    tabela_consolidado_dados_acao = pd.concat([tabela_consolidado_dados_acao, dados_acao_tabela])
                    tabela_consolidado_resumo_acao = pd.concat([tabela_consolidado_resumo_acao, tabela_resumo_acao])
                    
                    sleep(sleep_time)
                        
                    st.sidebar.success(acao + ' - Dados analisados!')          
                    
                else:
                        
                    st.sidebar.warning(acao + ' - Volume médio menor que o mínimo!')
        
        num_linha = 0

        if(len(tabela_relatorio_compra) > 1):

            continua = True

        else:

            continua = False

        while continua:

            codigo = tabela_relatorio_compra.at[num_linha, 'Código']

            codigo_posterior = tabela_relatorio_compra.at[num_linha + 1, 'Código']

            qtdTrades = tabela_relatorio_compra.at[num_linha, 'Qtd. Trades']
            qtdTrades_posterior = tabela_relatorio_compra.at[num_linha + 1, 'Qtd. Trades']

            qtdTradesPositivos = tabela_relatorio_compra.at[num_linha, 'Qtd. Trades Positivos']
            qtdTradesPositivos_posterior = tabela_relatorio_compra.at[num_linha + 1, 'Qtd. Trades Positivos']

            resultado = tabela_relatorio_compra.at[num_linha, 'Resultado']
            resultado_posterior = tabela_relatorio_compra.at[num_linha + 1, 'Resultado']

            if(codigo_posterior == codigo and qtdTrades == qtdTrades_posterior and qtdTradesPositivos == qtdTradesPositivos_posterior):                           

                if(resultado_posterior <= resultado):

                    tabela_relatorio_compra.drop(labels = num_linha + 1, axis = 0, inplace = True)
                    tabela_relatorio_compra = tabela_relatorio_compra.reset_index(drop = True)

                else:

                    tabela_relatorio_compra.drop(labels = num_linha, axis = 0, inplace = True)
                    tabela_relatorio_compra = tabela_relatorio_compra.reset_index(drop = True)

            else:

                num_linha = num_linha + 1

            if(num_linha >= len(tabela_relatorio_compra) -1):

                continua = False
        
        tabela_relatorio_compra_formatada = formata_tabela_relatorio(tabela_relatorio_compra)
        
        tabela_consolidado_dados_acao_sem_formatacao = tabela_consolidado_dados_acao.copy(deep=True)
        
        tabela_consolidado_dados_acao = formata_dados_acao_tabela_compra(tabela_consolidado_dados_acao)
        
        variacao2 = round(variacao_min, 2)
                    
        while variacao2 <= variacao_max:

            tabela_consolidado_dados_acao[str(variacao2)] = pd.Series(["{0:.2f}%".format(val) for val in tabela_consolidado_dados_acao[str(variacao2)]], index = tabela_consolidado_dados_acao.index)
            tabela_consolidado_dados_acao[str(variacao2)] = tabela_consolidado_dados_acao[str(variacao2)].astype(str)
            tabela_consolidado_dados_acao[str(variacao2)] = tabela_consolidado_dados_acao[str(variacao2)].str.replace('.', ',')
 
            variacao2 = round(variacao2+0.1, 2)
        
        fibonacci_consolidado.reset_index(drop = True)
        
        return tabela_relatorio_compra, tabela_relatorio_compra_formatada, tabela_consolidado_dados_acao, tabela_consolidado_resumo_acao, fibonacci_consolidado, tabela_consolidado_dados_acao_sem_formatacao


# In[ ]:


@st.cache_data
def venda_fechamentoDia(acoes_selecionadas, dataInicial, dataFinal, variacao_min, variacao_max, volume_min, tipoAtivo):
    
    # Cria a variável número de ações, que conta a quantidade de ações selecionadas
    numAcoes = 0

    sleep_time = 1
    
    #Cria a tabela de relatório - Aba Consolidado
    tabela_relatorio_venda = pd.DataFrame()
    tabela_relatorio_venda.insert(0, "Código", 0, allow_duplicates = False)
    tabela_relatorio_venda.insert(1, "Variação", 0, allow_duplicates = False)
    tabela_relatorio_venda.insert(2, "Ganho", 0, allow_duplicates = False)
    tabela_relatorio_venda.insert(3, "Preço de Entrada", 0, allow_duplicates = False)
    tabela_relatorio_venda.insert(4, "Data Referência", 0, allow_duplicates = False)
    tabela_relatorio_venda.insert(5, "Qtd. Trades", 0, allow_duplicates = False)
    tabela_relatorio_venda.insert(6, "Qtd. Trades Positivos", 0, allow_duplicates = False)
    tabela_relatorio_venda.insert(7, "Qtd. Trades Negativos", 0, allow_duplicates = False)
    tabela_relatorio_venda.insert(8, "Média dos Trades Positivos", 0, allow_duplicates = False)
    tabela_relatorio_venda.insert(9, "Média dos Trades Negativos", 0, allow_duplicates = False)
    tabela_relatorio_venda.insert(10, "Maior Trade Positivo", 0, allow_duplicates = False)
    tabela_relatorio_venda.insert(11, "Menor Trade Positivo", 0, allow_duplicates = False)
    tabela_relatorio_venda.insert(12, "Maior Trade Negativo", 0, allow_duplicates = False)
    tabela_relatorio_venda.insert(13, "Menor Trade Negativo", 0, allow_duplicates = False)
    tabela_relatorio_venda.insert(14, "Resultado", 0, allow_duplicates = False)
    tabela_relatorio_venda.insert(15, "Média do Volume no Período", 0, allow_duplicates = False)
     
    tabela_consolidado_dados_acao = pd.DataFrame()
    
    tabela_consolidado_dados_acao.insert(0, 'Data', 0, allow_duplicates = False)
    tabela_consolidado_dados_acao.insert(1, 'Abertura', 0, allow_duplicates = False)
    tabela_consolidado_dados_acao.insert(2, 'Máxima', 0, allow_duplicates = False)
    tabela_consolidado_dados_acao.insert(3, 'Mínima', 0, allow_duplicates = False)    
    tabela_consolidado_dados_acao.insert(4, 'Fechamento', 0, allow_duplicates = False)    
    tabela_consolidado_dados_acao.insert(5, 'Volume', 0, allow_duplicates = False)        
    tabela_consolidado_dados_acao.insert(6, "Máxima %", 0, allow_duplicates = False)
    tabela_consolidado_dados_acao.insert(7, "Fechamento %", 0, allow_duplicates = False)
    tabela_consolidado_dados_acao.insert(8, "Ativo", 0, allow_duplicates = False)
    
    # Cria a aba 'Fibonacci'
    fibonacci_consolidado = pd.DataFrame()
    
    fibonacci_consolidado.insert(0, 'Ação', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(1, 'Data Referência', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(2, 'Último Fechamento', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(3, 'Fib 100', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(4, 'Dif Fib 100', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(5, 'Fib 76.4', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(6, 'Dif Fib 76.4', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(7, 'Fib 61.8', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(8, 'Dif Fib 61.8', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(9, 'Fib 50', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(10, 'Dif Fib 50', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(11, 'Fib 38.2', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(12, 'Dif Fib 38.2', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(13, 'Fib 23.6', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(14, 'Dif Fib 23.6', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(15, 'Fib 0', 0, allow_duplicates = False)
    fibonacci_consolidado.insert(16, 'Dif Fib 0', 0, allow_duplicates = False)

    tabela_consolidado_resumo_acao = cria_tabela_resumo_acao()
    
    tabela_filtrado_dados_acao = pd.DataFrame()
    tabela_filtrado_resumo_acao = pd.DataFrame()
    
    dataInicial_seg = datetime(dataInicial.year, dataInicial.month, dataInicial.day, tzinfo=timezone)
    
    dataFinal_seg = datetime(dataFinal.year, dataFinal.month, dataFinal.day, tzinfo=timezone)
    
               
    with st.spinner('Analisando os dados das ações. Aguarde...'):
        
        # Para cada ação, dentre as ações selecionadas

        for acao in acoes_selecionadas:

            if(numAcoes>1):

                del tabela_resumo_acao

            # Primeira tabela da aba específica da ação. Contém os campos: Resultado, Qtd. Trades, Qtd. Trades Positivos,
            # Média Trades Positivos, Maior Trade Positivo, Menor Trade Positivo, Ganho e Ativo (é criada com essa informação, para
            # poder filtrar, mas ela é oculta na exibição)
            
            tabela_resumo_acao = cria_tabela_resumo_acao()
            
            # Busca os dados da ação no MT5
                
            dados_acao_tabela = cria_dados_acao_tabela (acao, dataInicial_seg, dataFinal_seg, tipoAtivo)        
                
            ultimoFechamentoAjustado = 0

            # Se a consulta no MT5 trouxe alguma informação, continua
                
            if len(dados_acao_tabela) > 0:
                
                ultima_data = dados_acao_tabela['Data'].values[-1:]
                ultimoFechamentoAjustado = dados_acao_tabela['Fechamento'].values[-1:]
                    
                # Calcula a média do volume no período informado
                
                dados_acao_tabela.drop(["Mínima %"], axis = 1, inplace = True)
                
                mediaVolume = dados_acao_tabela['Volume'].mean() 
                    
                # Verifica se a média do volume no período informado é maior ou igual ao volume mínimo informado
                
                if(mediaVolume >= volume_min):
                        
                    # Conta o número de ações que tem a média do volume maior do que o volume mínimo
                    
                    numAcoes = numAcoes + 1
                    
                    fibonacci_acao = calcula_fibonacci(dados_acao_tabela, ultima_data, acao, ultimoFechamentoAjustado)
                    fibonacci_consolidado = pd.concat([fibonacci_consolidado, fibonacci_acao])
                    
                    # Para cada linha, coloca o nome do ativo na coluna Ativo, para conseguir filtrar depois
                    # e calcula o % Mínima e o Fechamento %

                    for linha in dados_acao_tabela.index:

                        dados_acao_tabela.loc[linha, 'Ativo'] = acao

                        if(linha > 0):

                            dados_acao_tabela.loc[linha, 'Máxima %'] = (dados_acao_tabela.at[linha - 1, 'Fechamento'] - dados_acao_tabela.at[linha, 'Máxima'])/dados_acao_tabela.at[linha - 1, 'Fechamento']*-100
                            dados_acao_tabela.loc[linha, 'Fechamento %'] = (dados_acao_tabela.at[linha - 1, 'Fechamento'] - dados_acao_tabela.at[linha, 'Fechamento'])/dados_acao_tabela.at[linha - 1, 'Fechamento']*-100

                        else:

                            dados_acao_tabela.loc[linha, 'Máxima %'] = 0
                            dados_acao_tabela.loc[linha, 'Fechamento %'] = 0
                        
                    # Arredonda a variação mínima informada para duas casas decimais

                    variacao = round(variacao_min, 2)
                        
                    # Número da coluna que será colocada o valor da variação

                    coluna = 10
                    linha_tabela_resumo_acao = 0

                    # Percorre da variação mínima até a máxima, aumentando em 0.1 em cada iteração

                    while variacao <= variacao_max:

                        # Inclui uma coluna com o valor da variação na tabela dados_acao_tabela

                        dados_acao_tabela.insert(coluna, str(variacao), 0, allow_duplicates = False)

                        #Insere a variação na tabela_resumo_acao também
                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Variação'] = variacao

                        resultado = 0
                        qtdTrades = 0
                        qtdTradesPositivos = 0
                        somaTradesPositivos = 0
                        maiorTradePositivo = 0
                        menorTradePositivo = 0
                        mediaTradesPositivos = 0
                        qtdTradesNegativos = 0
                        somaTradesNegativos = 0
                        maiorTradeNegativo = 0
                        menorTradeNegativo = 0
                        mediaTradesNegativos = 0
                        ganho = 0

                        # Para cada linha da tabela dados_acao_tabela, calcula os resultados

                        for linha in dados_acao_tabela.index:

                            # Caso a Miníma % seja menor do que a variação

                            if(dados_acao_tabela.loc[linha, 'Máxima %'] > variacao):

                                # Calcula o resultado para a variação

                                dados_acao_tabela.loc[linha, str(variacao)] = round((variacao - dados_acao_tabela.loc[linha, 'Fechamento %']), 2)
                                resultado += dados_acao_tabela.loc[linha, str(variacao)]

                                # Verifica se o trade foi positivo ou negativo e ajusta a variável correspondente.
                                # Guarda se o resultado atual é menor ou maior do que os resultados anteriores

                                if(dados_acao_tabela.loc[linha, str(variacao)] != 0):

                                    qtdTrades += 1

                                    if(dados_acao_tabela.loc[linha, str(variacao)] > 0):

                                        qtdTradesPositivos += 1
                                        somaTradesPositivos += dados_acao_tabela.loc[linha, str(variacao)]

                                        if(dados_acao_tabela.loc[linha, str(variacao)] > maiorTradePositivo):

                                            maiorTradePositivo = dados_acao_tabela.loc[linha, str(variacao)]

                                        if(menorTradePositivo == 0):

                                            menorTradePositivo = dados_acao_tabela.loc[linha, str(variacao)]

                                        else:

                                            if(dados_acao_tabela.loc[linha, str(variacao)] < menorTradePositivo):

                                                menorTradePositivo = dados_acao_tabela.loc[linha, str(variacao)]
                                    else:
                                        
                                        qtdTradesNegativos += 1
                                        somaTradesNegativos += dados_acao_tabela.loc[linha, str(variacao)]
                                        
                                        if(maiorTradeNegativo == 0):
                                            
                                            maiorTradeNegativo = dados_acao_tabela.loc[linha, str(variacao)]
                                            
                                        else:

                                            if(dados_acao_tabela.loc[linha, str(variacao)] > maiorTradeNegativo):

                                                maiorTradeNegativo = dados_acao_tabela.loc[linha, str(variacao)]

                                        if(menorTradeNegativo == 0):

                                            menorTradeNegativo = dados_acao_tabela.loc[linha, str(variacao)]

                                        else:

                                            if(dados_acao_tabela.loc[linha, str(variacao)] < menorTradeNegativo):

                                                menorTradeNegativo = dados_acao_tabela.loc[linha, str(variacao)]


                            else:

                                dados_acao_tabela.loc[linha, str(variacao)] = round(0.0, 2)

                        coluna += 1

                        # Depois de percorrer todas as linhas, preenche a tabela_resumo_acao com 
                        # os dados de Resultado, Qtd. Trades e Qtd. Trades Positivos

                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Resultado'] = resultado
                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Qtd. Trades'] = qtdTrades
                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Qtd. Trades Positivos'] = qtdTradesPositivos
                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Qtd. Trades Negativos'] = qtdTradesNegativos

                        if(qtdTradesPositivos > 0):

                            mediaTradesPositivos = somaTradesPositivos/qtdTradesPositivos

                        else:

                            mediaTradesPositivos = 0
                            
                        if(qtdTradesNegativos > 0):

                            mediaTradesNegativos = somaTradesNegativos/qtdTradesNegativos

                        else:

                            mediaTradesNegativos = 0

                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Média Trades Positivos'] = mediaTradesPositivos
                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Maior Trade Positivo'] = maiorTradePositivo
                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Menor Trade Positivo'] = menorTradePositivo
                        
                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Média Trades Negativos'] = mediaTradesNegativos
                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Maior Trade Negativo'] = maiorTradeNegativo
                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Menor Trade Negativo'] = menorTradeNegativo

                        if(qtdTrades > 0):

                             ganho = qtdTradesPositivos/qtdTrades

                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Ganho'] = ganho
                        tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Ativo'] = acao

                        precoEntrada = np.round((ultimoFechamentoAjustado * (1+variacao/100)), 2)

                        # Se o ganhor for maior do que 75%, inclui na tabela_relatorio_venda

                        if(ganho > 0.75): 

                            tabela_relatorio_venda = pd.DataFrame([tabela_relatorio_venda['Código': acao], tabela_relatorio_venda['Variação': variacao], tabela_relatorio_venda['Ganho': ganho] , tabela_relatorio_venda['Média do Volume no Período': mediaVolume] , 
                                tabela_relatorio_venda['Preço de Entrada': precoEntrada] , tabela_relatorio_venda['Data Referência': ultima_data] , tabela_relatorio_venda['Qtd. Trades': qtdTrades] ,
                                tabela_relatorio_venda['Qtd. Trades Positivos': qtdTradesPositivos] , tabela_relatorio_venda['Qtd. Trades Negativos': qtdTradesNegativos] , tabela_relatorio_venda['Média dos Trades Positivos': mediaTradesPositivos] ,
                                tabela_relatorio_venda['Média dos Trades Negativos': mediaTradesNegativos] , tabela_relatorio_venda['Maior Trade Positivo': maiorTradePositivo] , tabela_relatorio_venda['Menor Trade Positivo': menorTradePositivo] ,
                                tabela_relatorio_venda['Maior Trade Negativo': maiorTradeNegativo] , tabela_relatorio_venda['Menor Trade Negativo': menorTradeNegativo] , tabela_relatorio_venda['Resultado': resultado]])

                        variacao = round(variacao + 0.1, 2)
                        linha_tabela_resumo_acao +=1
                    
                    tabela_consolidado_dados_acao = pd.concat([tabela_consolidado_dados_acao, dados_acao_tabela])
                    tabela_consolidado_resumo_acao = pd.concat([tabela_consolidado_resumo_acao, tabela_resumo_acao])
                    
                    sleep(sleep_time)
                        
                    st.sidebar.success(acao + ' - Dados analisados!')          
                    
                else:
                        
                    st.sidebar.warning(acao + ' - Volume médio menor que o mínimo!')
        
        num_linha = 0

        if(len(tabela_relatorio_venda) > 1):

            continua = True

        else:

            continua = False

        while continua:

            codigo = tabela_relatorio_venda.at[num_linha, 'Código']

            codigo_posterior = tabela_relatorio_venda.at[num_linha + 1, 'Código']

            qtdTrades = tabela_relatorio_venda.at[num_linha, 'Qtd. Trades']
            qtdTrades_posterior = tabela_relatorio_venda.at[num_linha + 1, 'Qtd. Trades']

            qtdTradesPositivos = tabela_relatorio_venda.at[num_linha, 'Qtd. Trades Positivos']
            qtdTradesPositivos_posterior = tabela_relatorio_venda.at[num_linha + 1, 'Qtd. Trades Positivos']

            resultado = tabela_relatorio_venda.at[num_linha, 'Resultado']
            resultado_posterior = tabela_relatorio_venda.at[num_linha + 1, 'Resultado']

            if(codigo_posterior == codigo and qtdTrades == qtdTrades_posterior and qtdTradesPositivos == qtdTradesPositivos_posterior):                           

                if(resultado_posterior <= resultado):

                    tabela_relatorio_venda.drop(labels = num_linha + 1, axis = 0, inplace = True)
                    tabela_relatorio_venda = tabela_relatorio_venda.reset_index(drop = True)

                else:

                    tabela_relatorio_venda.drop(labels = num_linha, axis = 0, inplace = True)
                    tabela_relatorio_venda = tabela_relatorio_venda.reset_index(drop = True)

            else:

                num_linha = num_linha + 1

            if(num_linha >= len(tabela_relatorio_venda) -1):

                continua = False
        
        
        tabela_relatorio_venda_formatada = formata_tabela_relatorio(tabela_relatorio_venda)
        
        tabela_consolidado_dados_acao_sem_formatacao = tabela_consolidado_dados_acao.copy(deep=True)
        
        tabela_consolidado_dados_acao = formata_dados_acao_tabela_venda(tabela_consolidado_dados_acao)
        
        variacao2 = round(variacao_min, 2)
                    
        while variacao2 <= variacao_max:

            tabela_consolidado_dados_acao[str(variacao2)] = pd.Series(["{0:.2f}%".format(val) for val in tabela_consolidado_dados_acao[str(variacao2)]], index = tabela_consolidado_dados_acao.index)
            tabela_consolidado_dados_acao[str(variacao2)] = tabela_consolidado_dados_acao[str(variacao2)].astype(str)
            tabela_consolidado_dados_acao[str(variacao2)] = tabela_consolidado_dados_acao[str(variacao2)].str.replace('.', ',')
 
            variacao2 = round(variacao2+0.1, 2)
        
        return tabela_relatorio_venda, tabela_relatorio_venda_formatada, tabela_consolidado_dados_acao, tabela_consolidado_resumo_acao, fibonacci_consolidado, tabela_consolidado_dados_acao_sem_formatacao


# In[ ]:


def top10(tabela_relatorio, compra_venda, dif_datas):
    
    qtd_ganhos_perdas = round(dif_datas.days*0.08, 0)
    
    tabela_relatorio_100 = tabela_relatorio.copy()
    tabela_relatorio_90_99 = tabela_relatorio.copy()
    
    #Ganho de 100%
    
    if(compra_venda == "Compra"):
    
        tabela_relatorio_100.sort_values(by=['Qtd. Trades Positivos', 'Qtd. Trades Negativos', 'Média dos Trades Positivos'], inplace = True, ascending=[False, True, False])
        tabela_relatorio_100 = tabela_relatorio_100.loc[tabela_relatorio_100['Média dos Trades Positivos'] >= 1.0]
        tabela_relatorio_100 = tabela_relatorio_100.loc[tabela_relatorio_100['Ganho'] == 1.0]
        tabela_relatorio_100 = tabela_relatorio_100.loc[tabela_relatorio_100['Qtd. Trades Positivos'] >= qtd_ganhos_perdas]
        tabela_relatorio_100 = tabela_relatorio_100.loc[tabela_relatorio_100['Média dos Trades Positivos'] > abs(tabela_relatorio_100['Média dos Trades Negativos'])]
        tabela_relatorio_100 = tabela_relatorio_100.reset_index(drop = True)
        
    else:
        
        tabela_relatorio_100.sort_values(by=['Qtd. Trades Negativos', 'Qtd. Trades Positivos', 'Média dos Trades Negativos'], inplace = True, ascending=[False, True, False])

        tabela_relatorio_100 = tabela_relatorio_100.loc[tabela_relatorio_100['Média dos Trades Negativos'] >= 1.0]
        tabela_relatorio_100 = tabela_relatorio_100.loc[tabela_relatorio_100['Ganho'] == 1.0]
        tabela_relatorio_100 = tabela_relatorio_100.loc[tabela_relatorio_100['Qtd. Trades Negativos'] >= qtd_ganhos_perdas]

        tabela_relatorio_100 = tabela_relatorio_100.loc[tabela_relatorio_100['Média dos Trades Negativos'] > abs(tabela_relatorio_100['Média dos Trades Positivos'])]
    
    # Ganho de 90 a 99%
    
    if(compra_venda == "Compra"):
    
        tabela_relatorio_90_99.sort_values(by=['Qtd. Trades Positivos', 'Qtd. Trades Negativos', 'Média dos Trades Positivos'], inplace = True, ascending=[False, True, False])

        tabela_relatorio_90_99 = tabela_relatorio_90_99.loc[tabela_relatorio_90_99['Média dos Trades Positivos'] >= 0.8]
        tabela_relatorio_90_99 = tabela_relatorio_90_99.loc[tabela_relatorio_90_99['Ganho'] >= 0.9]
        tabela_relatorio_90_99 = tabela_relatorio_90_99.loc[tabela_relatorio_90_99['Ganho'] <= 0.99]
        tabela_relatorio_90_99 = tabela_relatorio_90_99.loc[tabela_relatorio_90_99['Qtd. Trades Positivos'] >= qtd_ganhos_perdas]
        tabela_relatorio_90_99 = tabela_relatorio_90_99.loc[tabela_relatorio_90_99['Qtd. Trades Negativos'] <= 1]

        tabela_relatorio_90_99 = tabela_relatorio_90_99.loc[tabela_relatorio_90_99['Média dos Trades Positivos'] > abs(tabela_relatorio_90_99['Média dos Trades Negativos'])]

        tabela_relatorio_90_99 = tabela_relatorio_90_99.reset_index(drop = True)
        
    else:
        
        tabela_relatorio_90_99.sort_values(by=['Qtd. Trades Negativos', 'Qtd. Trades Positivos', 'Média dos Trades Negativos'], inplace = True, ascending=[False, True, False])

        tabela_relatorio_90_99 = tabela_relatorio_90_99.loc[tabela_relatorio_90_99['Média dos Trades Negativos'] >= 1.0]
        tabela_relatorio_90_99 = tabela_relatorio_90_99.loc[tabela_relatorio_90_99['Ganho'] >= 0.9]
        tabela_relatorio_90_99 = tabela_relatorio_90_99.loc[tabela_relatorio_90_99['Ganho'] <= 0.99]
        tabela_relatorio_90_99 = tabela_relatorio_90_99.loc[tabela_relatorio_90_99['Qtd. Trades Negativos'] >= qtd_ganhos_perdas]
        tabela_relatorio_90_99 = tabela_relatorio_90_99.loc[tabela_relatorio_90_99['Qtd. Trades Positivos'] <= 1]

        tabela_relatorio_90_99 = tabela_relatorio_90_99.loc[tabela_relatorio_90_99['Média dos Trades Negativos'] > abs(tabela_relatorio_90_99['Média dos Trades Positivos'])]
    
    # Junta as duas tabelas
    
    top10_consolidado = pd.concat([tabela_relatorio_100, tabela_relatorio_90_99], axis=0)
    
    # Formata a tabela
    
    top10_consolidado = formata_tabela_relatorio(top10_consolidado)
    
    return top10_consolidado.head(10)


# In[ ]:


st.set_page_config(page_title="Análise dados da Bolsa", layout="wide", initial_sidebar_state="expanded")

acoes_completo = pd.read_csv('acoes.csv', sep=";")
acoes_lista = list(acoes_completo['Codigo'])

estados_df2 = pd.DataFrame()
# Configura o front end

if "visibility" not in st.session_state:
    
    st.session_state.visibility = "visible"
    st.session_state.disabled = False   

if "load_state" not in st.session_state:
    
    st.session_state.load_state = False
    
if 'tabs' not in st.session_state:    

    st.session_state['tabs'] = ['']

else:
    
    del st.session_state['tabs']
    st.session_state['tabs'] = ['']
    
acoes_lista_filtrada = {}

st.title('Análise dados da Bolsa')

compra_venda = st.sidebar.radio("Selecione uma operação:", ("Compra", "Venda"))

if compra_venda == "Compra":
    
    lista_estrategia = {'% do fechamento do dia anterior'}

else:
    
    lista_estrategia = {'Fechamento do dia'}

estrategia = st.sidebar.selectbox("Selecione uma estratégia:", lista_estrategia)

st.sidebar.write("Selecione um ou mais mercados:")
acoes = st.sidebar.checkbox('Ações')
bmf = st.sidebar.checkbox('BMF')
bdr = st.sidebar.checkbox('BDR')
cripto = st.sidebar.checkbox('Criptomoedas')

if acoes:
    
    if len(acoes_lista_filtrada) == 0:
        
        acoes_lista_filtrada = acoes_completo.query("Tipo_Ativo=='Ação'")
        acoes_lista_filtrada = acoes_lista_filtrada['Codigo']
        tipoAtivo = "ações"
        
    else:
    
        lista_acao = acoes_completo.query("Tipo_Ativo=='Ação'")
        lista_acao = lista_acao['Codigo']
        tipoAtivo = "ações"
        
        acoes_lista_filtrada = pd.concat([acoes_lista_filtrada, lista_acao], axis=0, ignore_index=True)
    
if bmf:
    
    if len(acoes_lista_filtrada) == 0:
        
        acoes_lista_filtrada = acoes_completo.query("Tipo_Ativo=='BMF'")
        acoes_lista_filtrada = acoes_lista_filtrada['Codigo']
        tipoAtivo = "bmf"
        
    else:
        
        lista_bmf = acoes_completo.query("Tipo_Ativo=='BMF'")
        lista_bmf = lista_bmf['Codigo']
        tipoAtivo = "bmf"
  
        acoes_lista_filtrada = pd.concat([acoes_lista_filtrada, lista_bmf], axis=0, ignore_index=True)
                        
if bdr:
    
    if len(acoes_lista_filtrada) == 0:
        
        acoes_lista_filtrada = acoes_completo.query("Tipo_Ativo=='BDR'")
        acoes_lista_filtrada = acoes_lista_filtrada['Codigo']
        tipoAtivo = "bdr"
        
    else:
            
        lista_bdr = acoes_completo.query("Tipo_Ativo=='BDR'")
        lista_bdr = lista_bdr['Codigo']
        tipoAtivo = "bdr"
        
        acoes_lista_filtrada = pd.concat([acoes_lista_filtrada, lista_bdr], axis=0, ignore_index=True)
        
if cripto:
    
    if len(acoes_lista_filtrada) == 0:
        
        acoes_lista_filtrada = acoes_completo.query("Tipo_Ativo=='Cripto'")
        acoes_lista_filtrada = acoes_lista_filtrada['Codigo']
        
        tipoAtivo = "cripto"
        
    else:
    
        lista_acao = acoes_completo.query("Tipo_Ativo=='Cripto'")
        lista_acao = lista_acao['Codigo']
        tipoAtivo = "cripto"
        
        acoes_lista_filtrada = pd.concat([acoes_lista_filtrada, lista_acao], axis=0, ignore_index=True)

acoes_selecionadas = list(st.sidebar.multiselect('Selecione um ou mais ativos:', acoes_lista_filtrada, label_visibility=st.session_state.visibility))

selecionar_todos = st.sidebar.checkbox("Selecionar todos os ativos", key="disabled") 

if selecionar_todos:
    
    if(not acoes and not bmf and not bdr and not cripto):
        
        st.sidebar.error("Selecione pelo menos um mercado!")
        
    else:
        
        acoes_selecionadas = acoes_lista_filtrada

dataInicialExibida = date.today() - timedelta(60)
dataFinalExibida = date.today()

timezone = pytz.timezone("Etc/UTC")

dataInicial = st.sidebar.date_input('Selecione a data inicial:', dataInicialExibida)
dataFinal = st.sidebar.date_input('Selecione a data final:', dataFinalExibida)

variacao_min = st.sidebar.number_input('Variação Mínima:')
variacao_max = st.sidebar.number_input('Variação Máxima:')

volume_min = st.sidebar.number_input('Volume Médio Mínimo:', min_value=0, step = 100000)

hoje = dt.datetime.now()

dif_datas = dataFinal - dataInicial

if st.sidebar.button('Calcular') or st.session_state.load_state:   
    
    st.session_state.load_state = True
    
    if(len(acoes_selecionadas)> 0):
        
        if(dataInicial<date.today()):
            
            if(variacao_min < variacao_max):
                
                if(compra_venda == "Compra"):
                    
                    if(estrategia == "% do fechamento do dia anterior"):
                        
                        if(len(acoes_selecionadas) > 0):
                        
                            tabela_relatorio, tabela_relatorio_compra_formatada, tabela_consolidado_dados_acao, tabela_consolidado_resumo_acao, fibonacci_consolidado, tabela_consolidado_dados_acao_sem_formatacao = compra_percFechamentoDiaAnterior(acoes_selecionadas, dataInicial, dataFinal, variacao_min, variacao_max, volume_min, tipoAtivo)
                            
                            tabela_top10 = top10(tabela_relatorio, compra_venda, dif_datas)
                            
                            with st.expander("Top 10"):
                                
                                aggrid_sem_selecao(tabela_top10)
                                
                            with st.expander("Fibonacci"):
                                
                                grid_response2 = aggrid_selecao_unica(fibonacci_consolidado)
                                
                                resposta_fibo = pd.DataFrame(grid_response2["selected_rows"])
                                
                                if(len(resposta_fibo) > 0):

                                    ativo = resposta_fibo.at[0, 'Ação']

                                    tabela_filtrado_dados_acao_graf = tabela_consolidado_dados_acao_sem_formatacao[tabela_consolidado_dados_acao_sem_formatacao.Ativo == ativo]  

                                    if(tipoAtivo == "cripto"):

                                        tabela_filtrado_dados_acao_graf.drop(['Ativo'], axis = 1, inplace = True)

                                    else:

                                        tabela_filtrado_dados_acao_graf.drop(['Ativo', 'index'], axis = 1, inplace = True)

                                    fibonacci_filtrado = fibonacci_consolidado[fibonacci_consolidado.Ação == ativo]

                                    datas = tabela_filtrado_dados_acao_graf['Data'].unique()

                                    plt.figure(figsize=(30,10))
                                    plt.plot(datas, tabela_filtrado_dados_acao_graf["Fechamento"], color="black", label="Preço")
                                    plt.axhline(y=fibonacci_filtrado.at[0, "Fib 100"], color="limegreen", linestyle="-", label="100%")
                                    plt.axhline(y=fibonacci_filtrado.at[0, "Fib 76.4"], color="slateblue", linestyle="-", label="76.4%")
                                    plt.axhline(y=fibonacci_filtrado.at[0, "Fib 61.8"], color="mediumvioletred", linestyle="-", label="61.8%")
                                    plt.axhline(y=fibonacci_filtrado.at[0, "Fib 50"], color="gold", linestyle="-", label="50%")
                                    plt.axhline(y=fibonacci_filtrado.at[0, "Fib 23.6"], color="darkturquoise", linestyle="-", label="23.6%")
                                    plt.axhline(y=fibonacci_filtrado.at[0, "Fib 0"], color="lightcoral", linestyle="-", label="0%")

                                    plt.ylabel("Preço")
                                    plt.xticks(rotation=90)

                                    plt.title(ativo + " - Período: " + str(dataInicial.strftime("%d/%m/%Y")) + " a " + str(dataFinal.strftime("%d/%m/%Y")))
                                    plt.legend()
                                    st.pyplot(plt.gcf())

                                
                            with st.expander("Relatório Compra"):
                                
                                grid_response3 = aggrid(tabela_relatorio_compra_formatada)
                                
                                cont = 0

                                if grid_response3:

                                    resposta = pd.DataFrame(grid_response3["selected_rows"])

                                    if(len(resposta) > 0):

                                        lista_codigos = list(set(resposta['Código']))

                                        for ativo in lista_codigos:

                                            st.session_state['tabs'].append(ativo)    

                                        st.session_state['tabs'].pop(0)

                                        tabs = st.tabs(st.session_state['tabs'])

                                        qtdAbas = 0

                                        for ativo in lista_codigos:

                                            with tabs[qtdAbas]:

                                                tabela_filtrado_dados_acao = tabela_consolidado_dados_acao[tabela_consolidado_dados_acao.Ativo == ativo]  

                                                if(tipoAtivo == "cripto"):

                                                    tabela_filtrado_dados_acao.drop(['Ativo'], axis = 1, inplace = True)

                                                else:

                                                    tabela_filtrado_dados_acao.drop(['Ativo', 'index'], axis = 1, inplace = True)

                                                tabela_filtrado_resumo_acao = tabela_consolidado_resumo_acao[tabela_consolidado_resumo_acao.Ativo == ativo]


                                                tabela_filtrado_resumo_acao.drop(['Ativo'], axis = 1, inplace = True)

                                                tabela_resumo_acao_formatada = formatar_tabela_resumo_acao(tabela_filtrado_resumo_acao)

                                                st.dataframe(tabela_resumo_acao_formatada, height=422)

                                                aggrid_sem_selecao(tabela_filtrado_dados_acao)

                                                qtdAbas = qtdAbas + 1
                        
                else:
                    
                    if(estrategia == "Fechamento do dia"):
                        
                        if(len(acoes_selecionadas) > 0):
                        
                            tabela_relatorio, tabela_relatorio_venda_formatada, tabela_consolidado_dados_acao, tabela_consolidado_resumo_acao, fibonacci_consolidado, tabela_consolidado_dados_acao_sem_formatacao = venda_fechamentoDia(acoes_selecionadas, dataInicial, dataFinal, variacao_min, variacao_max, volume_min, tipoAtivo)
                            
                            tabela_top10 = top10(tabela_relatorio, compra_venda, dif_datas)
                            
                            with st.expander("Top 10"):
                                
                                aggrid_sem_selecao(tabela_top10)
                                
                            with st.expander("Fibonacci"):
                                
                                grid_response2 = aggrid_selecao_unica(fibonacci_consolidado)
                                
                                resposta_fibo = pd.DataFrame(grid_response2["selected_rows"])
                                
                                if(len(resposta_fibo) > 0):

                                    ativo = resposta_fibo.at[0, 'Ação']

                                    tabela_filtrado_dados_acao_graf = tabela_consolidado_dados_acao_sem_formatacao[tabela_consolidado_dados_acao_sem_formatacao.Ativo == ativo]  

                                    if(tipoAtivo == "cripto"):

                                        tabela_filtrado_dados_acao_graf.drop(['Ativo'], axis = 1, inplace = True)

                                    else:

                                        tabela_filtrado_dados_acao_graf.drop(['Ativo', 'index'], axis = 1, inplace = True)

                                    fibonacci_filtrado = fibonacci_consolidado[fibonacci_consolidado.Ação == ativo]

                                    datas = tabela_filtrado_dados_acao_graf['Data'].unique()

                                    plt.figure(figsize=(30,10))
                                    plt.plot(datas, tabela_filtrado_dados_acao_graf["Fechamento"], color="black", label="Preço")
                                    plt.axhline(y=fibonacci_filtrado.at[0, "Fib 100"], color="limegreen", linestyle="-", label="100%")
                                    plt.axhline(y=fibonacci_filtrado.at[0, "Fib 76.4"], color="slateblue", linestyle="-", label="76.4%")
                                    plt.axhline(y=fibonacci_filtrado.at[0, "Fib 61.8"], color="mediumvioletred", linestyle="-", label="61.8%")
                                    plt.axhline(y=fibonacci_filtrado.at[0, "Fib 50"], color="gold", linestyle="-", label="50%")
                                    plt.axhline(y=fibonacci_filtrado.at[0, "Fib 23.6"], color="darkturquoise", linestyle="-", label="23.6%")
                                    plt.axhline(y=fibonacci_filtrado.at[0, "Fib 0"], color="lightcoral", linestyle="-", label="0%")

                                    plt.ylabel("Preço")
                                    plt.xticks(rotation=90)

                                    plt.title(ativo + " - Período: " + str(dataInicial.strftime("%d/%m/%Y")) + " a " + str(dataFinal.strftime("%d/%m/%Y")))
                                    plt.legend()
                                    st.pyplot(plt.gcf())
                                    
                            with st.expander("Relatório Venda"):
                                
                                grid_response3 = aggrid(tabela_relatorio_venda_formatada)
                                
                                cont = 0

                                if grid_response3:

                                    resposta = pd.DataFrame(grid_response3["selected_rows"])

                                    if(len(resposta) > 0):

                                        lista_codigos = list(set(resposta['Código']))

                                        for ativo in lista_codigos:

                                            st.session_state['tabs'].append(ativo)    

                                        st.session_state['tabs'].pop(0)

                                        tabs = st.tabs(st.session_state['tabs'])

                                        qtdAbas = 0

                                        for ativo in lista_codigos:

                                            with tabs[qtdAbas]:

                                                tabela_filtrado_dados_acao = tabela_consolidado_dados_acao[tabela_consolidado_dados_acao.Ativo == ativo]  

                                                if(tipoAtivo == "cripto"):

                                                    tabela_filtrado_dados_acao.drop(['Ativo'], axis = 1, inplace = True)

                                                else:

                                                    tabela_filtrado_dados_acao.drop(['Ativo', 'index'], axis = 1, inplace = True)

                                                tabela_filtrado_resumo_acao = tabela_consolidado_resumo_acao[tabela_consolidado_resumo_acao.Ativo == ativo]

                                                tabela_filtrado_resumo_acao.drop(['Ativo'], axis = 1, inplace = True)

                                                tabela_resumo_acao_formatada = formatar_tabela_resumo_acao(tabela_filtrado_resumo_acao)

                                                st.dataframe(tabela_resumo_acao_formatada, height=422)

                                                aggrid_sem_selecao(tabela_filtrado_dados_acao)

                                                qtdAbas = qtdAbas + 1
                    
            else:
                    
                st.sidebar.error("O valor da variação mínima deve ser menor do que da máxima!")
                           
        else:
            
            st.sidebar.error("Selecione uma data menor do que a data atual!")
        
    else:
        
        st.sidebar.error("Selecione pelo menos uma ação!")

