#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# In[4]:


def cria_tabela_resumo_acao():
    
    #Cria a tabela de resumo da ação
    tabela_resumo_acao = pd.DataFrame()
    tabela_resumo_acao.insert(0, "Variação", 0, allow_duplicates = False)
    tabela_resumo_acao.insert(1, "Resultado", 0, allow_duplicates = False)
    tabela_resumo_acao.insert(2, "Qtd. Trades", 0, allow_duplicates = False)
    tabela_resumo_acao.insert(3, "Qtd. Trades Positivos", 0, allow_duplicates = False)
    tabela_resumo_acao.insert(4, "Média Trades Positivos", 0, allow_duplicates = False)
    tabela_resumo_acao.insert(5, "Maior Trade Positivo", 0, allow_duplicates = False)
    tabela_resumo_acao.insert(6, "Menor Trade Positivo", 0, allow_duplicates = False)
    tabela_resumo_acao.insert(7, "Ganho", 0, allow_duplicates = False)
    
    return tabela_resumo_acao


# In[5]:


def cria_dados_acao_tabela (codigoYahoo, dataInicial, dataFinal):

    dados_acao_tabela = yf.download(codigoYahoo, dataInicial, dataFinal)
    dados_acao_tabela = dados_acao_tabela.reset_index()

    dados_acao_tabela.rename(columns={'Date': 'Data'}, inplace = True)
    dados_acao_tabela.rename(columns={'Open': 'Abertura'}, inplace = True)
    dados_acao_tabela.rename(columns={'High': 'Máxima'}, inplace = True)
    dados_acao_tabela.rename(columns={'Low': 'Mínima'}, inplace = True)
    dados_acao_tabela.rename(columns={'Close': 'Fechamento'}, inplace = True)
    dados_acao_tabela.rename(columns={'Adj Close': 'Fech. Ajustado'}, inplace = True)
    dados_acao_tabela.rename(columns={'Volume': 'Volume'}, inplace = True)

    dados_acao_tabela['Data'] = dados_acao_tabela['Data'].dt.strftime('%d/%m/%Y')

    dados_acao_tabela.insert(7, "Mínima %", 0, allow_duplicates = False)
    dados_acao_tabela.insert(8, "Fechamento %", 0, allow_duplicates = False)
    
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

    tabela_resumo_acao['Ganho'] = pd.Series(["{0:.2f}%".format(val*100) for val in tabela_resumo_acao['Ganho']], index = tabela_resumo_acao.index)
    tabela_resumo_acao['Ganho'] = tabela_resumo_acao['Ganho'].astype(str)
    tabela_resumo_acao['Ganho'] = tabela_resumo_acao['Ganho'].str.replace('.', ',')

    tabela_resumo_acao = tabela_resumo_acao.set_index('Variação')
    tabela_resumo_acao = tabela_resumo_acao.T

    tabela_resumo_acao = tabela_resumo_acao.style.applymap(cor_ganho)
    
    return tabela_resumo_acao


# In[7]:


def formata_dados_acao_tabela():

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

    dados_acao_tabela['Fech. Ajustado'] = pd.Series(["R$ {0: _.2f}".format(val) for val in dados_acao_tabela['Fech. Ajustado']], index = dados_acao_tabela.index)
    dados_acao_tabela['Fech. Ajustado'] = dados_acao_tabela['Mínima'].astype(str)
    dados_acao_tabela['Fech. Ajustado'] = dados_acao_tabela['Mínima'].str.replace('.', ',')
    dados_acao_tabela['Fech. Ajustado'] = dados_acao_tabela['Mínima'].str.replace('_', '.')

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


# In[8]:


