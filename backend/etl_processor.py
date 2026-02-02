import os
import zipfile
import pandas as pd
import io


class ETLProcessor:
    """
    nesse classe temos que comprir alguns dos requisitos? etapas(1.2, e 1.3)

    1)concluimos o download dos arquivos dos 3 trimestres(done)
    2)vamos extrair os arquivos zip que instalamos na classe "ans_download" no  automaticamnete()
    4)apos extarir esses arquivos vamos identificar e processar os arquivos com os dados de "DESPESAS COM EVENTOS/SINISTRO.()
    5) apos concluir com os dados etapas anteriores iremos criar um unico arquivo csv.()
    6) continuação da anterior  apos criação desse csv, deve conter as sequintes colunas(CNPJ,RAZAOSOCIAL,TRIMESTRE,ANO,VALORDESPESAS) ()
    7)ultima etapa e passar um pente fino eliminando problemas nos CNPJS duplicados , valores zerados ou negativos e trimestre com formatos diferentes. ()
    8)Apos conclusao justificar cada tipo de inconsistencia da etapa anterior.
    9)ULTIMA etapa final e consolidar em um arquivo csv final zip com codenome: consolidado_despesas.zip.()
    """

    # vamos Definir  os caminhos  para garantir que funcione em quaisquer computador
    DIRETORIO_ATUAL = os.path.dirname(__file__)
    PASTA_ENTRADA = os.path.join(DIRETORIO_ATUAL, "../arquivos_ans")
    ARQUIVO_SAIDA = os.path.join(DIRETORIO_ATUAL, "../consolidado_despesas.zip")

    def processar(self):
        print("Iniciando o processamento ETL desses dados...")

        # Lista para armazenar os DataFrames de cada trimestre antes de juntar tudo naquele arquivo
        lista_dfs = []

        # Verificaçao simples se a  pasta de entrada existe antes de tentar ler ela.
        if not os.path.exists(self.PASTA_ENTRADA):
            print(f"Erro: Pasta '{self.PASTA_ENTRADA}' não encontrada.")
            return

        # filtra a Lista apenas os arquivos que terminam com .zip
        arquivos_zip = [f for f in os.listdir(self.PASTA_ENTRADA) if f.endswith('.zip')]

        #Verificação simples caso ocorra de não encontrar arquivo zip
        if not arquivos_zip:
            print("Nenhum arquivo ZIP encontrado! Rode o 'ans_download.py'")
            return

        # for para  Itera sobre cada arquivo ZIP encontrado na pasta na pasta "PASTA_ENTRADA"
        for nome_zip in arquivos_zip:
            caminho_completo = os.path.join(self.PASTA_ENTRADA, nome_zip)
            print(f"Processando ZIP: {nome_zip}...")

            try:
                # vai Abrir  o ZIP em modo de leitura ('r') sem descompactar no disco ainda
                with zipfile.ZipFile(caminho_completo, 'r') as z:
                    # Itera sobre cada arquivo dentro do ZIP
                    for nome_arquivo in z.namelist():

                        # REGRA 1.2: Identificar apenas arquivos de DESPESA / EVENTO / SINISTRO
                        nome_upper = nome_arquivo.upper()
                        # então vamos aceitar qualquer CSV e validar as colunas depois (dentro do transformar).
                        eh_csv = nome_upper.endswith('.CSV')

                        # validaçaõ simples caso Ser  for CSV e tiver a palavra chave, processa o arquivo
                        if eh_csv:
                            print(f"Lendo o CSV: {nome_arquivo}")

                            # Lê o CSV direto da memória (Stream) usando na biblioteca "Pandas"
                            # sep=';' e latin1 são padrões da ANS
                            with z.open(nome_arquivo) as f:
                                # Correção: Adicionado 'utf-8' como fallback caso latin1 falhe
                                try:
                                    df_temp = pd.read_csv(f, sep=';', encoding='latin1', on_bad_lines='skip')
                                except:
                                    f.seek(0)
                                    df_temp = pd.read_csv(f, sep=';', encoding='utf-8', on_bad_lines='skip')

                                # Chama a função auxiliar para limpar e padronizar os dados que foi definido
                                df_limpo = self._transformar_dados(df_temp, nome_zip)

                                # Se o dataframe voltou limpo (não é None), adiciona na lista
                                if df_limpo is not None:
                                    print(f"   --> Arquivo validado! {len(df_limpo)} linhas adicionadas.")
                                    lista_dfs.append(df_limpo)

            except Exception as e:
                print(f" Erro ao processar {nome_zip}: {e}")

        # aki e a etapa da CONSOLIDAÇÃO de tudo de uma vez no csv.
        if lista_dfs:
            print("consolidando todos os trimestres...")
            # vai Juntar todos os pedaços (trimestres) em um único tabela
            df_final = pd.concat(lista_dfs, ignore_index=True)

            # Etapa 7: removeremos todas as  duplicatas exatas se houver CNPJ etcs
            df_final.drop_duplicates(inplace=True)

            # aki iremos chamar  a função para salvar o arquivo final csv.
            self._carregar_dados(df_final)
        else:
            print("Nenhum dado válido foi extraído.")

    def _transformar_dados(self, df, nome_zip_origem):
        """aki iremos Padroniza colunas e limpar  valores" das etapas 7"""

        # 1. Removeremos os  espaços e deixa tudo minúsculo no cabeçalho das colunas
        df.columns = [c.strip().lower() for c in df.columns]

        # 2. Mapa de tradução (De nome ANS para nome do Sistema) definido pelo teste
        # ATUALIZAÇÃO: Adicionamos 'reg_ans' e 'vl_saldo_final' que descobrimos no Raio-X
        mapa_colunas = {
            'cd_ops': 'operadora_cnpj', 'reg_ans': 'operadora_cnpj',
            'nm_ops': 'razao_social', 'razao_social': 'razao_social',
            'vl_saldo_final': 'valor', 'valor': 'valor', 'valor_despesa': 'valor',
            'ano': 'ano', 'trimestre': 'trimestre'
        }
        # Aplica a renomeação
        df.rename(columns=mapa_colunas, inplace=True)

        # Validação simples: Se não tiver Valor ou Razão Social, o dado é inútil.
        if 'valor' not in df.columns or 'operadora_cnpj' not in df.columns:
            return None

        if 'razao_social' not in df.columns:
            df['razao_social'] = df['operadora_cnpj'].astype(str) + " (Nome não consta no CSV)"

        # 3. Enriquece com Ano/Trimestre (Fallback - caso não venha no CSV)
        # Tenta descobrir o ano/tri pelo nome do arquivo ZIP
        ano_estimado = "2025" if "2025" in nome_zip_origem else "2024"
        if "2024" in nome_zip_origem: ano_estimado = "2024" # Garante 2024

        tri_estimado = "3"
        if "1T" in nome_zip_origem: tri_estimado = "1"
        elif "2T" in nome_zip_origem: tri_estimado = "2"
        elif "4T" in nome_zip_origem: tri_estimado = "4"

        # somente vai  preencher se caso a coluna não existir.
        if 'ano' not in df.columns: df['ano'] = ano_estimado
        if 'trimestre' not in df.columns: df['trimestre'] = tri_estimado

        # Limpeza Fina e Conversão de Valores.
        # Converte "1.000,00" (String) para 1000.00 (Float)
        df['valor'] = df['valor'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce')

        # Etapa 7: Eliminaçao dos  valores zerados ou negativos
        df = df[df['valor'] > 0]

        # Selecionando  apenas as colunas pedidas no requisito 6
        colunas_finais = ['operadora_cnpj', 'razao_social', 'ano', 'trimestre', 'valor']
        cols_existentes = [c for c in colunas_finais if c in df.columns]

        return df[cols_existentes]

    def _carregar_dados(self, df):
        """Etapa 9: Salva o arquivo final compactado"""
        print(f"Salvando arquivo final: {self.ARQUIVO_SAIDA}")
        try:
            with zipfile.ZipFile(self.ARQUIVO_SAIDA, 'w', zipfile.ZIP_DEFLATED) as z:
                # Escreve o CSV dentro do ZIP
                z.writestr('consolidado_despesas.csv', df.to_csv(index=False, sep=';'))
            print(f"SUCESSO! {len(df)} registros processados e salvos.")
        except Exception as e:
            print(f" Erro ao salvar arquivo: {e}")


if __name__ == "__main__":
    processador = ETLProcessor()
    processador.processar()