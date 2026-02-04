## 4.API


### 4.2. Trade-offs Técnicos - Backend

**4.2.1. Escolha do Framework (Opção Escolhida: B - FastAPI)**
* **Decisão:** Utilização do FastAPI em vez do Flask.
* **Justificativa:**
    * **Performance:** O FastAPI é assíncrono (ASGI) e baseado em Starlette/Pydantic, oferecendo performance superior ao Flask (WSGI) para operações de I/O e banco de dados.
    * **Produtividade e Documentação:** O requisito do teste pedia documentação das rotas. O FastAPI gera automaticamente a interface Swagger UI (`/docs`), eliminando a necessidade de escrever documentação manual ou configurar plugins externos.
    * **Validação:** A tipagem forte reduz erros de runtime e valida automaticamente os inputs da API.

**4.2.2. Estratégia de Paginação (Opção Escolhida: A - Offset-based)**
* **Decisão:** Paginação via parâmetros `page` e `limit` (OFFSET e LIMIT no SQL).
* **Justificativa:**
    * **UX:** Permite pular para páginas específicas (ex: ir direto para a página 5), o que é um requisito comum em tabelas administrativas.
    * **Complexidade vs Volume:** Para o volume atual de dados (milhares/milhões de linhas), o Offset é performático o suficiente e muito mais simples de implementar e manter do que a paginação baseada em cursor (Cursor-based).

**4.2.3. Cache vs Queries Diretas (Opção Escolhida: C - Pré-calcular)**
* **Decisão:** Uso de tabela agregada (`despesas_agregadas`) gerada no ETL.
* **Justificativa:**
    * **Performance:** Calcular estatísticas (Top 5, Média Global) varrendo milhões de linhas a cada requisição (Opção A) seria ineficiente.
    * **Consistência:** Como os dados são carregados via batch (ETL), não há necessidade de cálculo real-time. Consultar uma tabela já consolidada garante resposta imediata (milissegundos) para o dashboard.

**4.2.4. Estrutura de Resposta (Opção Escolhida: B - Dados + Metadados)**
* **Decisão:** Retorno de objeto envelope `{ data: [...], meta: {...} }`.
* **Justificativa:**
    * **Frontend:** O Frontend precisa saber o `total_items` e `total_pages` para renderizar corretamente os botões de paginação ("Anterior", "Próximo", "Última"). Retornar apenas a lista (Opção A) impediria essa navegação completa.