def formata_tabela_relatorio_venda(tabela_relatorio_venda):

    #Formata a tabela Relatório Venda

    tabela_relatorio_venda.sort_values(by=['Ganho', 'Média do Volume no Período'], inplace = True, ascending=False)
    tabela_relatorio_venda = tabela_relatorio_venda.reset_index(drop = True)

    tabela_relatorio_venda['Variação'] = pd.Series(["{0:.2f}%".format(val) for val in tabela_relatorio_venda['Variação']], index = tabela_relatorio_venda.index)
    tabela_relatorio_venda['Variação'] = tabela_relatorio_venda['Variação'].astype(str)
    tabela_relatorio_venda['Variação'] = tabela_relatorio_venda['Variação'].str.replace('.', ',')

    tabela_relatorio_venda['Ganho'] = pd.Series(["{0:.2f}%".format(val * 100) for val in tabela_relatorio_venda['Ganho']], index = tabela_relatorio_venda.index)
    tabela_relatorio_venda['Ganho'] = tabela_relatorio_venda['Ganho'].astype(str)
    tabela_relatorio_venda['Ganho'] = tabela_relatorio_venda['Ganho'].str.replace('.', ',')

    tabela_relatorio_venda['Média dos Trades Positivos'] = pd.Series(["{0:.2f}%".format(val) for val in tabela_relatorio_venda['Média dos Trades Positivos']], index = tabela_relatorio_venda.index)
    tabela_relatorio_venda['Média dos Trades Positivos'] = tabela_relatorio_venda['Média dos Trades Positivos'].astype(str)
    tabela_relatorio_venda['Média dos Trades Positivos'] = tabela_relatorio_venda['Média dos Trades Positivos'].str.replace('.', ',')

    tabela_relatorio_venda['Maior Trade Positivo'] = pd.Series(["{0:.2f}%".format(val) for val in tabela_relatorio_venda['Maior Trade Positivo']], index = tabela_relatorio_venda.index)
    tabela_relatorio_venda['Maior Trade Positivo'] = tabela_relatorio_venda['Maior Trade Positivo'].astype(str)
    tabela_relatorio_venda['Maior Trade Positivo'] = tabela_relatorio_venda['Maior Trade Positivo'].str.replace('.', ',')

    tabela_relatorio_venda['Menor Trade Positivo'] = pd.Series(["{0:.2f}%".format(val) for val in tabela_relatorio_venda['Menor Trade Positivo']], index = tabela_relatorio_venda.index)
    tabela_relatorio_venda['Menor Trade Positivo'] = tabela_relatorio_venda['Menor Trade Positivo'].astype(str)
    tabela_relatorio_venda['Menor Trade Positivo'] = tabela_relatorio_venda['Menor Trade Positivo'].str.replace('.', ',')

    tabela_relatorio_venda['Resultado'] = pd.Series(["{0:.2f}%".format(val) for val in tabela_relatorio_venda['Resultado']], index = tabela_relatorio_venda.index)
    tabela_relatorio_venda['Resultado'] = tabela_relatorio_venda['Resultado'].astype(str)
    tabela_relatorio_venda['Resultado'] = tabela_relatorio_venda['Resultado'].str.replace('.', ',')

    tabela_relatorio_venda['Média do Volume no Período'] = pd.Series(["R$ {0:_.2f}".format(val) for val in tabela_relatorio_venda['Média do Volume no Período']], index = tabela_relatorio_venda.index)
    tabela_relatorio_venda['Média do Volume no Período'] = tabela_relatorio_venda['Média do Volume no Período'].astype(str)
    tabela_relatorio_venda['Média do Volume no Período'] = tabela_relatorio_venda['Média do Volume no Período'].str.replace('.', ',')
    tabela_relatorio_venda['Média do Volume no Período'] = tabela_relatorio_venda['Média do Volume no Período'].str.replace('_', '.')

    tabela_relatorio_venda['Preço de Entrada'] = pd.Series(["R$ {0: _.2f}".format(val) for val in tabela_relatorio_venda['Preço de Entrada']], index = tabela_relatorio_venda.index)
    tabela_relatorio_venda['Preço de Entrada'] = tabela_relatorio_venda['Preço de Entrada'].astype(str)
    tabela_relatorio_venda['Preço de Entrada'] = tabela_relatorio_venda['Preço de Entrada'].str.replace('.', ',')
    tabela_relatorio_venda['Preço de Entrada'] = tabela_relatorio_venda['Preço de Entrada'].str.replace('_', '.')
    
    return tabela_relatorio_venda


# In[ ]:


def cor_ganho(val):
    
    val = str(val)
    val = val.replace('%', '')
    val = val.replace(',', '.')
    cor_background = 'forestgreen' if float(val) > 75.00 else 'white'
    cor_letra = 'white' if float(val) > 75.00 else 'black'
    return f'background-color: {cor_background}; color:{cor_letra}'


