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
import plotly.graph_objects as go


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


# In[ ]:


acoes_completo = pd.read_csv('./Dados/acoes.csv', sep=";")
acoes_lista = list(acoes_completo['Codigo'])
acoes_completo_indice = pd.DataFrame({'Codigo': acoes_completo['Codigo_Yahoo'], 'Indice_Bovespa': acoes_completo['Indice_Bovespa']})
acoes_indice_bovespa = acoes_completo_indice.query("Indice_Bovespa=='Sim'")

# Configura o front end

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

if 'tabs' not in st.session_state:    

    st.session_state['tabs'] = ['Consolidado']

else:
    
    del st.session_state['tabs']
    st.session_state['tabs'] = ['Consolidado']
    
st.title('Análise dados da Bolsa')

acoes_selecionadas = list(st.sidebar.multiselect('Selecione uma ou mais ações:', acoes_lista))

dataInicialExibida = date.today() - timedelta(60)

dataInicial = st.sidebar.date_input('Selecione a data inicial:', dataInicialExibida)

variacao_min = st.sidebar.number_input('Variação Mínima:')
variacao_max = st.sidebar.number_input('Variação Máxima:')
    
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
                
                for acao in acoes_selecionadas:

                    st.session_state['tabs'].append(acao)    

                tabs = st.tabs(st.session_state['tabs'])
                
                with st.spinner('Analisando os dados das ações. Aguarde...'):

                    for acao in acoes_selecionadas:

                        if(qtdAbas>1):

                            del tabela_resumo_acao

                        tabela_resumo_acao = cria_tabela_resumo_acao()

                        codigoYahoo = pd.DataFrame(acoes_completo.loc[(acoes_completo['Codigo'] == acao), 'Codigo_Yahoo'])

                        codigoYahoo = codigoYahoo.iloc[0, 0]

                        with tabs[qtdAbas+1]:

                            dados_acao_tabela = cria_dados_acao_tabela (codigoYahoo, dataInicial, dataFinal)

                            ultimoFechamentoAjustado = 0

                            for linha in dados_acao_tabela.index:

                                if(linha > 0):

                                    dados_acao_tabela.loc[linha, 'Mínima %'] = (dados_acao_tabela.at[linha - 1, 'Fechamento'] - dados_acao_tabela.at[linha, 'Mínima'])/dados_acao_tabela.at[linha - 1, 'Fechamento']*-100
                                    dados_acao_tabela.loc[linha, 'Fechamento %'] = (dados_acao_tabela.at[linha - 1, 'Fechamento'] - dados_acao_tabela.at[linha, 'Fechamento'])/dados_acao_tabela.at[linha - 1, 'Fechamento']*-100

                                else:

                                    dados_acao_tabela.loc[linha, 'Mínima %'] = 0
                                    dados_acao_tabela.loc[linha, 'Fechamento %'] = 0

                            else:

                                ultimoFechamentoAjustado = dados_acao_tabela.loc[linha, 'Fechamento'] 

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

                qtdAbas = 0
                    
                with tabs[qtdAbas]:

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




