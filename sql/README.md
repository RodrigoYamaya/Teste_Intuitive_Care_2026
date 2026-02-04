#Modelagem, ETL e Análise de Dados de Operadoras

## 3.2 Modelagem e Estrutura do Banco (DDL)

### Trade-off Técnico — Normalização

**Opção escolhida:** Tabelas Normalizadas

**Justificativa:**  
Optamos pela normalização para organizar melhor os dados em tabelas separadas, evitando repetição de informações e reduzindo problemas de manutenção a longo prazo.

**Volume de Dados:**  
O nome da operadora (Razão Social) é uma string extensa. Repeti-lo em milhares de registros aumentaria o armazenamento e o custo de I/O.

**Manutenibilidade:**  
Alterações cadastrais podem ser realizadas em apenas um registro, garantindo integridade e reduzindo inconsistências.

**Performance:**  
JOINs utilizando chaves numéricas ou CNPJ são eficientes e mantêm a escalabilidade da aplicação.

---

### Trade-off Técnico — Tipos de Dados

#### Valores Monetários
**Escolha:** `DECIMAL(15,2)`

**Motivo:**  
O tipo DECIMAL garante precisão exata nos cálculos financeiros, evitando erros de arredondamento comuns em tipos de ponto flutuante.

---

#### Datas
**Escolha:** Inteiros para `ano` e `trimestre` e `TIMESTAMP` para auditoria.

**Motivo:**  
A separação em inteiros facilita filtros e indexação. O TIMESTAMP permite rastrear quando o dado foi carregado no sistema.

---

### Estrutura das Tabelas

#### Tabela Operadoras
- CNPJ (PK)
- Razão Social
- UF
- Endereço
- Outros dados cadastrais

---

#### Tabela Despesas Detalhadas
- ID
- CNPJ (FK)
- Ano
- Trimestre
- Valor
- Data de Carga

---

#### Tabela Despesas Agregadas
- CNPJ
- Ano
- Trimestre
- Valor Consolidado

---

## 3.3 Processo ETL (Importação e Tratamento de Dados)

A ingestão dos dados foi automatizada utilizando Python (`etl/init_db.py`) com apoio da biblioteca Pandas e banco SQLite.

Essa abordagem permitiu realizar validações e tratamentos antes da inserção no banco.

---

### Tratamento de Inconsistências

#### Formatação Decimal
Os dados de origem utilizavam vírgula como separador decimal.  
Foi realizada conversão para ponto, seguindo o padrão ANSI SQL.

---

#### Dados Nulos — Nome da Operadora
Registros sem Razão Social foram preenchidos com:


**Motivo:**  
Manter registros financeiros válidos sem comprometer a leitura dos relatórios.

---

#### CNPJ Ausente
Foi realizado cruzamento entre arquivos para recuperar chaves faltantes.

**Motivo:**  
O CNPJ é essencial para relacionamentos entre tabelas e sua recuperação evita perda de dados relevantes.

---

#### Encoding
Foi utilizada leitura forçada em UTF-8.

**Motivo:**  
Garantir preservação de caracteres especiais como acentos e cedilha.

---

#### Strings em Campos Numéricos
Foi aplicada tentativa de conversão automática.  
Registros inválidos foram descartados ou ajustados conforme contexto.

---

#### Datas Inconsistentes
As datas foram padronizadas antes da inserção no banco.

**Motivo:**  
Garantir compatibilidade com filtros e consultas analíticas.

---

## 3.4 Queries Analíticas

As consultas foram desenvolvidas com foco em responder perguntas estratégicas de negócio.

---

### Query 1 — Top 5 Operadoras com Maior Crescimento Percentual

**Objetivo:**  
Identificar operadoras com maior crescimento entre o primeiro e o último trimestre analisado.

**Desafio:**  
Algumas operadoras não possuem dados completos em todos os períodos.

**Solução:**  
Utilização de `INNER JOIN` entre os períodos inicial e final.

**Justificativa:**  
O crescimento percentual só pode ser calculado quando existem valores nos dois períodos.  
Operadoras sem dados completos são automaticamente filtradas, evitando distorções ou divisões por zero.

---

### Query 2 — Distribuição de Despesas por UF

**Objetivo:**  
Listar os 5 estados com maior volume total de despesas e calcular a média de gastos por operadora.

**Solução:**

**sql**
SUM(valor) / COUNT(DISTINCT CNPJ)


**Justificativa: O uso direto da função AVG calcularia a média por lançamento individual**.
A abordagem escolhida representa corretamente a média de despesas por operadora, atendendo ao requisito de negócio.

Query 3 — Operadoras com Despesas Acima da Média Geral

**Objetivo: Identificar operadoras que ficaram acima da média em pelo menos 2 trimestres**.

Trade-off Técnico

Opções Avaliadas

CTE (Common Table Expression)

Subquery Correlacionada

Escolha: Subquery Correlacionada

**Justificativa — Legibilidade: A estrutura WHERE valor > (SELECT AVG(...)) facilita entendimento e auditoria da consulta**.

**Justificativa — Lógica de Negócio: Permite comparar cada operadora com a média do seu próprio trimestre, respeitando variações sazonais**.