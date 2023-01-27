#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import numpy as np
import pandas_datareader as pdr
from pandas_datareader import data as web
import datetime as dt
from datetime import date
from datetime import timedelta
import itertools
import yfinance as yf
from decimal import Decimal
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier 
import plotly.graph_objects as go


# In[ ]:


def treina_modelo(opcoes_dados_selecionados):
    
    if(opcoes_dados_selecionados == 0):
        
        acoes_historico = pd.read_csv('./Dados/dados_historicos.csv', sep=",")
        
    else:
        
        acoes_historico = pd.read_csv('./Dados/dados_historicos_bovespa.csv', sep=",")
    
    with st.spinner('Treinando Modelo. Aguarde...'):

        #Cria uma massa de dados com os dados de todas as ações

        acoes_historico.drop(["Unnamed: 0"], axis = 1, inplace = True)
        acoes_historico = acoes_historico.reset_index(drop = True)
        acoes_historico = acoes_historico.dropna(axis=0)

        X_completo = acoes_historico.drop(['Previsao_Subida_Descida'], axis = 1)
        Y_completo = acoes_historico['Previsao_Subida_Descida']

        X_train_completo, X_test_completo, Y_train_completo, Y_test_completo = train_test_split(X_completo, Y_completo, test_size = 0.2)

        if(opcoes_dados_selecionados == 0):
        
            # Instânciando a árvore de decisão
            modelo = RandomForestClassifier(criterion='entropy', max_depth = 100, max_leaf_nodes = 10, min_samples_leaf = 5, min_samples_split = 10, n_estimators = 10)
            
        else:
            
            modelo = RandomForestClassifier(criterion='gini', max_depth = 500, max_leaf_nodes = 5, min_samples_leaf = 50, min_samples_split = 100, n_estimators = 50)

        # Treinando o modelo de arvore de decisão
        modelo = modelo.fit(X_train_completo, Y_train_completo)
    
    st.sidebar.success('Modelo treinado!')
    
    return modelo


# In[ ]:


def treina_modelo_fechamento():
    
    acoes_historico = pd.read_csv('./Dados/dados_historicos_bovespa_fechamento.csv', sep=",")
    
    acoes_historico.drop(["Unnamed: 0"], axis = 1, inplace = True)
    acoes_historico = acoes_historico.reset_index(drop = True)
    acoes_historico = acoes_historico.dropna(axis=0)

    acoes_historico = acoes_historico.astype({'volume': 'float16', 'Distancia_Maxima_Minima': 'float16', 'Distancia_Abertura_Minima': 'float16', 'Distancia_Abertura_Maxima': 'float16', 'Distancia_Abertura_Fechamento': 'float16', 'Distancia_Maxima_Fechamento': 'float16', 'Distancia_Minima_Fechamento': 'float16', 'Tendencia_Anterior': 'float16', 'Variacao_Periodo_Anterior': 'float16', 'Dia_Semana': 'float16', 'Previsao_Subida_Descida': 'float16'})
    acoes_historico = acoes_historico[np.isfinite(acoes_historico).all(1)] 

    X_completo = acoes_historico.drop(['Previsao_Subida_Descida'], axis = 1)
    Y_completo = acoes_historico['Previsao_Subida_Descida']

    X_train_completo, X_test_completo, Y_train_completo, Y_test_completo = train_test_split(X_completo, Y_completo, test_size = 0.2)
    
    # Instânciando a árvore de decisão
    modelo_fechamento = RandomForestClassifier(criterion='gini', max_depth = 10, max_leaf_nodes = 500, min_samples_leaf = 10, min_samples_split = 100, n_estimators = 50)

    # Treinando o modelo de arvore de decisão
    modelo_fechamento = modelo_fechamento.fit(X_train_completo, Y_train_completo)

    return modelo_fechamento


# In[ ]:


