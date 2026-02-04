from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from pathlib import Path

# --- Configurações Iniciais ---
app = FastAPI(
    title="API de Despesas ANS",
    description="API para consulta de dados de operadoras e despesas",
    version="1.0.0"
)

# Habilitando o  CORS (Isso vai permitir  que o Frontend Vue.js converse com esse  nosso Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, trocar pelo domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Caminho do nosso Banco de Dados
DB_PATH = Path(__file__).resolve().parent.parent / "projeto.db"


def get_db_connection():
    """ aki vai Abrir a  conexão com o banco de dados  SQLite e vai  retorna linhas como dicionários."""
    if not DB_PATH.exists():
        raise HTTPException(status_code=500, detail="Banco de dados não encontrado. Rode o etl/init_db.py primeiro.")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# --- API 1: (get) Listar Todas as  Operadoras ("Com Paginação e Busca") ---
@app.get("/api/operadoras")
def listar_operadoras(
        page: int = Query(1, ge=1, description="Número da página"),
        limit: int = Query(10, ge=1, le=100, description="Itens por página"),
        busca: str = Query(None, description="Filtrar por Razão Social ou CNPJ")
):
    conn = get_db_connection()
    cursor = conn.cursor()

    offset = (page - 1) * limit

    # Query Base
    sql_base = "SELECT cnpj, razao_social, uf, modalidade FROM operadoras"
    sql_count = "SELECT COUNT(*) as total FROM operadoras"
    params = []

    # aki vamos Aplica Filtro de Busca (Se  caso houver)
    if busca:
        filtro = " WHERE razao_social LIKE ? OR cnpj = ?"
        sql_base += filtro
        sql_count += filtro
        params.extend([f"%{busca}%", busca])

    #aki a Ordenação e Paginação
    sql_base += " ORDER BY razao_social LIMIT ? OFFSET ?"
    params_paginacao = params + [limit, offset]

    # Executa a contagem total (para o frontend saber quantas páginas existem)
    cursor.execute(sql_count, params)
    total_registros = cursor.fetchone()['total']

    # aki vai  Executar a busca dos dados
    cursor.execute(sql_base, params_paginacao)
    resultados = [dict(row) for row in cursor.fetchall()]

    conn.close()

    # aki vai Retornar estruturado (Opção B do Trade-off 4.2.4)na paginação deve retornar apenas os dados ou dados + metadados(data,total,page)
    return {
        "data": resultados,
        "meta": {
            "page": page,
            "limit": limit,
            "total_items": total_registros,
            "total_pages": (total_registros + limit - 1) // limit
        }
    }


# --- API 2: GET retornar os Detalhes da Operadora  especifica---
@app.get("/api/operadoras/{cnpj}")
def detalhes_operadora(cnpj: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM operadoras WHERE cnpj = ?", (cnpj,))
    operadora = cursor.fetchone()

    conn.close()

    if not operadora:
        raise HTTPException(status_code=404, detail="Operadora não encontrada")

    return dict(operadora)


# --- API 3: GET Retornar o  Histórico de Despesas das operadora ---
@app.get("/api/operadoras/{cnpj}/despesas")
def historico_despesas(cnpj: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # aki vamos fazer validação simples,Para Primeiro verifica se a operadora existe
    cursor.execute("SELECT razao_social FROM operadoras WHERE cnpj = ?", (cnpj,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Operadora não encontrada")

    # aki vamos  Buscar as despesas detalhadas das operadoras
    sql = """
        SELECT ano, trimestre, valor 
        FROM despesas_detalhadas 
        WHERE operadora_cnpj = ?
        ORDER BY ano DESC, trimestre DESC
    """
    cursor.execute(sql, (cnpj,))
    despesas = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return despesas


# --- Api 4: GET para retornar as Estatísticas agregadas (Dashboard) das total das despesas,media e top 5 operadoras ---
@app.get("/api/estatisticas")
def obter_estatisticas():
    conn = get_db_connection()
    cursor = conn.cursor()

    stats = {}

    # 1) aki vamos pegar Total Geral de Despesas (Somar tudo)
    cursor.execute("SELECT SUM(valor) as total FROM despesas_detalhadas")
    row_total = cursor.fetchone()
    stats['total_geral'] = row_total['total'] if row_total['total'] else 0

    # 2. vamos calcular a Média por Trimestre
    cursor.execute("SELECT AVG(valor) as media FROM despesas_detalhadas")
    row_media = cursor.fetchone()
    stats['media_por_lancamento'] = row_media['media'] if row_media['media'] else 0

    # 3. aki vamos query retornar os Top 5 Operadoras
    sql_top5 = """
        SELECT razao_social, uf, valor_total_despesas as total
        FROM despesas_agregadas
        ORDER BY valor_total_despesas DESC
        LIMIT 5
    """
    cursor.execute(sql_top5)
    stats['top_5_operadoras'] = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return stats