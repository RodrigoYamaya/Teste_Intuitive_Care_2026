import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class ANSDownloader:

    """
    Essa classe tem que comprir alguns desafios?
    1)iremos passar "API" para download dos arquivos ans(done)
    2) apos isso iremos organiza esses dados em ano e 3 trimestre no formato americano(done).
    3) apos isso iremos fazer o download numa pasta "arquivo_ans"(done).
    """

    # url dos dados ans que iremos fazer download
    BASE_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"

    # definindo o destino da pasta onde iremos salvar e vai criar um caminho para a pasta arquivos_ans
    DESTINO_DIR = os.path.join(os.path.dirname(__file__), "../arquivos_ans")

    def __init__(self):
        # Garantir que a pasta de destino exista
        if not os.path.exists(self.DESTINO_DIR):
            os.makedirs(self.DESTINO_DIR)
            print(f"Pasta criada: {self.DESTINO_DIR}")

    def _obter_links(self, url):
        # vai pegar todos os links da pagina que do url que nos inserimos "html"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return []
            soup = BeautifulSoup(response.text, 'html.parser')
            # vai  Retorna links válidos
            return [href.get('href') for href in soup.find_all('a') if href.get('href')]
        except Exception as e:
            return []

    def baixar_arquivo_direto(self, url_completa, nome_arquivo):
        caminho_salvar = os.path.join(self.DESTINO_DIR, nome_arquivo)
        print(f"BAIXANDO: {nome_arquivo} (Trimestre encontrado!)")
        try:
            dado = requests.get(url_completa, timeout=60)
            with open(caminho_salvar, 'wb') as f:
                f.write(dado.content)
            return caminho_salvar
        except Exception as e:
            print(f"Erro ao baixar {nome_arquivo}: {e}")
            return None

    def baixar_ultimos_3_trimestres(self):
        print("iniciando o download dos dados da ANS...")

        # 1) Lista dos Anos disponíveis e ordenados  do mais recente pro antigo
        links_anos = self._obter_links(self.BASE_URL)
        anos = sorted([l for l in links_anos if l.strip('/').isdigit()], reverse=True)

        trimestres_baixados_contador = 0
        arquivos_finais = []

        # 2) Varre por anos
        for ano in anos:
            if trimestres_baixados_contador >= 3:
                break

            if "2025" in ano:
                print(f"Pulando o ano {ano} para garantir dados estáveis...")
                continue

            print(f" Verificando ano: {ano.strip('/')}...")
            url_ano = urljoin(self.BASE_URL, ano)
            links_itens = self._obter_links(url_ano)

            # vai pegar as pastas (ou zips) que têm "T" e ordena decrescente
            itens_trimestres = sorted([t for t in links_itens if 'T' in t.upper()], reverse=True)

            # 3. vai Varre os trimestres (itens encontrados)
            for item in itens_trimestres:
                if trimestres_baixados_contador >= 3:
                    print("dados dos 3 trimestres obtidos!")
                    break

                print(f" Encontrado possível trimestre: {item.strip('/')} de {ano.strip('/')}")
                url_item = urljoin(url_ano, item)

                # Verifica se o item JÁ É O ZIP (Caso de 2025)
                if item.lower().endswith('.zip'):
                    caminho = self.baixar_arquivo_direto(url_item, item)
                    if caminho:
                        arquivos_finais.append(caminho)
                        trimestres_baixados_contador += 1

                # Se não for ZIP, assume que é PASTA (Caso de 2024)
                else:
                    links_arquivos = self._obter_links(url_item)

                    # 4. vai Achar o ZIP dentro da pasta
                    zips = [f for f in links_arquivos if f.lower().endswith('.zip')]

                    if zips:
                        # vai por um tem 1 zip por pasta, mas caso se tiver mais, vai pega o primeiro
                        zip_file = zips[0]
                        url_download = urljoin(url_item, zip_file)

                        caminho = self.baixar_arquivo_direto(url_download, zip_file)
                        if caminho:
                            arquivos_finais.append(caminho)
                            trimestres_baixados_contador += 1  # Conta +1 sucesso

        print(f" Processo Finalizado! {len(arquivos_finais)} arquivos baixados.")
        return arquivos_finais


# vai permitrmos que vai rodar esses arquivo direto para testar
if __name__ == "__main__":
    robo = ANSDownloader()
    robo.baixar_ultimos_3_trimestres()