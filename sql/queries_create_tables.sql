-- 1. Tabela de Operadoras
CREATE TABLE IF NOT EXISTS operadoras (
    registro_ans VARCHAR(20),
    cnpj VARCHAR(14) PRIMARY KEY, -- CNPJ chave única
    razao_social VARCHAR(255),
    modalidade VARCHAR(100),
    uf VARCHAR(2)
);

-- Index para velocidade buscas por UF (pedido na regra da query 2)
CREATE INDEX IF NOT EXISTS idx_operadoras_uf ON operadoras(uf);

-- 2. Tabela de Despesas
CREATE TABLE IF NOT EXISTS despesas_detalhadas (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    operadora_cnpj VARCHAR(14),
    ano INT NOT NULL,
    trimestre INT NOT NULL,
    valor DECIMAL(15, 2),
    data_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Aki ficar "Fk" Chave Estrangeira (Relacionamento com tabela operadoras)
    FOREIGN KEY (operadora_cnpj) REFERENCES operadoras(cnpj)
);

-- Index para velocidade na busca de despesas por operadora e tempo
CREATE INDEX IF NOT EXISTS idx_despesas_cnpj ON despesas_detalhadas(operadora_cnpj);
CREATE INDEX IF NOT EXISTS idx_despesas_tempo ON despesas_detalhadas(ano, trimestre);

-- 3. Tabela de Despesas Agregadas
CREATE TABLE IF NOT EXISTS despesas_agregadas (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    operadora_cnpj VARCHAR(14),
    razao_social VARCHAR(255),
    uf VARCHAR(2),
    valor_total_despesas DECIMAL(20, 2),
    media_despesas_trimestre DECIMAL(20, 2),
    desvio_padrao_despesas DECIMAL(20, 2),
    qtd_lancamentos INT
);

-- PARTE 2: IMPORTAÇÃO DOS DADOS
LOAD DATA INFILE '/var/lib/mysql-files/despesas_agregadas.csv'
INTO TABLE operadoras
FIELDS TERMINATED BY ';' ENCLOSED BY '"' LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@v_cnpj, @v_razao, @v_uf, @dummy, @dummy, @dummy, @dummy)
SET
    cnpj = @v_cnpj,
    razao_social = NULLIF(@v_razao, ''),
    uf = NULLIF(@v_uf, 'Indefinido'),
    registro_ans = NULL,
    modalidade = 'Não Informado';

-- Importando Despesas
LOAD DATA INFILE '/var/lib/mysql-files/consolidado_despesas.csv'
INTO TABLE despesas_detalhadas
FIELDS TERMINATED BY ';' ENCLOSED BY '"' LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@v_cnpj, @v_razao_social, @v_trimestre, @v_ano, @v_valor)
SET
    operadora_cnpj = @v_cnpj,
    ano = CAST(@v_ano AS UNSIGNED),
    trimestre = CAST(@v_trimestre AS UNSIGNED),
    valor = CAST(REPLACE(@v_valor, ',', '.') AS DECIMAL(15,2)),
    data_carga = NOW();

-- Importando Despesas Agregadas
LOAD DATA INFILE '/var/lib/mysql-files/despesas_agregadas.csv'
INTO TABLE despesas_agregadas
FIELDS TERMINATED BY ';' ENCLOSED BY '"' LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(operadora_cnpj, razao_social, uf, valor_total_despesas, media_despesas_trimestre, desvio_padrao_despesas, qtd_lancamentos);