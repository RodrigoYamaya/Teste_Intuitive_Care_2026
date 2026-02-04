---aki vamos retornar os 5 estados maiores despesas totais.
---Aki e a query mais facil de todas passadas.
---vamos passar um count e AS nomear quantidade_trimestre para facilitar vizualização dos dados retornados.
--- where dentro duma subquery avg para calcular a media dos trimestre .
---apos vamos usar uma possibilidade group by agrupar com ajuntar que tem o mesmo  CNPJ.
---apos usar group concerteza iremos usar having filtrar os dados finais dos trimestres .

SELECT
    operadora_cnpj,
    COUNT(*) as qtd_trimestres_acima
FROM despesas_detalhadas d_fora
WHERE valor > (
    -- Iremos criar uma Subquery para  Calcular a média daquele trimestre específico.
    SELECT AVG(valor)
    FROM despesas_detalhadas d_dentro
    WHERE d_dentro.ano = d_fora.ano
      AND d_dentro.trimestre = d_fora.trimestre
)
GROUP BY operadora_cnpj
HAVING qtd_trimestres_acima >= 2;