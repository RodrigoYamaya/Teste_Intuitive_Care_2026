## Decisões Arquiteturais e Trade-offs (Documentação Técnica)

###  Decisão de Arquitetura (Java)
A Escolha Inicial: Comecei o projeto escolhendo Java e Spring Boot, pois é minha especialidade e facilitaria muito a criação do Banco de Dados e da API nas etapas finais.

O Obstáculo: Porém, notei que fazer o ETL (leitura e limpeza de CSVs complexos) em Java estava criando uma complexidade desnecessária. O código estava ficando gigante e difícil de manter, o que travou meu progresso inicial.

A Solução: Decidi ser prático: mudei o ETL para Python. Mesmo não sendo minha linguagem principal, usei IA para auxiliar na sintaxe e aprendizado. O que parecia impossível em Java foi resolvido de forma simples em Python, permitindo que eu entregasse os dados limpos e prontos para o SQL.



* **Justificativas:** Optei por carregar os arquivos CSV com  biblioteca  Pandas que tem balanço perfeito com performace e praticidade que na minha situação tenho maestria python. 
* Os dados cabem tranquilamente na memoria RAM do computador .Nessa situação funcionaria tranquilo e outra situação optei também pela simplicidade e eficiência. Visto que o volume dos dados não são tão gigantesco que aponto de travar a maquina.

### 1.3 Consolidação e Inconsistências
* **Justificativas:** Formatos das datas Inconsistente:  Ignorei completamente as colunas referente as datas e usei os dados do proprio nome do arquivo para facilitação. 
* ** CNPJs Duplicados com Nomes Diferentes **: A minnha solução foi em focar nos dados importantes que e o CNPJ, visto que empresa mudam de razão social , agora o CNPJ E único e o nome ignorando. 
* valores zerados ou negativos": mantive tudo no arquivo com codinome consolidado_despesa.zip e minha logica foi que ignorar os dados negativos e focar somente no positivos para facilitar considerei apenas os valores dinheiro da saída positivo e negativo ignorei. 
* **Coluna "Razão Social" Faltando (2025):** tive alguns dificuldades , optei pela simplicidade em por CNPJ E Nome não consta no csv, optei pela maior importância os dados financeiros 

### 2.1 Validação de CNPJ
**Justificativa:** Esta foi a etapa de maior desafio técnico quanto à implementação da lógica de validação. Após análise, optei por **excluir** os registros com CNPJ matematicamente inválido.
* **Motivo:** O objetivo foi garantir a integridade dos dados: um CNPJ inválido não é rastreável e sujaria o cruzamento de dados. Priorizei que apenas dados auditáveis entrassem no relatório final.

### 2.2 Enriquecimento (Join)
**Justificativa:** A estratégia adotada foi utilizar o **Left Join**.
* **Motivo:** O foco foi priorizar as despesas passadas. Se eu usasse outra estratégia, perderia os valores gastos por empresas que não estão mais ativas. Com o Left Join, mantive os valores financeiros históricos e preenchi os dados cadastrais faltantes como "Indefinido".

### 2.3 Agregação e Ordenação
**Justificativa:** A estratégia de ordenação foi do **maior para o menor** valor.
* **Motivo:** Busquei somar os totais e calcular o **Desvio Padrão** para encontrar as operadoras com maior volume e variação de gastos. A ordenação decrescente serve para apresentar de imediato os maiores impactos financeiros (foco nos maiores valores).


