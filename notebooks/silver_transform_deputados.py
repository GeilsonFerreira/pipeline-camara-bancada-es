# Databricks notebook source
# DBTITLE 1,Cell 1
from pyspark.sql.functions import col, trim, upper, current_timestamp

#1 - Ler dados brutos da Bronze
df_dep_bronze = spark.read.table('dados_es.bronze.deputados_raw')

#2 Aplicar regras de qualidade:ripagem explícita, limpeza de espaços e padrão snake_case
df_dep_silver = df_dep_bronze.select(
    col('id').cast('long').alias('deputado_id'),
    trim(col('nome')).alias('nome_deputado'),
    upper(trim(col('siglaPartido'))).alias('sigla_partido'),
    upper(trim(col('siglaUf'))).alias('sigla_uf'),
    col('idLegislatura').cast('int').alias('legislatura_id'),
    col('email').alias('email'),
    col('urlFoto').alias('url_foto')
).dropDuplicates(['deputado_id']) \
.withColumn('data_processamento', current_timestamp())



# COMMAND ----------


#Salvar como tabela Delta na camada Silver
tabela_silver_dep = 'dados_es.silver.deputados_clean'
df_dep_silver.write \
    .format('delta') \
    .mode('overwrite') \
    .saveAsTable(tabela_silver_dep)

print(f'Sucesso! Tabela criada: {tabela_silver_dep} Total de registros: {df_dep_silver.count()}')
display(spark.read.table(tabela_silver_dep))