# In[9]:


def treina_modelo():
    
    with st.spinner('Treinando Modelo. Aguarde...'):
    
        acoes_historico = pd.read_csv('dados_historicos.csv', sep=",")

        #Cria uma massa de dados com os dados de todas as ações

        acoes_historico.drop(["Unnamed: 0"], axis = 1, inplace = True)
        acoes_historico = acoes_historico.reset_index(drop = True)
        acoes_historico = acoes_historico.dropna(axis=0)

        X_completo = acoes_historico.drop(['Previsao_Subida_Descida'], axis = 1)
        Y_completo = acoes_historico['Previsao_Subida_Descida']

        X_train_completo, X_test_completo, Y_train_completo, Y_test_completo = train_test_split(X_completo, Y_completo, test_size = 0.2)

        # Instânciando a árvore de decisão
        modelo = RandomForestClassifier(criterion='gini', max_depth = 100, max_leaf_nodes = 500, min_samples_leaf = 100, min_samples_split = 100, n_estimators = 10)

        # Treinando o modelo de arvore de decisão
        modelo = modelo.fit(X_train_completo, Y_train_completo)
    
    st.sidebar.success('Modelo treinado!')
    
    return modelo


# In[ ]:


def calcula_tendencia(modelo):
    
    with st.spinner('Calculando as tendências. Aguarde...'):
        
        acoes_completo = pd.read_csv('acoes.csv', sep=";") 
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
    
            if(hoje.hour > 18 and hoje.minute >= 30):
        
                dataFinal = date.today() + timedelta(1)
    
            else:
    
                dataFinal = date.today()
        
        linha = 0

        for i in codigos.index:

            codigo = codigos.at[i, 'Codigo_Yahoo']
            dados_acao = yf.download(codigo, dataInicial, dataFinal)
            dados_acao = dados_acao.reset_index()
            dados_acao_filtrado = pd.DataFrame({'Abertura': dados_acao['Open'], 'Volume': dados_acao['Volume'], 'Máxima': dados_acao['High'], 'Fechamento': dados_acao['Adj Close'], 'Mínima': dados_acao['Low']})

            if(len(dados_acao) > 0):

                for j in dados_acao.index:
                    
                    dados_acao_filtrado.at[j, 'Distancia_Maxima_Minima'] = (dados_acao_filtrado.at[j, 'Máxima'] / dados_acao_filtrado.at[j, 'Mínima'])-1
                    dados_acao_filtrado.at[j, 'Distancia_Abertura_Minima'] = (dados_acao_filtrado.at[j, 'Mínima'] / dados_acao_filtrado.at[j, 'Abertura'])-1
                    dados_acao_filtrado.at[j, 'Distancia_Abertura_Maxima'] = (dados_acao_filtrado.at[j, 'Máxima'] / dados_acao_filtrado.at[j, 'Abertura'])-1
            
                    data_string = str(dados_acao.at[j, 'Date'])
                    ano = data_string[0:4]
                    mes = data_string[5:7]
                    dia = data_string[8:10]

                    data_string_formatada = ano+mes+dia

                    data = dt.datetime(int(ano), int(mes), int(dia))

                    if(j > 0):

                        if(dados_acao.at[j, 'High'] > dados_acao.at[j-1, 'Adj Close']):

                            dados_acao_filtrado.at[j, 'Aumento_Preco'] = 1

                        else:

                            dados_acao_filtrado.at[j, 'Aumento_Preco'] = 0

                        dados_acao_filtrado.at[j, 'Variacao_Periodo_Anterior'] = (dados_acao_filtrado.at[j, 'Máxima'] / dados_acao_filtrado.at[j-1, 'Fechamento']) - 1

                    else:

                        dados_acao_filtrado.at[j, 'Aumento_Preco'] = 0
                        dados_acao_filtrado.at[j, 'Variacao_Periodo_Anterior'] = 0

                    dados_acao_filtrado.at[j, 'Dia_Semana'] = data.isoweekday() 

                for i in dados_acao_filtrado.index:

                    if(j>0):

                        dados_acao_filtrado.at[j, 'Tendencia_Anterior'] = dados_acao_filtrado.at[j-1, 'Aumento_Preco']

                    else:

                        dados_acao_filtrado.at[j, 'Tendencia_Anterior'] = 0

                dados_acao_filtrado = pd.DataFrame({'open': dados_acao_filtrado['Abertura'], 'volume': dados_acao_filtrado['Volume'], 'high': dados_acao_filtrado['Máxima'], 'close': dados_acao_filtrado['Fechamento'], 'low': dados_acao_filtrado['Mínima'], 'Distancia_Maxima_Minima':dados_acao_filtrado['Distancia_Maxima_Minima'], 'Distancia_Abertura_Minima':dados_acao_filtrado['Distancia_Abertura_Minima'], 'Distancia_Abertura_Maxima':dados_acao_filtrado['Distancia_Abertura_Maxima'],'Tendencia_Anterior': dados_acao_filtrado['Tendencia_Anterior'], 'Variacao_Periodo_Anterior': dados_acao_filtrado['Variacao_Periodo_Anterior'], 'Dia_Semana': dados_acao_filtrado['Dia_Semana']})
                dados_acao_filtrado = dados_acao_filtrado.reset_index(drop=True)

                dados_acao_filtrado = dados_acao_filtrado.iloc[-1]
                dados_acao_filtrado_array = np.array(dados_acao_filtrado)
                dados_acao_filtrado_array.reshape(-1, 1)

                previsao = modelo.predict([dados_acao_filtrado_array])
                previsao_percentual = modelo.predict_proba([dados_acao_filtrado_array])

            dados_consolidados.at[linha, "Acao"] = codigo
            dados_consolidados.at[linha, "Previsao"] = previsao[0]
            dados_consolidados.at[linha, "Chances Descida %"] = previsao_percentual[0][0]
            dados_consolidados.at[linha, "Chances Subida %"] = previsao_percentual[0][1]

            linha += 1

    st.sidebar.success('Tendências calculadas.')
    
    dados_consolidados = dados_consolidados.reset_index(drop=True)
    
    return dados_consolidados


