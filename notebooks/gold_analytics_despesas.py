# Databricks notebook source
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
