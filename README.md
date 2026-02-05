# Teste_Intuitive_Care_2026

## Descrição do Projeto
Este repositório contém a solução completa para todas as etapas do processo seletivo para Estágio em Back-End. O projeto foi estruturado em módulos independentes para garantir organização e escalabilidade:

* **Módulos Principais:**
    * `ETL`: Scripts de extração e tratamento de dados.
    * `SQL`: Queries e modelagem do banco de dados.
    * `API`: Backend em Python (FastAPI).
    * `FRONTEND`: Interface visual em Vue.js.

* **Arquivos e Pastas Auxiliares:**
    * `projeto.db`: Banco de dados SQLite finalizado.
    * `outputs/`: Diretório com os arquivos finais gerados (CSV/ZIP).
    * `arquivos_ans/`: Arquivos originais baixados automaticamente do site do governo.
    * `docs/`: Documentação da API (Postman Collection).
    * `requirements.txt`: Lista de bibliotecas necessárias para execução.

---

## Considerações e Qualidade de Dados

Durante o processamento dos dados oficiais da ANS, foram identificadas inconsistências no cruzamento de informações entre os arquivos de origem:

1. **Divergência de Cadastro (PDF vs CSV):**
   Alguns CNPJs presentes no relatório financeiro (PDF) não foram encontrados na base cadastral de operadoras ativas (CSV). É provável que o arquivo PDF contenha registros históricos de empresas que não constam mais na lista ativa.

2. **Tratamento Adotado:**
   Para manter a integridade dos dados financeiros e não descartar informações de despesas válidas, optei pela seguinte abordagem:
   * **Razão Social:** Registrada como *"Nome não consta no CSV"*.
   * **UF:** Registrada como *NULL* (vazio).
   * **Modalidade:** Registrada como *NÃO INFORMADO* (vazio).

   
   O restante dos dados segue rigorosamente as informações originais, sem alterações.