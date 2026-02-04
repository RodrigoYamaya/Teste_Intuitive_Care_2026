---Aki iremos passar uma query para verificar os 5 operadores com o maior percentual despesas, entre os primeiros meses e o ultimo meses
---nivel dificuldade bastante elevado nessas query.
---a tatica vamos acessar as colunas despesas_detalhadas e iremos utilizar um join "despesas detalhada" e "operadora".
---apos isso vamos where filtra o inicio do ano e o fim.
--- apos isso iremos order by coluna crescimento_percentual Desc para retornar maior para menor
--- usar limit 5 limitar os 5 operadores maior percentual somente.Não havendo necessidade retornar mais.

SELECT
    inicio.operadora_cnpj,
    ops.razao_social,
    inicio.valor AS valor_inicial,
    fim.valor AS valor_final,
    ROUND(((fim.valor - inicio.valor) / inicio.valor) * 100, 2) AS crescimento_percentual
FROM despesas_detalhadas AS inicio
JOIN despesas_detalhadas AS fim
    ON inicio.operadora_cnpj = fim.operadora_cnpj
JOIN operadoras AS ops
    ON inicio.operadora_cnpj = ops.cnpj
WHERE
    (inicio.ano = 2023 AND inicio.trimestre = 1)
    AND (fim.ano = 2023 AND fim.trimestre = 4)
ORDER BY crescimento_percentual DESC
LIMIT 5;