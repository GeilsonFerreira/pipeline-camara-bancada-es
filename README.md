# 🏛️ Pipeline Câmara dos Deputados: Bancada do Espírito Santo

[![Databricks](https://img.shields.io/badge/Databricks-FF3621?style=for-the-badge&logo=databricks&logoColor=white)](https://databricks.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Delta Lake](https://img.shields.io/badge/Delta_Lake-00A98F?style=for-the-badge&logo=delta-lake&logoColor=white)](https://delta.io/)
[![SQL](https://img.shields.io/badge/SQL-4479A1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

Pipeline de engenharia de dados end-to-end desenvolvido no **Databricks**, responsável por coletar, tratar, auditar e consolidar os dados cadastrais e os gastos de cota parlamentar dos deputados federais do Espírito Santo, utilizando a API de Dados Abertos da Câmara dos Deputados.

> **Pergunta central que o projeto responde:** quanto cada deputado federal capixaba gasta, com o quê e qual o perfil de execução orçamentária da bancada?

---

## 📊 Demonstração do Pipeline
![Pipeline rodando](docs/pipeline_demo.gif)

---

## 🏗️ Arquitetura do Lakehouse (Medallion Architecture)
Os dados são estruturados e governados no **Unity Catalog** sob o schema `dados_es`:

| Camada | Schema | Descrição |
|--------|--------|-----------|
| **Bronze** | `dados_es.bronze` | Ingestão bruta (*raw*), espelhando exatamente os payloads JSON obtidos via API. |
| **Silver** | `dados_es.silver` | Dados limpos, tipados e normalizados (`deputados_clean` e `despesas_clean`), com deduplicação e saneamento de valores. |
| **Gold** | `dados_es.gold` | Tabela analítica relacional consolidada (`resumo_despesas_deputado`), pronta para consumo em BI. |

---

### 📊 Amostra dos Resultados (Top 5 Gastos Líquidos — 2023 a 2026)

| Deputado | Partido | Notas Fiscais | Valor Bruto | Valor Líquido | Ticket Médio |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Paulo Folletto** | PSB | 1.119 | R$ 1.908.570,49 | R$ 1.453.060,45 | R$ 1.298,53 |
| **Messias Donato** | UNIÃO | 1.314 | R$ 1.899.146,69 | R$ 1.445.612,63 | R$ 1.100,16 |
| **Gilson Daniel** | PODE | 1.501 | R$ 1.860.421,43 | R$ 1.405.145,75 | R$ 936,14 |
| **Dr. Victor Linhalis** | PSB | 1.098 | R$ 1.923.559,78 | R$ 1.401.973,15 | R$ 1.276,84 |
| **Amaro Neto** | PP | 1.119 | R$ 1.837.132,41 | R$ 1.397.012,82 | R$ 1.248,45 |

---

### 🔍 Auditoria de Dados: Bruto vs. Líquido (O Efeito dos Estornos)
Durante a validação analítica da camada Gold, identificou-se que a fórmula contábil tradicional (`Valor Bruto - Valor Glosado = Valor Líquido`) não se sustenta de forma direta. 

* **A Prova Numérica:** Somando toda a bancada, o *Valor Bruto* menos as *Glosas* resulta em **R$ 18,32 milhões**, enquanto o *Valor Líquido* efetivo é de **R$ 12,35 milhões**. A diferença de **R$ 5,97 milhões (32,59% do volume)** não é erro nem glosa oculta.
* **Causa Raiz:** Essa lacuna de quase R$ 6 milhões é explicada por **lançamentos compensatórios e estornos de bilhetes aéreos**. Na API da Câmara, bilhetes cancelados geram créditos/estornos que abatem o saldo líquido consumido da cota.
* **Tratamento de Engenharia:** Na camada Gold, aplicamos uma normalização contábil (`valor_liquido * -1`) para que os gastos reais sejam exibidos como valores positivos (facilitando somas em dashboards e gráficos), mantendo os estornos como valores negativos (redutores).

---

## ⚙️ Orquestração (Databricks Jobs)
O pipeline é totalmente automatizado por meio de um Job orquestrado no Databricks (`pipeline_camara_bancada_es`), composto por 5 tasks sequenciais:

| Task no Job | Notebook Correspondente | Responsabilidade |
|-------------|-------------------------|------------------|
| `nomes_deputados_es` | `01_deputados_extract_api_camara.py` | Extração da lista oficial de deputados da bancada. |
| `despesas_deputados_es` | `02_despesas_extract_lote.py` | Ingestão paginada em lote de todas as despesas (2023–2026). |
| `normaliza_deputados_es` | `03_silver_transform_deputados.py` | Limpeza cadastral e tipagem em PySpark. |
| `normaliza_despesas_deputados_es` | `04_silver_transform_despesas.py` | Tratamento financeiro, conversão de datas e deduplicação. |
| `despesas_deputados_es_final` | `05_gold_analytics_despesas.py` | Agregações analíticas e consolidação financeira em Spark SQL. |

![Job no Databricks](docs/job_databricks.jpg)

---

## 💡 Decisões de Engenharia e Regras de Negócio

1. **Paginação Resiliente de APIs:** Implementação de controle manual de páginas com tratamento de erros HTTP e mitigação de bugs de parâmetros combinados da API da Câmara.
2. **Saneamento do `valor_liquido`:** Na API de cota parlamentar, lançamentos de despesas vêm com sinal negativo na coluna líquida, enquanto estornos vêm positivos. Na camada Gold, aplicamos uma transformação contábil para exibir os gastos reais como valores positivos (facilitando somas e visualizações em gráficos) e mantendo os estornos como redutores.
3. **Deduplicação Inteligente:** A deduplicação na Silver utiliza uma chave composta (`deputado_id`, `documento_id`, `valor_liquido`) para evitar a exclusão acidental de estornos que compartilham o mesmo código de documento fiscal.

---

## 📂 Estrutura do Repositório

```text
├── docs/        # Prints de execução, GIFs e recursos visuais
├── jobs/        # Definição exportada do Job do Databricks (JSON)
└── notebooks/   # Notebooks do pipeline numerados por ordem de execução
```
---

## ▶️ Como Reproduzir

1. No Databricks, crie o catálogo/schema base (`CREATE SCHEMA IF NOT EXISTS dados_es.bronze`, `silver` e `gold`).
2. Importe os arquivos da pasta `notebooks/` para o seu Workspace mantendo a numeração sequencial (`01` a `05`).
3. Na aba **Workflows / Jobs**, crie um novo Job utilizando a definição exportada em `jobs/pipeline_camara_bancada_es.json` (ou encadeie as 5 tasks manualmente).
4. Execute o Job para popular todas as camadas end-to-end.

---

## 🚀 Próximos Passos

- [ ] Construir dashboard interativo no Databricks com gastos por deputado e categoria de despesa
- [ ] Adicionar testes automatizados de qualidade de dados (*Data Quality*) na camada Silver
- [ ] Ingerir proposições de leis apresentadas por cada parlamentar
- [ ] Mapear votações nominais da bancada capixaba

---

## 👤 Autor

**Geilson Ferreira** — Jornalista, historiador e engenheiro de dados em transição de carreira, unindo investigação e transparência pública à arquitetura moderna de dados.  
🔗 [Conecte-se comigo no LinkedIn](https://www.linkedin.com/in/geilson-ferreira)
