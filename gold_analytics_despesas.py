# Databricks notebook source
# MAGIC %sql
# MAGIC -- 1. Garantir que o schema Gold existe
# MAGIC CREATE SCHEMA IF NOT EXISTS dados_es.gold;
# MAGIC
# MAGIC -- 2. Criar a tabela analítica Gold cruzando Deputados e Despesas
# MAGIC CREATE OR REPLACE TABLE dados_es.gold.resumo_despesas_deputado AS
# MAGIC SELECT 
# MAGIC     d.deputado_id,
# MAGIC     d.nome_deputado,
# MAGIC     d.sigla_partido,
# MAGIC     d.sigla_uf,
# MAGIC     COUNT(f.documento_id) AS total_notas_fiscais,
# MAGIC     SUM(f.valor_documento) AS valor_total_bruto,
# MAGIC     SUM(f.valor_glosa) AS valor_total_glosado,
# MAGIC     SUM(f.valor_liquido) AS valor_total_liquido,
# MAGIC     ROUND(AVG(f.valor_liquido), 2) AS ticket_medio_despesa,
# MAGIC     MIN(f.data_documento) AS primeira_despesa,
# MAGIC     MAX(f.data_documento) AS ultima_despesa
# MAGIC FROM dados_es.silver.despesas_clean f
# MAGIC JOIN dados_es.silver.deputados_clean d 
# MAGIC     ON f.deputado_id = d.deputado_id
# MAGIC GROUP BY 
# MAGIC     d.deputado_id,
# MAGIC     d.nome_deputado,
# MAGIC     d.sigla_partido,
# MAGIC     d.sigla_uf
# MAGIC ORDER BY 
# MAGIC     valor_total_liquido DESC;
# MAGIC
# MAGIC -- 3. Visualizar o resultado pronto para consumo analítico / dashboard
# MAGIC SELECT * FROM dados_es.gold.resumo_despesas_deputado;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE dados_es.gold.resumo_despesas_deputado AS
# MAGIC SELECT 
# MAGIC     d.deputado_id,
# MAGIC     d.nome_deputado,
# MAGIC     d.sigla_partido,
# MAGIC     d.sigla_uf,
# MAGIC     COUNT(f.documento_id) AS total_notas_fiscais,
# MAGIC     CAST(SUM(f.valor_documento) AS DECIMAL(12,2)) AS valor_total_bruto,
# MAGIC     CAST(SUM(f.valor_glosa) AS DECIMAL(12,2)) AS valor_total_glosado,
# MAGIC     -- Multiplicamos por -1 para refletir o gasto real positivo (mantendo estornos como subtração)
# MAGIC     CAST(SUM(f.valor_liquido * -1) AS DECIMAL(12,2)) AS valor_total_liquido,
# MAGIC     CAST(ROUND(AVG(f.valor_liquido * -1), 2) AS DECIMAL(12,2)) AS ticket_medio_despesa,
# MAGIC     MIN(f.data_documento) AS primeira_despesa,
# MAGIC     MAX(f.data_documento) AS ultima_despesa
# MAGIC FROM dados_es.silver.despesas_clean f
# MAGIC JOIN dados_es.silver.deputados_clean d 
# MAGIC     ON f.deputado_id = d.deputado_id
# MAGIC GROUP BY 
# MAGIC     d.deputado_id,
# MAGIC     d.nome_deputado,
# MAGIC     d.sigla_partido,
# MAGIC     d.sigla_uf
# MAGIC ORDER BY 
# MAGIC     valor_total_liquido DESC;
# MAGIC
# MAGIC SELECT * FROM dados_es.gold.resumo_despesas_deputado;