def calcula_tendencia(modelo):
    
    with st.spinner('Calculando as tendências de mínima/ máxima. Aguarde...'):
        
        acoes_completo = pd.read_csv('./Dados/acoes.csv', sep=";") 
        codigos = pd.DataFrame(acoes_completo['Codigo_Yahoo']) 
        
        dados_consolidados = pd.DataFrame()
        dados_consolidados.insert(0, "Acao", 0, allow_duplicates = False)
        dados_consolidados.insert(1, "Previsao", 0, allow_duplicates = False)
        dados_consolidados.insert(2, "Chances Descida %", 0, allow_duplicates = False)
        dados_consolidados.insert(3, "Chances Subida %", 0, allow_duplicates = False)

        dataInicial = date.today() - timedelta(5)

        hoje = dt.datetime.now()

        if(hoje.hour < 18):
    
            dataFinal = date.today()
    
        else:
    
            if(hoje.hour > 18 or (hoje.hour == 18 and hoje.minute >= 30)):
        
                dataFinal = date.today() + timedelta(1)
    
            else:
    
                dataFinal = date.today()
        
        
        linha = 0

        for i in codigos.index:

            codigo = codigos.at[i, 'Codigo_Yahoo']
            dados_acao = yf.download(codigo, dataInicial, dataFinal)
            dados_acao = dados_acao.reset_index()
            dados_acao_filtrado = pd.DataFrame({'Abertura': dados_acao['Open'], 'Volume': dados_acao['Volume'], 'Máxima': dados_acao['High'], 'Fechamento': dados_acao['Close'], 'Mínima': dados_acao['Low']})

            if(dados_acao_filtrado.notna):
                
                if(len(dados_acao) > 0):

                    for j in dados_acao.index:

                        if(dados_acao_filtrado.at[j, 'Mínima'] != 0):

                            dados_acao_filtrado.at[j, 'Distancia_Maxima_Minima'] = (dados_acao_filtrado.at[j, 'Máxima'] / dados_acao_filtrado.at[j, 'Mínima'])-1

                        else:

                            dados_acao_filtrado.at[j, 'Distancia_Maxima_Minima'] = 0

                        if(dados_acao_filtrado.at[j, 'Abertura'] != 0):

                            dados_acao_filtrado.at[j, 'Distancia_Abertura_Minima'] = (dados_acao_filtrado.at[j, 'Mínima'] / dados_acao_filtrado.at[j, 'Abertura'])-1
                            dados_acao_filtrado.at[j, 'Distancia_Abertura_Maxima'] = (dados_acao_filtrado.at[j, 'Máxima'] / dados_acao_filtrado.at[j, 'Abertura'])-1

                        else:

                            dados_acao_filtrado.at[j, 'Distancia_Abertura_Minima'] = 0
                            dados_acao_filtrado.at[j, 'Distancia_Abertura_Maxima'] = 0

                        data_string = str(dados_acao.at[j, 'Date'])
                        ano = data_string[0:4]
                        mes = data_string[5:7]
                        dia = data_string[8:10]

                        data_string_formatada = ano+mes+dia

                        data = dt.datetime(int(ano), int(mes), int(dia))

                        if(j > 0):

                            if(dados_acao.at[j, 'High'] > dados_acao.at[j-1, 'Close']):

                                dados_acao_filtrado.at[j, 'Aumento_Preco'] = 1

                            else:

                                dados_acao_filtrado.at[j, 'Aumento_Preco'] = 0
                            
                            if(dados_acao_filtrado.at[j-1, 'Fechamento'] != 0):
                                
                                dados_acao_filtrado.at[j, 'Variacao_Periodo_Anterior'] = (dados_acao_filtrado.at[j, 'Máxima'] / dados_acao_filtrado.at[j-1, 'Fechamento']) - 1

                        else:

                            dados_acao_filtrado.at[j, 'Aumento_Preco'] = 0
                            dados_acao_filtrado.at[j, 'Variacao_Periodo_Anterior'] = 0

                        dados_acao_filtrado.at[j, 'Dia_Semana'] = data.isoweekday() 

                    for k in dados_acao_filtrado.index:

                        if(k>0):

                            dados_acao_filtrado.at[k, 'Tendencia_Anterior'] = dados_acao_filtrado.at[k-1, 'Aumento_Preco']

                        else:

                            dados_acao_filtrado.at[k, 'Tendencia_Anterior'] = 0

                    dados_acao_filtrado = pd.DataFrame({'open': dados_acao_filtrado['Abertura'], 'volume': dados_acao_filtrado['Volume'], 'high': dados_acao_filtrado['Máxima'], 'close': dados_acao_filtrado['Fechamento'], 'low': dados_acao_filtrado['Mínima'], 'Distancia_Maxima_Minima':dados_acao_filtrado['Distancia_Maxima_Minima'], 'Distancia_Abertura_Minima':dados_acao_filtrado['Distancia_Abertura_Minima'], 'Distancia_Abertura_Maxima':dados_acao_filtrado['Distancia_Abertura_Maxima'],'Tendencia_Anterior': dados_acao_filtrado['Tendencia_Anterior'], 'Variacao_Periodo_Anterior': dados_acao_filtrado['Variacao_Periodo_Anterior'], 'Dia_Semana': dados_acao_filtrado['Dia_Semana']})
                    dados_acao_filtrado = dados_acao_filtrado.dropna(axis=0)
                    dados_acao_filtrado = dados_acao_filtrado.reset_index(drop=True)

                    if(len(dados_acao_filtrado) > 0):

                        dados_acao_filtrado = dados_acao_filtrado.iloc[-1]
                        dados_acao_filtrado_array = np.array(dados_acao_filtrado)
                        dados_acao_filtrado_array.reshape(-1, 1)

                        previsao = modelo.predict([dados_acao_filtrado_array])
                        previsao_percentual = modelo.predict_proba([dados_acao_filtrado_array])

                    else:

                        previsao[0] = 0
                        previsao_percentual[0][0] = 0
                        previsao_percentual[0][1] = 0

                dados_consolidados.at[linha, "Acao"] = codigo
                dados_consolidados.at[linha, "Previsao"] = previsao[0]
                dados_consolidados.at[linha, "Chances Descida %"] = previsao_percentual[0][0]
                dados_consolidados.at[linha, "Chances Subida %"] = previsao_percentual[0][1]

                linha = linha + 1

    st.sidebar.success('Tendências de mínima/ máxima calculadas.')
    
    dados_consolidados = dados_consolidados.reset_index(drop=True)
    
    return dados_consolidados


