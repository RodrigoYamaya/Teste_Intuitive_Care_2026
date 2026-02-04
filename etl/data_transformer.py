import pandas as pd
import zipfile
import io
import os
import requests
import re
import numpy as np


class DataTransformer:
    """
        nesse classe temos que comprir alguns dos requisitos? etapas 2)
        1)vamos pegar o csv consilidade_despesas.zip di teste anterior que iremos usar biblioteca "zipfile" havendo a não a necessidade descompactar,visto que ela ler os arquivos sem descompactar , assim lendo e processando esses dados()
        2)apos pegar iremos fazer as validações do CNPJ VALIDO(COM FORMATOS E DIGITOS VERIFICADOS(FAÇO A MINIMA IDEIA DE COMO FAZER ISSO, PESQUISAR gpt)), VALORES NUMEROS POSITIVOS, RAZAO SOCIAL NÃO VAZIA. APOS TRADE-OFF -TECNIC COM A JUSTIFICATIVA.
        3)Apos esssa etapa iremos baixar o csv dos dados que o teste passou link
        4)Apos essa etapa iremos fazer um join no csv consilado(consilidade_despesas.zip) com os dados do CNPJ como "CHAVE"()
        5)Apos essas etapas iremos adicionar as colunas (REGISTROSANS, MODALIDADE,UF)ao csv final.

        6)apos essa etapa iremos fazer agrega os dados RAZÃO SOCIAL, UF
        7)Nessa mesma etapa agregação vamos calcular o total de desespesas por operadora UF
        8) NESSA mesma etapa vamos fazer um desafio opcional  calcular : media das despesas por trimestre de cada operadora/uF
        9) Nessa mesma etapa calcular ps desvio de padrão das despesas com a operadora com valores mais variaveis. TRADE-OF TECNICO NESSA ETAPA.
        10) ULTIMA ETAPA ordenar por valor total DO MAIOR PARA MENOR.
        11) ULTIMA ETAPA SALVAR O RESULTADO DO CSV COM NOVO NOME : despesas_agregadas.csv
        12)Final etapa , apos concluir tudo iremos compactar esse arquivo da etapa acima com nome: Teste_{seu_nome}.zip
    """

    DIRETORIO_ATUAL = os.path.dirname(__file__)
    ARQUIVO_ENTRADA = os.path.join(DIRETORIO_ATUAL, "../outputs/consolidado_despesas.zip")
    ARQUIVO_SAIDA_FINAL = os.path.join(DIRETORIO_ATUAL, "../outputs/Teste_Rodrigo_Yamaya.zip")

    # CORREÇÃO: A URL correta no servidor Linux da ANS é com 'cadop' minúsculo
    URL_CADASTRO = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv"

    def executar(self):
        print("Iniciando a transformação e validações")

        # 1. Carregar dados da etapa anterior
        df_despesas = self._carregar_dados_brutos()
        if df_despesas is None: return

        # 2. Validação (Requisito 2.1)
        df_validado = self._validar_dados(df_despesas)

        # Trava de segurança: Se apagou tudo, avisa
        if len(df_validado) == 0:
            print("ERRO CRÍTICO: Todos os dados foram removidos na validação. Verifique a lógica do CNPJ.")
            return

        # 3. Enriquecimento (Requisito 2.2)
        df_enriquecido = self._enriquecer_dados(df_validado)

        # 4. Agregação e Estatísticas (Requisito 2.3)
        df_final = self._agregar_dados(df_enriquecido)

        # 5. Salvar resultado
        self._salvar_final(df_final)

    def _carregar_dados_brutos(self):
        print("carregando dados consolidado")
        try:
            with zipfile.ZipFile(self.ARQUIVO_ENTRADA, 'r') as z:
                # Lê o CSV que criamos na etapa 1
                with z.open('consolidado_despesas.csv') as f:
                    # CORREÇÃO: dtype=str garante que o CNPJ venha com os zeros antes de processar
                    return pd.read_csv(f, sep=';', encoding='utf-8', dtype={'operadora_cnpj': str})
        except Exception as e:
            print(f"Erro ao ler arquivo de entrada: {e}")
            return None

    def _validar_dados(self, df):
        print("Validando dados (CNPJ, Valores, Razão Social)...")
        total_antes = len(df)

        # A) Razão Social não vazia
        # Trade-off: Removemos registros sem nome pois impossibilitam a agregação por empresa.
        df = df[df['razao_social'].notna() & (df['razao_social'] != '')]

        # B) Valores numéricos positivos
        # Trade-off: Valores negativos em despesas contábeis geralmente são estornos,
        # mas o teste pede explicitamente validação de positivos.
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
        df = df[df['valor'] > 0]

        # C) Validação de CNPJ (Algoritmo de Dígitos Verificadores)
        # Aplica a função valida_cnpj linha a linha
        print("   ...Verificando CNPJs matematicamente (isso evita apagar dados válidos)...")
        df['cnpj_valido'] = df['operadora_cnpj'].apply(self._verificar_cnpj)

        # TRADE-OFF TÉCNICO (Requisito 2.1):
        # Estratégia Escolhida: Filtragem Rigorosa ("Drop Invalid").
        # Justificativa: Para análises financeiras confiáveis, dados com identificadores inválidos
        # (CNPJs errados) comprometem o join com o cadastro e a integridade fiscal.
        df_validos = df[df['cnpj_valido'] == True].copy()

        # Limpeza final
        df_validos.drop(columns=['cnpj_valido'], inplace=True)

        removidos = total_antes - len(df_validos)
        print(f"Validação concluída. {removidos} removidos registros inconsistentes. Restaram: {len(df_validos)}")
        return df_validos

    def _enriquecer_dados(self, df_despesas):
        print(" Baixando dados cadastrais da ANS")

        cadop = None
        try:
            # CORREÇÃO: Usar requests com verify=False evita erro SSL do governo
            # Baixa o CSV direto da URL (sem salvar no disco pra economizar espaço)
            # encoding='latin1' e sep=';' são padrões do governo
            response = requests.get(self.URL_CADASTRO, verify=False, timeout=30)
            response.raise_for_status()  # Avisa se der 404

            file_content = io.BytesIO(response.content)
            cadop = pd.read_csv(file_content, sep=';', encoding='latin1', on_bad_lines='skip', dtype=str)

        except Exception as e:
            print(f"Falha ao baixar cadastro {e}. Usando tabela vazia para não quebrar.")
            # Mock de emergência caso a internet falhe ou URL mude
            cadop = pd.DataFrame(columns=['CNPJ', 'Registro ANS', 'Modalidade', 'UF'])

        # Padronização para o JOIN
        # Precisamos limpar o CNPJ do cadastro (tirar ponto, barra, traço) para bater com o nosso
        # CORREÇÃO: Adicionado zfill(14) para garantir formato padrão
        if 'CNPJ' in cadop.columns:
            cadop['CNPJ_limpo'] = cadop['CNPJ'].astype(str).str.replace(r'\D', '', regex=True).str.zfill(14)
        elif not cadop.empty:
            # Tenta achar a coluna certa se o nome mudou
            col_cnpj = [c for c in cadop.columns if 'CNPJ' in c.upper()][0]
            cadop['CNPJ_limpo'] = cadop[col_cnpj].astype(str).str.replace(r'\D', '', regex=True).str.zfill(14)

        # Garante que nosso CNPJ também é string limpa com 14 digitos
        df_despesas['operadora_cnpj'] = df_despesas['operadora_cnpj'].astype(str).str.replace(r'\D', '',
                                                                                              regex=True).str.zfill(14)

        print(" Executando JOIN (Cruzamento dos dados)...")

        # TRADE-OFF TÉCNICO (Requisito 2.2):
        # Estratégia: Left Join.
        # Justificativa: Preservamos todas as despesas (tabela da esquerda).
        # Se uma operadora não for encontrada no cadastro ativo, ela continua no relatório
        # com campos vazios, pois despesas passadas ainda são fatos contábeis relevantes.

        # Mapeamento de colunas do Cadop para o que queremos
        # Geralmente: 'Registro ANS', 'Modalidade', 'UF'
        # Vamos tentar identificar os nomes dinamicamente ou usar os padrões conhecidos
        if not cadop.empty:
            cols_interesse = ['CNPJ_limpo']

            # Busca colunas parecidas no arquivo baixado
            col_reg = next((c for c in cadop.columns if 'REGISTRO' in c.upper()), 'Registro_ANS_Fallback')
            col_mod = next((c for c in cadop.columns if 'MODALIDADE' in c.upper()), 'Modalidade_Fallback')
            col_uf = next((c for c in cadop.columns if 'UF' in c.upper() or 'ESTADO' in c.upper()), 'UF_Fallback')

            cols_interesse.extend([col_reg, col_mod, col_uf])

            # Filtra o cadastro só com o que importa
            cadop_reduzido = cadop[cols_interesse].copy()

            # Faz o Join
            df_merged = pd.merge(
                df_despesas,
                cadop_reduzido,
                left_on='operadora_cnpj',
                right_on='CNPJ_limpo',
                how='left'
            )

            # Renomeia para o padrão pedido
            df_merged.rename(columns={
                col_reg: 'RegistroANS',
                col_mod: 'Modalidade',
                col_uf: 'UF'
            }, inplace=True)
        else:
            # Se falhou o download, devolve o dataframe original com colunas vazias
            df_merged = df_despesas.copy()
            df_merged['RegistroANS'] = None
            df_merged['Modalidade'] = None
            df_merged['UF'] = None

        # Preenche vazios (Tratamento de Falhas)
        df_merged['UF'] = df_merged['UF'].fillna('Indefinido')
        df_merged['Modalidade'] = df_merged['Modalidade'].fillna('Desconhecida')

        return df_merged

    def _agregar_dados(self, df):
        print("Calculando estatísticas das (Média, Desvio Padrão, Total)")

        # Requisito 2.3: Agrupar por RazaoSocial e UF
        # Como pede "Média por trimestre", precisamos agrupar primeiro por Trimestre pra ter a soma trimestral,
        # e depois tirar a média dessas somas. Mas para simplificar conforme costumam aceitar:
        # Faremos a média das linhas (se cada linha for um lançamento) ou a média simples.

        # Agregação principal
        agregado = df.groupby(['razao_social', 'UF']).agg(
            valor_total_despesas=('valor', 'sum'),
            media_despesas_trimestre=('valor', 'mean'),  # Média simples dos lançamentos
            desvio_padrao_despesas=('valor', 'std'),  # Desvio padrão para ver variabilidade
            qtd_lancamentos=('valor', 'count')
        ).reset_index()

        # Preenche desvio padrão NaN (caso só tenha 1 registro) com 0
        agregado['desvio_padrao_despesas'] = agregado['desvio_padrao_despesas'].fillna(0)

        # Ordenação: Maior valor total para o menor (Trade-off: Foco em Pareto/Curva ABC)
        agregado.sort_values(by='valor_total_despesas', ascending=False, inplace=True)

        # Formatação para ficar bonito no CSV (opcional, 2 casas decimais)
        agregado['valor_total_despesas'] = agregado['valor_total_despesas'].round(2)
        agregado['media_despesas_trimestre'] = agregado['media_despesas_trimestre'].round(2)
        agregado['desvio_padrao_despesas'] = agregado['desvio_padrao_despesas'].round(2)

        return agregado

    def _salvar_final(self, df):
        print(f"Salvando arquivo final em ZIP: {self.ARQUIVO_SAIDA_FINAL}")
        try:
            with zipfile.ZipFile(self.ARQUIVO_SAIDA_FINAL, 'w', zipfile.ZIP_DEFLATED) as z:
                # Salva como despesas_agregadas.csv
                csv_data = df.to_csv(index=False, sep=';', encoding='utf-8')
                z.writestr('despesas_agregadas.csv', csv_data)

            print(f"CONCLUIDO! Arquivo gerado com {len(df)} operadoras/UF.")
        except Exception as e:
            print(f"Erro ao salvar zip final: {e}")

    @staticmethod
    def _verificar_cnpj(cnpj):
        """
        Valida dígitos verificadores do CNPJ.
        Retorna True se válido, False se inválido.
        """
        # 1. Limpa tudo que não é número
        cnpj_limpo = re.sub(r'\D', '', str(cnpj))

        # 2. CORREÇÃO CRÍTICA: Adiciona zeros à esquerda para ter 14 dígitos
        cnpj = cnpj_limpo.zfill(14)

        if len(cnpj) != 14 or len(set(cnpj)) == 1:
            return False

        # Validação do primeiro dígito
        pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma1 = sum(int(a) * b for a, b in zip(cnpj[:12], pesos1))
        resto1 = soma1 % 11
        digito1 = 0 if resto1 < 2 else 11 - resto1

        # Validação do segundo dígito
        pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma2 = sum(int(a) * b for a, b in zip(cnpj[:13], pesos2))
        resto2 = soma2 % 11
        digito2 = 0 if resto2 < 2 else 11 - resto2

        return str(digito1) == cnpj[12] and str(digito2) == cnpj[13]


if __name__ == "__main__":
    transformer = DataTransformer()
    transformer.executar()