# Databricks notebook source
# MAGIC %md
# MAGIC # Extrair dados da API da Câmara

# COMMAND ----------

# MAGIC %md
# MAGIC Utilizando a biblioteca requests do Python, vamos extrair as informações que queremos o endpoint disponibilizado pela API da Câmara

# COMMAND ----------

import requests
import pandas as pd

URL = 'https://dadosabertos.camara.leg.br/api/v2/deputados?siglaUf=ES&ordem=ASC&ordenarPor=nome'

response = requests.get(URL)
deputados_df = pd.DataFrame(response.json()['dados'])
display(deputados_df)


# COMMAND ----------

# MAGIC %md
# MAGIC ## Salvar os dados no Databricks

# COMMAND ----------

# MAGIC %md
# MAGIC Agora vamos salvar os dados retornados em na camada bronze do Databricks

# COMMAND ----------

#Converter do DataFrame do Pandas para o Spark DataFrame
deputados_df_bronze = spark.createDataFrame(deputados_df)

#Definir o nome da tabela na camada Bronze
tabela_bronze = 'dados_es.bronze.deputados_raw'

#Salvar como tabela Delta na camara Bronze
deputados_df_bronze \
    .write \
    .format('delta') \
    .mode('overwrite') \
    .saveAsTable(tabela_bronze)
print(f'Sucesso! Dados salvos na tabela bronze: {tabela_bronze}')