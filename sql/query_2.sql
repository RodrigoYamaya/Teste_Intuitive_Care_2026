-- aki tem intuito de Listar os 5 estados com maiores despesas totais.
-- DESAFIO ADICIONAL: Calcular a média de gastos POR OPERADORA (não a média simples) que eleva bastante a dificuldade.
--- primeiro passo iremos soma total das despesas naqueles estados.
---iremos passar count com  distinct para remover as operadores duplicadas.
---- talves round para arrendodar numeros,visto que iremos trabalhar com media
--- apos isso iremos usar join e group by e order by para retornar os estados maiores despesas maior para menor.
SELECT
    o.uf,

    -- 1. Soma total das despesas naquele estado
    SUM(d.valor) AS total_despesas,

    -- 2. Quantidade de operadoras que atuam no estado
    COUNT(DISTINCT d.operadora_cnpj) AS qtd_operadoras,

    -- 3. Média por Operadora (Pulo do Gato):
    -- Dividimos o Total do Estado pelo número de Empresas únicas.
    ROUND(SUM(d.valor) / COUNT(DISTINCT d.operadora_cnpj), 2) AS media_por_operadora

FROM despesas_detalhadas d
JOIN operadoras o ON d.operadora_cnpj = o.cnpj
WHERE o.uf IS NOT NULL -- aki vamos Removemos 'Indefinido' para focar apenas em estados reais
GROUP BY o.uf
ORDER BY total_despesas DESC
LIMIT 5;