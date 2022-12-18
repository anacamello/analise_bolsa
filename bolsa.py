#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
import pandas_datareader as pdr
from pandas_datareader import data as web
import pandas as pd
import datetime
from datetime import date, timedelta, datetime, time
import itertools
import yfinance as yf
from decimal import Decimal
import locale


# In[60]:


def formata_cores_planilha(value):
    color = 'blue' if value != 0 else 'black'
    return 'color: %s' % color

locale.setlocale(locale.LC_ALL, 'pt_BR')

acoes_completo = pd.read_csv('acoes.csv', sep=";")
acoes_lista = list(acoes_completo['Codigo'])

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

variacao = st.sidebar.slider('Selecione o intervalo da variação:', -15.0, 15.0, [-9.7, -0.9])

variacao_min = variacao[0]
variacao_max = variacao[1]

botao = st.sidebar.button('Calcular')

#Cria as abas
qtdAbas = 0

yf.pdr_override() 

if(datetime.today().time().hour > 18):
    
    dataFinal = date.today()
    
else:
    
    if(datetime.today().time().hour > 18 and datetime.today().time().minutes >= 30):
        
        dataFinal = date.today()
    
    else:
    
        dataFinal = date.today() - timedelta(1)
        
#Cria a tabela de relatório
tabela_relatorio_venda = pd.DataFrame()
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
    
            for acao in acoes_selecionadas:

                st.session_state['tabs'].append(acao)    

            tabs = st.tabs(st.session_state['tabs'])

            for acao in acoes_selecionadas:
                
                if(qtdAbas>0):
                    
                    del tabela_resumo_acao
                
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

                codigoYahoo = pd.DataFrame(acoes_completo.loc[(acoes_completo['Codigo'] == acao), 'Codigo_Yahoo'])

                codigoYahoo = codigoYahoo.iloc[0, 0]

                with tabs[qtdAbas+1]:

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
                            
                            dados_acao_tabela[[str(variacao)]].style.applymap(formata_cores_planilha)
                        
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
                        
                        if(ganho>0.75):
                            
                            tabela_relatorio_venda = tabela_relatorio_venda.append({'Código': acao, 'Variação': variacao, 'Ganho': ganho, 'Média do Volume no Período': mediaVolume, 'Preço de Entrada': precoEntrada, 'Qtd. Trades': qtdTrades, 'Qtd. Trades Positivos': qtdTradesPositivos, 'Média dos Trades Positivos': mediaTradesPositivos, 'Maior Trade Positivo': maiorTradePositivo, 'Menor Trade Positivo': menorTradePositivo, 'Resultado': resultado}, ignore_index = True)
                        
                        variacao = round(variacao + 0.1, 2)
                        linha_tabela_resumo_acao +=1
                    
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
                    
                    tabela_resumo_acao['Ganho'] = pd.Series(["{0:.2f}%".format(val) for val in tabela_resumo_acao['Ganho']], index = tabela_resumo_acao.index)
                    tabela_resumo_acao['Ganho'] = tabela_resumo_acao['Ganho'].astype(str)
                    tabela_resumo_acao['Ganho'] = tabela_resumo_acao['Ganho'].str.replace('.', ',')
                    
                    tabela_resumo_acao = tabela_resumo_acao.set_index('Variação')
                    tabela_resumo_acao = tabela_resumo_acao.T
                    st.dataframe(tabela_resumo_acao)
                    
                    #formata dados_acao_tabela
                    
                    for i in dados_acao_tabela.index:
                                    
                        dados_acao_tabela.loc[i, 'Abertura'] = locale.currency(dados_acao_tabela.at[i, 'Abertura'], grouping=True)
                        dados_acao_tabela.loc[i, 'Máxima'] = locale.currency(dados_acao_tabela.at[i, 'Máxima'], grouping=True)
                        dados_acao_tabela.loc[i, 'Mínima'] = locale.currency(dados_acao_tabela.at[i, 'Mínima'], grouping=True)
                        dados_acao_tabela.loc[i, 'Fechamento'] = locale.currency(dados_acao_tabela.at[i, 'Fechamento'], grouping=True)
                        dados_acao_tabela.loc[i, 'Fech. Ajustado'] = locale.currency(dados_acao_tabela.at[i, 'Fech. Ajustado'], grouping=True)
                        dados_acao_tabela.loc[i, 'Volume'] = locale.currency(dados_acao_tabela.at[i, 'Volume'], grouping=True)
                
                    dados_acao_tabela['Mínima %'] = pd.Series(["{0:.2f}%".format(val) for val in dados_acao_tabela['Mínima %']], index = dados_acao_tabela.index)
                    dados_acao_tabela['Mínima %'] = dados_acao_tabela['Mínima %'].astype(str)
                    dados_acao_tabela['Mínima %'] = dados_acao_tabela['Mínima %'].str.replace('.', ',')
                    
                    dados_acao_tabela['Fechamento %'] = pd.Series(["{0:.2f}%".format(val) for val in dados_acao_tabela['Fechamento %']], index = dados_acao_tabela.index)
                    dados_acao_tabela['Fechamento %'] = dados_acao_tabela['Fechamento %'].astype(str)
                    dados_acao_tabela['Fechamento %'] = dados_acao_tabela['Fechamento %'].str.replace('.', ',')
                    
                    variacao2 = round(variacao_min, 2)
                    
                    while variacao2 <= variacao_max:
                        
                        dados_acao_tabela[str(variacao2)] = pd.Series(["{0:.2f}%".format(val) for val in dados_acao_tabela[str(variacao2)]], index = dados_acao_tabela.index)
                        dados_acao_tabela[str(variacao2)] = dados_acao_tabela[str(variacao2)].astype(str)
                        dados_acao_tabela[str(variacao2)] = dados_acao_tabela[str(variacao2)].str.replace('.', ',')
                        
                        variacao2 = round(variacao2+0.1, 2)
                    
                    st.dataframe(dados_acao_tabela)
                    
                    qtdAbas = qtdAbas + 1
                    
            with tabs[0]:
                
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
                           
                for i in tabela_relatorio_venda.index:
                                    
                    tabela_relatorio_venda.loc[i, 'Média do Volume no Período'] = locale.currency(tabela_relatorio_venda.at[i, 'Média do Volume no Período'], grouping=True)
                    tabela_relatorio_venda.loc[i, 'Preço de Entrada'] = locale.currency(tabela_relatorio_venda.at[i, 'Preço de Entrada'], grouping=True)
                
                st.dataframe(tabela_relatorio_venda)
                    
        else:
            
            st.sidebar.error("Selecione uma data menor do que a data atual!")
        
    else:
        
        st.sidebar.error("Selecione pelo menos uma ação!")


# In[ ]:




