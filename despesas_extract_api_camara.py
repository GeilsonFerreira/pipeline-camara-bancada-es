# Databricks notebook source
# DBTITLE 1,Cell 1
import requests
import pandas as pd

#Definindo o ID do deputado a URL base do endpoint de despesas
deputado_id = 204356
URL = f'https://dadosabertos.camara.leg.br/api/v2/deputados/{deputado_id}/despesas'

#Parametros iniciais da requisição
#Limite de 100 registros por requisição
params = {	
    'idLegislatura': 57, 
    'ano': '2023, 2024, 2025, 2026', 
    'ordem': 'ASC', 
	'ordenarPor': 'ano',
    'itens': 100 
}

todas_despesas = []
pagina = 1
url = URL

print(f'iniciando a extração das despesas do deputado {deputado_id}')

#Navegar pelas páginas

while url:
    print(f'baixando a página {pagina}...')
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        #adicionando os registros da página atual na lista
        dados_pagina = data.get('dados', [])
        todas_despesas.extend(dados_pagina)

        #A API da Câmara retorna uma lista de links de navegação
        #Vamos procurar qual deles tem o 'rel': 'next'
        links = data.get('links', [])
        url_proxima = None
        for link in links:
            if link.get('rel') == 'next':
                url_proxima = link.get('href')
                break

        #Atualizando a URL da próxima página
        url = url_proxima

        #A URL do 'next' já vem com todos os parâmetros embutidos pelo servidor da Câmara.
        # Portanto, zeramos o dicionário 'params' para evitar conflito nas próximas voltas do loop.
        params = None
        pagina += 1

    else:
        print(f'Erro ao baixar a página {pagina}. Código de status: {response.status_code}')
        break

#Converte a lista completa em um DataFrame do Pandas
df_gastos_deputados = pd.DataFrame(todas_despesas)
display(df_gastos_deputados)