# In[ ]:


acoes_completo = pd.read_csv('acoes.csv', sep=";")
acoes_lista = list(acoes_completo['Codigo'])
acoes_completo_indice = pd.DataFrame({'Codigo': acoes_completo['Codigo_Yahoo'], 'Indice_Bovespa': acoes_completo['Indice_Bovespa']})
acoes_indice_bovespa = acoes_completo_indice.query("Indice_Bovespa=='Sim'")

# Configura o front end

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

if 'tabs' not in st.session_state:    

    st.session_state['tabs'] = ['Tendências de Subida', 'Tendências de Descida', 'IBOVESPA - Tendências de Subida', 'IBOVESPA - Tendências de Descida', 'Consolidado']

else:
    
    del st.session_state['tabs']
    st.session_state['tabs'] = ['Tendências de Subida', 'Tendências de Descida', 'IBOVESPA - Tendências de Subida', 'IBOVESPA - Tendências de Descida', 'Consolidado']
    
st.title('Análise dados da Bolsa')

acoes_selecionadas = list(st.sidebar.multiselect('Selecione uma ou mais ações:', acoes_lista))

dataInicialExibida = date.today() - timedelta(60)

dataInicial = st.sidebar.date_input('Selecione a data inicial:', dataInicialExibida)

variacao_min = st.sidebar.number_input('Variação Mínima:')
variacao_max = st.sidebar.number_input('Variação Máxima:')

incluir_previsao_subida_descida = st.sidebar.checkbox("Incluir relatórios de tendências.")

botao = st.sidebar.button('Calcular')

#Cria as abas
qtdAbas = 0

yf.pdr_override() 

dataInicial = date.today() - timedelta(5)

hoje = dt.datetime.now()

if(hoje.hour < 18):
    
    dataFinal = date.today()
    
else:
    
    if(hoje.hour > 18 and hoje.minute >= 30):
        
        dataFinal = date.today() + timedelta(1)
    
    else:
    
        dataFinal = date.today()

tabela_relatorio_venda = pd.DataFrame()

#Cria a tabela de relatório
tabela_relatorio_venda.insert(0, "Código", 0, allow_duplicates = False)
tabela_relatorio_venda.insert(1, "Variação", 0, allow_duplicates = False)
tabela_relatorio_venda.insert(2, "Ganho", 0, allow_duplicates = False)
tabela_relatorio_venda.insert(3, "Média do Volume no Período", 0, allow_duplicates = False)
tabela_relatorio_venda.insert(4, "Preço de Entrada", 0, allow_duplicates = False)
tabela_relatorio_venda.insert(5, "Qtd. Trades", 0, allow_duplicates = False)
tabela_relatorio_venda.insert(6, "Qtd. Trades Positivos", 0, allow_duplicates = False)
tabela_relatorio_venda.insert(7, "Média dos Trades Positivos", 0, allow_duplicates = False)
tabela_relatorio_venda.insert(8, "Maior Trade Positivo", 0, allow_duplicates = False)
tabela_relatorio_venda.insert(9, "Menor Trade Positivo", 0, allow_duplicates = False)
tabela_relatorio_venda.insert(10, "Resultado", 0, allow_duplicates = False)

if botao:   
    
    if(len(acoes_selecionadas)> 0):
        
        if(dataInicial<date.today()):
            
            if(variacao_min < variacao_max):
                
                if(incluir_previsao_subida_descida):
                    
                    qtdAbas = 4
                    
                else:
                    
                    del st.session_state['tabs']
                    st.session_state['tabs'] = ['Consolidado']
    
                for acao in acoes_selecionadas:

                    st.session_state['tabs'].append(acao)    

                tabs = st.tabs(st.session_state['tabs'])
                
                with st.spinner('Analisando os dados das ações. Aguarde...'):

                    for acao in acoes_selecionadas:

                        if(qtdAbas>4):

                            del tabela_resumo_acao

                        tabela_resumo_acao = cria_tabela_resumo_acao()

                        codigoYahoo = pd.DataFrame(acoes_completo.loc[(acoes_completo['Codigo'] == acao), 'Codigo_Yahoo'])

                        codigoYahoo = codigoYahoo.iloc[0, 0]

                        with tabs[qtdAbas+1]:

                            dados_acao_tabela = cria_dados_acao_tabela (codigoYahoo, dataInicial, dataFinal)

                            ultimoFechamentoAjustado = 0

                            for linha in dados_acao_tabela.index:

                                if(linha > 0):

                                    dados_acao_tabela.loc[linha, 'Mínima %'] = (dados_acao_tabela.at[linha - 1, 'Fech. Ajustado'] - dados_acao_tabela.at[linha, 'Mínima'])/dados_acao_tabela.at[linha - 1, 'Fech. Ajustado']*-100
                                    dados_acao_tabela.loc[linha, 'Fechamento %'] = (dados_acao_tabela.at[linha - 1, 'Fech. Ajustado'] - dados_acao_tabela.at[linha, 'Fech. Ajustado'])/dados_acao_tabela.at[linha - 1, 'Fech. Ajustado']*-100

                                else:

                                    dados_acao_tabela.loc[linha, 'Mínima %'] = 0
                                    dados_acao_tabela.loc[linha, 'Fechamento %'] = 0

                            else:

                                ultimoFechamentoAjustado = dados_acao_tabela.loc[linha, 'Fech. Ajustado'] 

                            variacao = round(variacao_min, 2)
                            coluna = 9
                            linha_tabela_resumo_acao = 0

                            while variacao <= variacao_max:

                                dados_acao_tabela.insert(coluna, str(variacao), 0, allow_duplicates = False)
                                tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Variação'] = variacao
                                resultado = 0
                                qtdTrades = 0
                                qtdTradesPositivos = 0
                                somaTradesPositivos = 0
                                maiorTradePositivo = 0
                                menorTradePositivo = 0
                                mediaTradesPositivos = 0
                                ganho = 0

                                for linha in dados_acao_tabela.index:

                                    if(dados_acao_tabela.loc[linha, 'Mínima %'] < variacao):

                                        dados_acao_tabela.loc[linha, str(variacao)] = round((variacao - dados_acao_tabela.loc[linha, 'Fechamento %']) *-1, 2)
                                        resultado += dados_acao_tabela.loc[linha, str(variacao)]

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

                                        dados_acao_tabela.loc[linha, str(variacao)] = round(0.0, 2)

                                coluna += 1

                                tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Resultado'] = resultado
                                tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Qtd. Trades'] = qtdTrades
                                tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Qtd. Trades Positivos'] = qtdTradesPositivos

                                if(qtdTradesPositivos > 0):

                                    mediaTradesPositivos = somaTradesPositivos/qtdTradesPositivos

                                else:

                                    mediaTradesPositivos = 0

                                tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Média Trades Positivos'] = mediaTradesPositivos
                                tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Maior Trade Positivo'] = maiorTradePositivo
                                tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Menor Trade Positivo'] = menorTradePositivo

                                if(qtdTrades > 0):

                                     ganho = qtdTradesPositivos/qtdTrades

                                tabela_resumo_acao.loc[linha_tabela_resumo_acao, 'Ganho'] = ganho

                                mediaVolume = dados_acao_tabela['Volume'].mean() 

                                precoEntrada = ultimoFechamentoAjustado * (1+variacao/100)

                                if(ganho>0.75  and mediaVolume > 100000): 

                                    tabela_relatorio_venda = tabela_relatorio_venda.append({'Código': acao, 'Variação': variacao, 'Ganho': ganho, 'Média do Volume no Período': mediaVolume, 'Preço de Entrada': precoEntrada, 'Qtd. Trades': qtdTrades, 'Qtd. Trades Positivos': qtdTradesPositivos, 'Média dos Trades Positivos': mediaTradesPositivos, 'Maior Trade Positivo': maiorTradePositivo, 'Menor Trade Positivo': menorTradePositivo, 'Resultado': resultado}, ignore_index = True)

                                variacao = round(variacao + 0.1, 2)
                                linha_tabela_resumo_acao +=1

                            tabela_resumo_acao_formatada = formatar_tabela_resumo_acao(tabela_resumo_acao)

                            st.dataframe(tabela_resumo_acao_formatada)

                            formata_dados_acao_tabela()

                            variacao2 = round(variacao_min, 2)

                            while variacao2 <= variacao_max:

                                dados_acao_tabela[str(variacao2)] = pd.Series(["{0:.2f}%".format(val) for val in dados_acao_tabela[str(variacao2)]], index = dados_acao_tabela.index)
                                dados_acao_tabela[str(variacao2)] = dados_acao_tabela[str(variacao2)].astype(str)
                                dados_acao_tabela[str(variacao2)] = dados_acao_tabela[str(variacao2)].str.replace('.', ',')

                                variacao2 = round(variacao2+0.1, 2)

                            st.dataframe(dados_acao_tabela)

                            qtdAbas = qtdAbas + 1
                            
                    st.sidebar.success('Dados analisados!')

                if(incluir_previsao_subida_descida):
                    
                    num_aba = 4
                    
                    modelo_treinado = treina_modelo()
                    tendencias = calcula_tendencia(modelo_treinado)
                    
                    with tabs[0]:
                        
                        tendencias_positivas = tendencias.query("Previsao==1.0")
                        tendencias_positivas = pd.DataFrame({'Ação': tendencias_positivas['Acao'], 'Previsão' : 'Subida', '% Chances de acerto': tendencias_positivas['Chances Subida %']})
                        
                        tendencias_positivas['% Chances de acerto'] = pd.Series(["{0:.2f}%".format(val*100) for val in tendencias_positivas['% Chances de acerto']], index = tendencias_positivas.index)
                        tendencias_positivas['% Chances de acerto'] = tendencias_positivas['% Chances de acerto'].astype(str)
                        tendencias_positivas['% Chances de acerto'] = tendencias_positivas['% Chances de acerto'].str.replace('.', ',')

                        tendencias_positivas = tendencias_positivas.reset_index(drop = True)
                        
                        st.dataframe(tendencias_positivas)
                        
                    with tabs[1]:
                        
                        tendencias_negativas = tendencias.query("Previsao==0.0")
                        tendencias_negativas = pd.DataFrame({'Ação': tendencias_negativas['Acao'], 'Previsão' : 'Descida', '% Chances de acerto': tendencias_negativas['Chances Descida %']})
                        tendencias_negativas = tendencias_negativas.reset_index(drop = True)
                        
                        tendencias_negativas['% Chances de acerto'] = pd.Series(["{0:.2f}%".format(val*100) for val in tendencias_negativas['% Chances de acerto']], index = tendencias_negativas.index)
                        tendencias_negativas['% Chances de acerto'] = tendencias_negativas['% Chances de acerto'].astype(str)
                        tendencias_negativas['% Chances de acerto'] = tendencias_negativas['% Chances de acerto'].str.replace('.', ',')
                        
                        st.dataframe(tendencias_negativas) 
                        
                    with tabs[2]:
                        
                        tendencias_positivas_ibovespa = pd.DataFrame()
                        tendencias_positivas_ibovespa.insert(0, "Ação", 0, allow_duplicates = False)
                        tendencias_positivas_ibovespa.insert(1, "Previsão", 0, allow_duplicates = False)
                        tendencias_positivas_ibovespa.insert(2, "% Chances de acerto", 0, allow_duplicates = False)
                        
                        linha_tendencias_positivas = 0
                        
                        for b in tendencias_positivas.index:
                            
                            acao_codigo = tendencias_positivas.at[b, 'Ação']
                            
                            if(acao_codigo in acoes_indice_bovespa.values):
                                
                                tendencias_positivas_ibovespa.at[linha_tendencias_positivas, 'Ação'] = tendencias_positivas.at[b, 'Ação']
                                tendencias_positivas_ibovespa.at[linha_tendencias_positivas, 'Previsão'] = tendencias_positivas.at[b, 'Previsão']
                                tendencias_positivas_ibovespa.at[linha_tendencias_positivas, '% Chances de acerto'] = tendencias_positivas.at[b, '% Chances de acerto']
                                
                                linha_tendencias_positivas += 1

                        st.dataframe(tendencias_positivas_ibovespa) 
                        
                    with tabs[3]:
                        
                        tendencias_negativas_ibovespa = pd.DataFrame()
                        tendencias_negativas_ibovespa.insert(0, "Ação", 0, allow_duplicates = False)
                        tendencias_negativas_ibovespa.insert(1, "Previsão", 0, allow_duplicates = False)
                        tendencias_negativas_ibovespa.insert(2, "% Chances de acerto", 0, allow_duplicates = False)
                        
                        linha_tendencias_negativas = 0
                        
                        for c in tendencias_negativas.index:
                            
                            acao_codigo = tendencias_negativas.at[c, 'Ação']
                            
                            if(acao_codigo in acoes_indice_bovespa.values):
                                
                                tendencias_negativas_ibovespa.at[linha_tendencias_negativas, 'Ação'] = tendencias_negativas.at[c, 'Ação']
                                tendencias_negativas_ibovespa.at[linha_tendencias_negativas, 'Previsão'] = tendencias_negativas.at[c, 'Previsão']
                                tendencias_negativas_ibovespa.at[linha_tendencias_negativas, '% Chances de acerto'] = tendencias_negativas.at[c, '% Chances de acerto']
                                
                                linha_tendencias_negativas += 1

                        st.dataframe(tendencias_negativas_ibovespa) 
                    
                else:
                    
                    num_aba = 0
                    
                with tabs[num_aba]:

                    num_linha = 0

                    if(len(tabela_relatorio_venda) > 0):

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

                        if(codigo_posterior == codigo and qtdTrades == qtdTrades_posterior and qtdTradesPositivos == qtdTradesPositivos_posterior and resultado_posterior < resultado):

                            tabela_relatorio_venda.drop(labels = num_linha + 1, axis = 0, inplace = True)
                            tabela_relatorio_venda = tabela_relatorio_venda.reset_index(drop = True)

                        else:

                            num_linha = num_linha + 1

                        if(num_linha >= len(tabela_relatorio_venda) -1):

                            continua = False
                    
                    tabela_relatorio_venda = formata_tabela_relatorio_venda(tabela_relatorio_venda)
                    
                    st.dataframe(tabela_relatorio_venda)
                    
            else:
                    
                st.sidebar.error("O valor da variação mínima deve ser menor do que da máxima!")
                           
        else:
            
            st.sidebar.error("Selecione uma data menor do que a data atual!")
        
    else:
        
        st.sidebar.error("Selecione pelo menos uma ação!")


# In[ ]:




