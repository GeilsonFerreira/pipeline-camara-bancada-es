# Databricks notebook source
# DBTITLE 1,Cell 1
from pyspark.sql.functions import (
    col, trim, upper, to_date, regexp_replace, coalesce, lit, current_timestamp
)

# 1. Ler os dados brutos da Bronze
df_desp_bronze = spark.read.table("dados_es.bronze.despesas_raw")

# 2. Transformações e regras de qualidade em PySpark
df_desp_silver = df_desp_bronze.select(
    col("idDeputado_fk").cast("long").alias("deputado_id"),
    trim(col("codDocumento")).alias("documento_id"),
    col("ano").cast("int").alias("ano"),
    col("mes").cast("int").alias("mes"),
    to_date(col("dataDocumento")).alias("data_documento"),
    upper(trim(col("tipoDespesa"))).alias("tipo_despesa"),
    trim(col("tipoDocumento")).alias("tipo_documento"),
    trim(col("numDocumento")).alias("numero_documento"),
    upper(trim(col("nomeFornecedor"))).alias("nome_fornecedor"),
    # Remove qualquer caractere que não seja número no CNPJ/CPF
    regexp_replace(trim(col("cnpjCpfFornecedor")), "[^0-9]", "").alias("cnpj_cpf_fornecedor"),
    # Conversão segura para Decimal (ideal para valores financeiros)
    coalesce(col("valorDocumento").cast("decimal(12,2)"), lit(0.00)).alias("valor_documento"),
    coalesce(col("valorGlosa").cast("decimal(12,2)"), lit(0.00)).alias("valor_glosa"),
    coalesce(col("valorLiquido").cast("decimal(12,2)"), lit(0.00)).alias("valor_liquido"),
    col("urlDocumento").alias("url_nota_fiscal")
)

# Remover eventuais registros sem ID de documento ou duplicados
df_desp_silver = df_desp_silver \
    .filter(col("documento_id").isNotNull()) \
    .dropDuplicates(["deputado_id", "documento_id", "valor_liquido"]) \
    .withColumn("data_processamento", current_timestamp())

# 3. Salvar como tabela Delta na Camada Silver
tabela_silver_desp = "dados_es.silver.despesas_clean"
df_desp_silver.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable(tabela_silver_desp)

print(f"Sucesso! Tabela criada: {tabela_silver_desp} | Total de registros limpos: {df_desp_silver.count()}")
display(spark.read.table(tabela_silver_desp).limit(10))