# In[ ]:


def calcula_tendencia_fechamento(modelo_fechamento):
    
    with st.spinner('Calculando as tendências de fechamento. Aguarde...'):
        
        acoes_completo = pd.read_csv('./Dados/acoes.csv', sep=";") 
        codigos = pd.DataFrame(acoes_completo[{'Codigo_Yahoo', 'Indice_Bovespa'}]) 
        
        dados_consolidados_fechamento = pd.DataFrame()
        dados_consolidados_fechamento.insert(0, "Acao", 0, allow_duplicates = False)
        dados_consolidados_fechamento.insert(1, "Previsao", 0, allow_duplicates = False)
        dados_consolidados_fechamento.insert(2, "Chances Descida %", 0, allow_duplicates = False)
        dados_consolidados_fechamento.insert(3, "Chances Subida %", 0, allow_duplicates = False)

        dataInicial = date.today() - timedelta(5)

        hoje = dt.datetime.now()

        if(hoje.hour < 18):
    
            dataFinal = date.today()
    
        else:
    
            if(hoje.hour > 18 or (hoje.hour == 18 and hoje.minute >= 30)):
        
                dataFinal = date.today() + timedelta(1)
    
            else:
    
                dataFinal = date.today()
        
        
        linha = 0

        for i in codigos.index:
            
            if(codigos.at[i, 'Indice_Bovespa'] == "Sim"):

                codigo = codigos.at[i, 'Codigo_Yahoo']
                dados_acao = yf.download(codigo, dataInicial, dataFinal)
                dados_acao = dados_acao.reset_index()
                
                if(dados_acao.notna):
                
                    if(len(dados_acao) > 0):

                        for j in dados_acao.index:

                            data_string = str(dados_acao.at[j, 'Date'])
                            ano = data_string[0:4]
                            mes = data_string[5:7]
                            dia = data_string[8:10]

                            data_string_formatada = ano+mes+dia

                            data = dt.datetime(int(ano), int(mes), int(dia))
                            
                            if(dados_acao.at[j, 'Low'] != 0 and dados_acao.at[j, 'Open'] !=0 and dados_acao.at[j, 'Close'] != 0):

                                dados_acao.at[j, 'Distancia_Maxima_Minima'] = (dados_acao.at[j, 'High'] / dados_acao.at[j, 'Low'])-1
                                dados_acao.at[j, 'Distancia_Abertura_Minima'] = (dados_acao.at[j, 'Low'] / dados_acao.at[j, 'Open'])-1
                                dados_acao.at[j, 'Distancia_Abertura_Maxima'] = (dados_acao.at[j, 'High'] / dados_acao.at[j, 'Open'])-1
                                dados_acao.at[j, 'Distancia_Abertura_Fechamento'] = (dados_acao.at[j, 'Close'] / dados_acao.at[j, 'Open'])-1
                                dados_acao.at[j, 'Distancia_Maxima_Fechamento'] = (dados_acao.at[j, 'High'] / dados_acao.at[j, 'Close'])-1
                                dados_acao.at[j, 'Distancia_Minima_Fechamento'] = (dados_acao.at[j, 'Low'] / dados_acao.at[j, 'Close'])-1
                            
                            else:
                                
                                dados_acao.at[j, 'Distancia_Maxima_Minima'] = ""
                                dados_acao.at[j, 'Distancia_Abertura_Minima'] = ""
                                dados_acao.at[j, 'Distancia_Abertura_Maxima'] = ""
                                dados_acao.at[j, 'Distancia_Abertura_Fechamento'] = ""
                                dados_acao.at[j, 'Distancia_Maxima_Fechamento'] = ""
                                dados_acao.at[j, 'Distancia_Minima_Fechamento'] = ""

                            if(j > 0):

                                dados_acao.at[j, 'Tendencia_Anterior'] = dados_acao.at[j-1, 'Aumento_Preco']
                                
                                if(dados_acao.at[j-1, 'Close'] != 0):
                                    
                                    dados_acao.at[j, 'Variacao_Periodo_Anterior'] = (dados_acao.at[j, 'High'] / dados_acao.at[j-1, 'Close'])-1

                                #Verifica se a ação subiu ou desceu em relação ao último período

                                if(dados_acao.at[j, 'Close'] > dados_acao.at[j-1, 'Close']):

                                    dados_acao.at[j, 'Aumento_Preco'] = 1

                                else:

                                    dados_acao.at[j, 'Aumento_Preco'] = 0

                                dados_acao.at[j, 'Dia_Semana'] = data.isoweekday()

                            else:

                                dados_acao.at[j, 'Tendencia_Anterior'] = 0
                                dados_acao.at[j, 'Variacao_Periodo_Anterior'] = 0
                                dados_acao.at[j, 'Aumento_Preco'] = 0

                        dados_acao.drop(["Adj Close", "Date", "Aumento_Preco", "Close", "Open", "High", "Low"], axis = 1, inplace = True)
                        dados_acao = dados_acao.dropna(axis=0)
                        dados_acao = dados_acao.reset_index(drop = True)

                        dados_acao = dados_acao.astype({'Distancia_Maxima_Minima': 'float16', 'Distancia_Abertura_Minima': 'float16', 'Distancia_Abertura_Maxima': 'float16', 'Distancia_Abertura_Fechamento': 'float16', 'Distancia_Maxima_Fechamento': 'float16', 'Distancia_Minima_Fechamento': 'float16', 'Tendencia_Anterior': 'float16', 'Variacao_Periodo_Anterior': 'float16', 'Dia_Semana': 'float16'})
                        dados_acao = dados_acao.dropna(axis=0)
                        dados_acao = dados_acao.reset_index(drop=True)

                        if(len(dados_acao) > 0):

                            dados_acao = dados_acao.iloc[-1]
                            dados_acao_array = np.array(dados_acao)
                            dados_acao_array.reshape(-1, 1)

                            previsao = modelo_fechamento.predict([dados_acao_array])
                            previsao_percentual = modelo_fechamento.predict_proba([dados_acao_array])

                        else:

                            previsao[0] = 0
                            previsao_percentual[0][0] = 0
                            previsao_percentual[0][1] = 0

                    dados_consolidados_fechamento.at[linha, "Acao"] = codigo
                    dados_consolidados_fechamento.at[linha, "Previsao"] = previsao[0]
                    dados_consolidados_fechamento.at[linha, "Chances Descida %"] = previsao_percentual[0][0]
                    dados_consolidados_fechamento.at[linha, "Chances Subida %"] = previsao_percentual[0][1]

                    linha = linha + 1

    st.sidebar.success('Tendências de fechamento calculadas.')
    
    dados_consolidados_fechamento = dados_consolidados_fechamento.reset_index(drop=True)
    
    return dados_consolidados_fechamento


# In[ ]:


def calcula_medianas():

    with st.spinner('Calculando as medianas. Aguarde...'):
        
        acoes_completo = pd.read_csv('./Dados/acoes.csv', sep=";") 
        codigos = pd.DataFrame(acoes_completo['Codigo_Yahoo']) 
        
        medianas = pd.DataFrame()
        medianas.insert(0, "Acao", 0, allow_duplicates = False)
        medianas.insert(1, "Mediana_Subida", 0, allow_duplicates = False)
        medianas.insert(2, "Mediana_Descida", 0, allow_duplicates = False)
        
        dataInicial = date.today() - timedelta(90)

        hoje = dt.datetime.now()

        if(hoje.hour < 18):
    
            dataFinal = date.today()
    
        else:
    
            if(hoje.hour > 18 or (hoje.hour == 18 and hoje.minute >= 30)):
        
                dataFinal = date.today() + timedelta(1)
    
            else:
    
                dataFinal = date.today()
        
        linha = 0
        
        for i in codigos.index:
        
            codigo_yahoo = codigos.at[i, 'Codigo_Yahoo']
            dados_acao = yf.download(codigo_yahoo, dataInicial, dataFinal)
            dados_acao = dados_acao.reset_index()
            
            dados_acao_filtrado = pd.DataFrame()
            dados_acao_filtrado.insert(0, "Acao", 0, allow_duplicates = False)
            dados_acao_filtrado.insert(1, "Abertura", 0, allow_duplicates = False)
            dados_acao_filtrado.insert(2, "Máxima", 0, allow_duplicates = False)
            dados_acao_filtrado.insert(3, "Mínima", 0, allow_duplicates = False)
            dados_acao_filtrado.insert(4, "Subida", 0, allow_duplicates = False)
            dados_acao_filtrado.insert(5, "Descida", 0, allow_duplicates = False)
            
            if(dados_acao_filtrado.notna):
            
                if(len(dados_acao) > 0):

                    for j in dados_acao.index:

                        dados_acao_filtrado.at[j, 'Acao'] = codigo_yahoo
                        dados_acao_filtrado.at[j, 'Abertura'] = dados_acao.at[j, 'Open']
                        dados_acao_filtrado.at[j, 'Máxima'] = dados_acao.at[j, 'High']
                        dados_acao_filtrado.at[j, 'Mínima'] = dados_acao.at[j, 'Low']
                        
                        if(dados_acao_filtrado.at[j, 'Abertura'] > 0):

                            dados_acao_filtrado.at[j, 'Subida'] = (dados_acao_filtrado.at[j, 'Máxima'] / dados_acao_filtrado.at[j, 'Abertura'])-1
                            dados_acao_filtrado.at[j, 'Descida'] = (dados_acao_filtrado.at[j, 'Mínima'] / dados_acao_filtrado.at[j, 'Abertura'])-1

                medianas.at[linha, 'Acao'] = codigo_yahoo
                medianas.at[linha, 'Mediana_Subida'] = dados_acao_filtrado['Subida'].median()*100
                medianas.at[linha, 'Mediana_Descida'] = dados_acao_filtrado['Descida'].median()*100

                linha = linha + 1

    st.sidebar.success('Medianas calculadas.')
    
    return medianas


