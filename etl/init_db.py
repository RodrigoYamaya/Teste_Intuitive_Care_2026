import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "projeto.db"
OUTPUTS_DIR = BASE_DIR / "outputs"


def init_database():
    print("Iniciando Recuperação e Carga do Banco...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("🛠️  Limpando banco de dados...")
    cursor.executescript("""
        DROP TABLE IF EXISTS despesas_agregadas;
        DROP TABLE IF EXISTS despesas_detalhadas;
        DROP TABLE IF EXISTS operadoras;

        CREATE TABLE operadoras (
            cnpj VARCHAR(14) PRIMARY KEY,
            razao_social VARCHAR(255),
            modalidade VARCHAR(100),
            uf VARCHAR(2),
            registro_ans VARCHAR(20)
        );

        CREATE TABLE despesas_detalhadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operadora_cnpj VARCHAR(14),
            ano INT,
            trimestre INT,
            valor DECIMAL(15, 2),
            data_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (operadora_cnpj) REFERENCES operadoras(cnpj)
        );

        CREATE TABLE despesas_agregadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operadora_cnpj VARCHAR(14),
            razao_social VARCHAR(255),
            uf VARCHAR(2),
            valor_total_despesas DECIMAL(20, 2),
            media_despesas_trimestre DECIMAL(20, 2),
            desvio_padrao_despesas DECIMAL(20, 2),
            qtd_lancamentos INT
        );
    """)

    try:
        print("lendo CSVs...")

        # aki Ler Detalhado (Tem CNPJ, mas não tem UF)
        df_detalhes = pd.read_csv(OUTPUTS_DIR / "consolidado_despesas.csv", sep=";", encoding="utf-8")
        if df_detalhes['valor'].dtype == 'object':
            df_detalhes['valor'] = df_detalhes['valor'].str.replace(',', '.').astype(float)

        # ler o Agregado (Tem UF, mas não tem CNPJ)
        df_agregado = pd.read_csv(OUTPUTS_DIR / "despesas_agregadas.csv", sep=";", encoding="utf-8")

        print("Reconstruindo Tabela de Operadoras")

        # Pega CNPJ e Razão Social unicos do detalhado
        df_base_ops = df_detalhes[['operadora_cnpj', 'razao_social']].drop_duplicates(subset=['operadora_cnpj']).copy()

        # Pega Razão Social e UF do agregado
        df_ufs = df_agregado[['razao_social', 'UF']].drop_duplicates(subset=['razao_social']).copy()

        # Junta os dois (Procv)
        df_ops_final = pd.merge(df_base_ops, df_ufs, on='razao_social', how='left')

        # Prepara para salvar
        df_ops_final.rename(columns={'operadora_cnpj': 'cnpj', 'UF': 'uf'}, inplace=True)
        df_ops_final['registro_ans'] = None
        df_ops_final['modalidade'] = 'Não Informado'

        # Salva Operadoras
        df_ops_final.to_sql('operadoras', conn, if_exists='append', index=False)
        print(f"Operadoras recuperadas e salvas: {len(df_ops_final)}")

        # --- PASSO 3: Salvar DESPESAS DETALHADAS ---
        print("Salvando Despesas Detalhadas...")
        df_save_detalhes = df_detalhes[['operadora_cnpj', 'ano', 'trimestre', 'valor']].copy()
        df_save_detalhes.to_sql('despesas_detalhadas', conn, if_exists='append', index=False)
        print(f"Despesas detalhadas salvas: {len(df_save_detalhes)}")

        # --- PASSO 4: Salvar DADOS AGREGADOS ---
        print("Salvando Dados Agregados...")
        df_mart = pd.merge(df_agregado, df_base_ops, on='razao_social', how='left')

        # Renomeia para o banco de dados
        rename_map = {
            'UF': 'uf',
            'valor_total_despesas': 'valor_total_despesas'
        }
        df_mart.rename(columns=rename_map, inplace=True)

        # Seleciona colunas válidas
        cols_banco = ['operadora_cnpj', 'razao_social', 'uf', 'valor_total_despesas',
                      'media_despesas_trimestre', 'desvio_padrao_despesas', 'qtd_lancamentos']

        df_mart_final = df_mart[[c for c in cols_banco if c in df_mart.columns]]
        df_mart_final.to_sql('despesas_agregadas', conn, if_exists='append', index=False)
        print(f"Dados agregados salvos: {len(df_mart_final)}")

        print("\nTUDO CERTO! Banco de dados recuperado com sucesso.")

    except Exception as e:
        print(f"\nERRO FATAL: {e}")
        import traceback
        traceback.print_exc()

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_database()