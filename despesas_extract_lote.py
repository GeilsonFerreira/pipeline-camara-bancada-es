# Databricks notebook source
import requests
import pandas as pd

# 1. Ler os deputados da tabela Bronze
df_deputados_spark = spark.read.table("dados_es.bronze.deputados_raw")
df_deputados_pd = df_deputados_spark.select("id", "nome").toPandas()

lista_geral_despesas = []

print(f"Iniciando a extração das despesas para {len(df_deputados_pd)} deputados da bancada capixaba...")

for index, row in df_deputados_pd.iterrows():
    deputado_id = int(row["id"])
    nome_deputado = row["nome"]
    
    print(f"\n--- Coletando dados de: {nome_deputado} (ID: {deputado_id}) ---")
    
    pagina = 1
    total_deputado = 0
    
    while True:
        # URL validada sem idLegislatura=57
        url_atual = f"https://dadosabertos.camara.leg.br/api/v2/deputados/{deputado_id}/despesas?ano=2023,2024,2025,2026&itens=100&pagina={pagina}"
        
        response = requests.get(url_atual)
        
        if response.status_code == 200:
            data = response.json()
            dados_pagina = data.get("dados", [])
            
            # Se a página vier vazia, encerramos o loop deste deputado
            if len(dados_pagina) == 0:
                print(f"Concluído: {total_deputado} despesas coletadas para {nome_deputado}.")
                break
            
            # Adiciona o ID e o Nome do deputado em cada registro
            for item in dados_pagina:
                item["idDeputado_fk"] = deputado_id
                item["nomeDeputado_fk"] = nome_deputado
            
            lista_geral_despesas.extend(dados_pagina)
            total_deputado += len(dados_pagina)
            pagina += 1
        else:
            print(f"Erro HTTP {response.status_code} na página {pagina}: {response.text}")
            break

# 2. Persistir na Camada Bronze
if len(lista_geral_despesas) > 0:
    df_despesas_raw_pd = pd.DataFrame(lista_geral_despesas)
    print(f"\n==========================================")
    print(f"Total geral de registros coletados: {len(df_despesas_raw_pd)}")
    print(f"==========================================")

    df_despesas_bronze = spark.createDataFrame(df_despesas_raw_pd)
    tabela_bronze_despesas = "dados_es.bronze.despesas_raw"

    df_despesas_bronze.write \
        .format("delta") \
        .mode("overwrite") \
        .saveAsTable(tabela_bronze_despesas)

    print(f"Sucesso! Tabela Bronze criada: {tabela_bronze_despesas}")
    display(spark.read.table(tabela_bronze_despesas).limit(10))
else:
    print("\nAtenção: Nenhum registro coletado.")