# In[ ]:


acoes_completo = pd.read_csv('./Dados/acoes.csv', sep=";")
acoes_lista = list(acoes_completo['Codigo'])
acoes_completo_indice = pd.DataFrame({'Codigo': acoes_completo['Codigo_Yahoo'], 'Indice_Bovespa': acoes_completo['Indice_Bovespa']})
acoes_indice_bovespa = acoes_completo_indice.query("Indice_Bovespa=='Sim'")

# Configura o front end

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

if 'tabs' not in st.session_state:    

    st.session_state['tabs'] = ['Tendências de Subida', 'Tendências de Descida', 'IBOVESPA - Tendências de Subida - Fechamento', 'IBOVESPA - Tendências de Descida - Fechamento', 'IBOVESPA - Tendências de Subida', 'IBOVESPA - Tendências de Descida', 'IBOVESPA - Indicadores']

else:
    
    del st.session_state['tabs']
    st.session_state['tabs'] = ['Tendências de Subida - Máxima', 'Tendências de Descida - Máxima', 'IBOVESPA - Tendências de Subida - Fechamento', 'IBOVESPA - Tendências de Descida - Fechamento', 'IBOVESPA - Tendências de Subida - Máxima', 'IBOVESPA - Tendências de Descida - Máxima', 'IBOVESPA - Indicadores']
    
st.title('Análise dados da Bolsa')

opcoes_dados = st.sidebar.radio('Selecione os dados para treinar o modelo:', ('Todas as ações', 'Apenas ações do índice Bovespa'))
    
botao = st.sidebar.button('Calcular')

#Cria as abas
qtdAbas = 0

yf.pdr_override() 

hoje = dt.datetime.now()

if(hoje.hour < 18):
    
    dataFinal = date.today()
    
else:
    
    if(hoje.hour > 18 or (hoje.hour == 18 and hoje.minute >= 30)):
        
        dataFinal = date.today() + timedelta(1)
    
    else:
    
        dataFinal = date.today()
    
if botao:   
                        
    if(opcoes_dados == 'Apenas ações do índice Bovespa'):

        del st.session_state['tabs']
        st.session_state['tabs'] = ['IBOVESPA - Tendências de Subida - Fechamento', 'IBOVESPA - Tendências de Descida - Fechamento', 'IBOVESPA - Tendências de Subida - Máxima', 'IBOVESPA - Tendências de Descida - Máxima', 'IBOVESPA - Indicadores']
        
    else:

        st.session_state['tabs'] = ['Tendências de Subida - Máxima', 'Tendências de Descida - Máxima', 'IBOVESPA - Tendências de Subida - Fechamento', 'IBOVESPA - Tendências de Descida - Fechamento', 'IBOVESPA - Tendências de Subida - Máxima', 'IBOVESPA - Tendências de Descida - Máxima', 'IBOVESPA - Indicadores']

    tabs = st.tabs(st.session_state['tabs'])

    qtdAbas = 0

    if(opcoes_dados == 'Todas as ações'):

        opcoes_dados_selecionados = 0

    else:

        opcoes_dados_selecionados = 1

    modelo_treinado = treina_modelo(opcoes_dados_selecionados)
    modelo_treinado_fechamento = treina_modelo_fechamento()

    tendencias = calcula_tendencia(modelo_treinado)
    tendencias_fechamento = calcula_tendencia_fechamento(modelo_treinado_fechamento)

    resultado_medianas = calcula_medianas()
   
    merge_tendencias_medianas = pd.merge(tendencias, resultado_medianas, how = 'inner', on = 'Acao')
    
    # Tendências Positivas (Máxima em relação ao Fechamento)
    tendencias_positivas = merge_tendencias_medianas.query("Previsao==1.0")
    tendencias_positivas = pd.DataFrame({'Ação': tendencias_positivas['Acao'], 'Previsão' : 'Subida', 'Mediana Subida': tendencias_positivas['Mediana_Subida'], 'Chances de acerto': tendencias_positivas['Chances Subida %']})
    tendencias_positivas = tendencias_positivas.reset_index(drop = True)

    tendencias_positivas['Mediana Subida'] = pd.Series(["{0:.2f}%".format(val) for val in tendencias_positivas['Mediana Subida']], index = tendencias_positivas.index)
    tendencias_positivas['Mediana Subida'] = tendencias_positivas['Mediana Subida'].astype(str)
    tendencias_positivas['Mediana Subida'] = tendencias_positivas['Mediana Subida'].str.replace('.', ',')

    tendencias_positivas['Chances de acerto'] = pd.Series(["{0:.2f}%".format(val*100) for val in tendencias_positivas['Chances de acerto']], index = tendencias_positivas.index)
    tendencias_positivas['Chances de acerto'] = tendencias_positivas['Chances de acerto'].astype(str)
    tendencias_positivas['Chances de acerto'] = tendencias_positivas['Chances de acerto'].str.replace('.', ',')

    #Tendências Positivas (Fechamento em relação ao fechamento anterior)

    tendencias_positivas_fechamento = tendencias_fechamento.query("Previsao==1.0")
    tendencias_positivas_fechamento = pd.DataFrame({'Ação': tendencias_positivas_fechamento['Acao'], 'Previsão' : 'Subida', 'Chances de acerto': tendencias_positivas_fechamento['Chances Subida %']})
    tendencias_positivas_fechamento = tendencias_positivas_fechamento.reset_index(drop = True)
    
    qtd_tendencias_positivas_ibovespa_fechamento_filtrado = 0
    
    for a in tendencias_positivas_fechamento.index:
    
        if(float(tendencias_positivas_fechamento.at[a, 'Chances de acerto'])>=0.51):
            
            qtd_tendencias_positivas_ibovespa_fechamento_filtrado = qtd_tendencias_positivas_ibovespa_fechamento_filtrado + 1

    tendencias_positivas_fechamento['Chances de acerto'] = pd.Series(["{0:.2f}%".format(val*100) for val in tendencias_positivas_fechamento['Chances de acerto']], index = tendencias_positivas_fechamento.index)
    tendencias_positivas_fechamento['Chances de acerto'] = tendencias_positivas_fechamento['Chances de acerto'].astype(str)
    tendencias_positivas_fechamento['Chances de acerto'] = tendencias_positivas_fechamento['Chances de acerto'].str.replace('.', ',')

    # Tendências Negativas (Máxima em relação ao Fechamento)
    tendencias_negativas = merge_tendencias_medianas.query("Previsao==0.0")
    tendencias_negativas = pd.DataFrame({'Ação': tendencias_negativas['Acao'], 'Previsão' : 'Descida', 'Mediana Descida': tendencias_negativas['Mediana_Descida'], 'Chances de acerto': tendencias_negativas['Chances Descida %']})
    tendencias_negativas = tendencias_negativas.reset_index(drop = True)

    tendencias_negativas['Mediana Descida'] = pd.Series(["{0:.2f}%".format(val) for val in tendencias_negativas['Mediana Descida']], index = tendencias_negativas.index)
    tendencias_negativas['Mediana Descida'] = tendencias_negativas['Mediana Descida'].astype(str)
    tendencias_negativas['Mediana Descida'] = tendencias_negativas['Mediana Descida'].str.replace('.', ',')

    tendencias_negativas['Chances de acerto'] = pd.Series(["{0:.2f}%".format(val*100) for val in tendencias_negativas['Chances de acerto']], index = tendencias_negativas.index)
    tendencias_negativas['Chances de acerto'] = tendencias_negativas['Chances de acerto'].astype(str)
    tendencias_negativas['Chances de acerto'] = tendencias_negativas['Chances de acerto'].str.replace('.', ',')

    # Tendências Negativas (Fechamento em relação ao Fechamento)
    tendencias_negativas_fechamento = tendencias_fechamento.query("Previsao==0.0")
    tendencias_negativas_fechamento = pd.DataFrame({'Ação': tendencias_negativas_fechamento['Acao'], 'Previsão' : 'Descida', 'Chances de acerto': tendencias_negativas_fechamento['Chances Descida %']})
    tendencias_negativas_fechamento = tendencias_negativas_fechamento.reset_index(drop = True)
    
    qtd_tendencias_negativas_ibovespa_fechamento_filtrado = 0
    
    for b in tendencias_negativas_fechamento.index:
    
        if(float(tendencias_negativas_fechamento.at[b, 'Chances de acerto'])>=0.51):
            
            qtd_tendencias_negativas_ibovespa_fechamento_filtrado = qtd_tendencias_negativas_ibovespa_fechamento_filtrado + 1

    tendencias_negativas_fechamento['Chances de acerto'] = pd.Series(["{0:.2f}%".format(val*100) for val in tendencias_negativas_fechamento['Chances de acerto']], index = tendencias_negativas_fechamento.index)
    tendencias_negativas_fechamento['Chances de acerto'] = tendencias_negativas_fechamento['Chances de acerto'].astype(str)
    tendencias_negativas_fechamento['Chances de acerto'] = tendencias_negativas_fechamento['Chances de acerto'].str.replace('.', ',')

    if (opcoes_dados == 'Todas as ações'):

        with tabs[qtdAbas]:

            st.dataframe(tendencias_positivas)

            qtdAbas = qtdAbas + 1

        with tabs[qtdAbas]:

            st.dataframe(tendencias_negativas) 

            qtdAbas = qtdAbas + 1

    with tabs[qtdAbas]:

        st.dataframe(tendencias_positivas_fechamento) 

        qtdAbas = qtdAbas + 1

    with tabs[qtdAbas]:

        st.dataframe(tendencias_negativas_fechamento) 

        qtdAbas = qtdAbas + 1

    with tabs[qtdAbas]:

        tendencias_positivas_ibovespa = pd.DataFrame()
        tendencias_positivas_ibovespa.insert(0, "Ação", 0, allow_duplicates = False)
        tendencias_positivas_ibovespa.insert(1, "Previsão", 0, allow_duplicates = False)
        tendencias_positivas_ibovespa.insert(2, "Mediana Subida", 0, allow_duplicates = False)
        tendencias_positivas_ibovespa.insert(3, "Chances de acerto", 0, allow_duplicates = False)

        linha_tendencias_positivas = 0

        for b in tendencias_positivas.index:

            acao_codigo = tendencias_positivas.at[b, 'Ação']

            if(acao_codigo in acoes_indice_bovespa.values):

                tendencias_positivas_ibovespa.at[linha_tendencias_positivas, 'Ação'] = tendencias_positivas.at[b, 'Ação']
                tendencias_positivas_ibovespa.at[linha_tendencias_positivas, 'Previsão'] = tendencias_positivas.at[b, 'Previsão']
                tendencias_positivas_ibovespa.at[linha_tendencias_positivas, 'Mediana Subida'] = tendencias_positivas.at[b, 'Mediana Subida']
                tendencias_positivas_ibovespa.at[linha_tendencias_positivas, 'Chances de acerto'] = tendencias_positivas.at[b, 'Chances de acerto']

                linha_tendencias_positivas += 1

        qtd_tendencias_positivas_ibovespa = len(tendencias_positivas_ibovespa)
        st.dataframe(tendencias_positivas_ibovespa) 

        qtdAbas = qtdAbas + 1

    with tabs[qtdAbas]:

        tendencias_negativas_ibovespa = pd.DataFrame()
        tendencias_negativas_ibovespa.insert(0, "Ação", 0, allow_duplicates = False)
        tendencias_negativas_ibovespa.insert(1, "Previsão", 0, allow_duplicates = False)
        tendencias_negativas_ibovespa.insert(2, "Mediana Descida", 0, allow_duplicates = False)
        tendencias_negativas_ibovespa.insert(3, "Chances de acerto", 0, allow_duplicates = False)

        linha_tendencias_negativas = 0

        for c in tendencias_negativas.index:

            acao_codigo = tendencias_negativas.at[c, 'Ação']

            if(acao_codigo in acoes_indice_bovespa.values):

                tendencias_negativas_ibovespa.at[linha_tendencias_negativas, 'Ação'] = tendencias_negativas.at[c, 'Ação']
                tendencias_negativas_ibovespa.at[linha_tendencias_negativas, 'Previsão'] = tendencias_negativas.at[c, 'Previsão']
                tendencias_negativas_ibovespa.at[linha_tendencias_negativas, 'Mediana Descida'] = tendencias_negativas.at[c, 'Mediana Descida']
                tendencias_negativas_ibovespa.at[linha_tendencias_negativas, 'Chances de acerto'] = tendencias_negativas.at[c, 'Chances de acerto']

                linha_tendencias_negativas += 1

        qtd_tendencias_negativas_ibovespa = len(tendencias_negativas_ibovespa)
        st.dataframe(tendencias_negativas_ibovespa) 

        qtdAbas = qtdAbas + 1

        with tabs[qtdAbas]:

            qtd_tendencias_positivas_ibovespa_fechamento = int(len(tendencias_positivas_fechamento))
            qtd_tendencias_negativas_ibovespa_fechamento = int(len(tendencias_negativas_fechamento))
            
            if((qtd_tendencias_positivas_ibovespa_fechamento + qtd_tendencias_negativas_ibovespa_fechamento) > 0):

                percentual_subida_ibovespa_fechamento = (qtd_tendencias_positivas_ibovespa_fechamento / (qtd_tendencias_positivas_ibovespa_fechamento + qtd_tendencias_negativas_ibovespa_fechamento)) * 100
                percentual_descida_ibovespa_fechamento = (qtd_tendencias_negativas_ibovespa_fechamento / (qtd_tendencias_positivas_ibovespa_fechamento + qtd_tendencias_negativas_ibovespa_fechamento)) * - 100

            if((qtd_tendencias_positivas_ibovespa+qtd_tendencias_negativas_ibovespa)>0):

                percentual_subida_ibovespa = (qtd_tendencias_positivas_ibovespa / (qtd_tendencias_positivas_ibovespa+qtd_tendencias_negativas_ibovespa)) *100
                percentual_descida_ibovespa = (qtd_tendencias_negativas_ibovespa / (qtd_tendencias_positivas_ibovespa+qtd_tendencias_negativas_ibovespa)) *-100
            
            if((qtd_tendencias_positivas_ibovespa_fechamento_filtrado+qtd_tendencias_negativas_ibovespa_fechamento_filtrado)>0):

                percentual_subida_ibovespa_fechamento_filtrado = (qtd_tendencias_positivas_ibovespa_fechamento_filtrado / (qtd_tendencias_positivas_ibovespa_fechamento_filtrado+qtd_tendencias_negativas_ibovespa_fechamento_filtrado)) *100
                percentual_descida_ibovespa_fechamento_filtrado = (qtd_tendencias_negativas_ibovespa_fechamento_filtrado / (qtd_tendencias_positivas_ibovespa_fechamento_filtrado+qtd_tendencias_negativas_ibovespa_fechamento_filtrado)) *-100
            
            if(percentual_subida_ibovespa> (percentual_descida_ibovespa*-1)):

                st.metric("Tendência de Máxima > Fechamento Dia Anterior:", "Subida", percentual_subida_ibovespa)

            else:

                st.metric("Tendência de Máxima > Fechamento Dia Anterior:", "Descida", percentual_descida_ibovespa)

            if(percentual_subida_ibovespa_fechamento> (percentual_descida_ibovespa_fechamento*-1)):

                st.metric("Tendência de Fechamento do Dia > Fechamento Dia Anterior:", "Subida", percentual_subida_ibovespa_fechamento)

            else:

                st.metric("Tendência de Fechamento do Dia > Fechamento Dia Anterior:", "Descida", percentual_descida_ibovespa_fechamento)
                
            if(percentual_subida_ibovespa_fechamento_filtrado> (percentual_descida_ibovespa_fechamento_filtrado*-1)):

                st.metric("FILTRADO - Tendência de Fechamento do Dia > Fechamento Dia Anterior:", "Subida", percentual_subida_ibovespa_fechamento_filtrado)

            else:

                st.metric("FILTRADO -  Tendência de Fechamento do Dia > Fechamento Dia Anterior:", "Descida", percentual_descida_ibovespa_fechamento_filtrado)


            fig = go.Figure()
            fig.add_trace(go.Bar(y=['Tendência de Máxima > Fechamento Dia Anterior'], x=[percentual_subida_ibovespa], name='Subida', orientation='h', marker=dict(color='rgba(19, 141, 19, 1.0)', line=dict(color='rgba(19, 141, 19, 1.0)', width=3)))) 
            fig.add_trace(go.Bar(y=['Tendência de Máxima > Fechamento Dia Anterior'], x=[percentual_descida_ibovespa*-1], name='Descida', orientation='h', marker=dict(color='rgba(195, 11, 20, 1.0)', line=dict(color='rgba(195, 11, 20, 1.0)', width=3))))                                                                                                                                  
            fig.update_layout(barmode='stack', autosize = False, width=1000, height=220)

            st.plotly_chart(fig, theme="streamlit")

            fig = go.Figure()
            fig.add_trace(go.Bar(y=['Tendência de Fechamento do Dia > Fechamento Dia Anterior'], x=[percentual_subida_ibovespa_fechamento], name='Subida', orientation='h', marker=dict(color='rgba(19, 141, 19, 1.0)', line=dict(color='rgba(19, 141, 19, 1.0)', width=3)))) 
            fig.add_trace(go.Bar(y=['Tendência de Fechamento do Dia > Fechamento Dia Anterior'], x=[percentual_descida_ibovespa_fechamento*-1], name='Descida', orientation='h', marker=dict(color='rgba(195, 11, 20, 1.0)', line=dict(color='rgba(195, 11, 20, 1.0)', width=3))))                                                                                                                                  
            fig.update_layout(barmode='stack', autosize = False, width=1000, height=220)

            st.plotly_chart(fig, theme="streamlit")

            qtdAbas = qtdAbas + 1

