from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd

# Configuração do ChromeDriver
caminho_chromedriver = "C:/Drive/chromedriver-win64/chromedriver.exe"  # Atualize com o caminho correto
service = Service(executable_path=caminho_chromedriver)
driver = webdriver.Chrome(service=service)

# Função para limpar e formatar o preço
def formatar_preco(preco):
    preco = preco.replace("\n", "")  # Remove quebras de linha
    preco = preco.replace("em", "") # Remove "em"
    preco = preco.replace("x", "x ") # Formatação idiota porque tenho toque
    preco = preco.replace("s juros", "") # Remove "Sem juros"
    preco = preco.strip()  # Remove espaços em branco extras
    return preco

# Função para coletar dados dos produtos
def coletar_dados(url):
    driver.get(url)
    
    produtos = driver.find_elements(By.CLASS_NAME, 'ui-search-result__content')
    
    dados = []
    for produto in produtos[:10]:  # Limita a coleta a 10 itens
        try:
            nome = produto.find_element(By.CLASS_NAME, 'ui-search-item__title').text
        except:
            nome = 'Não disponível'
        try:
            valor = produto.find_element(By.CLASS_NAME, 'ui-search-price__part').text
            valor = formatar_preco(valor)
        except:
            valor = 'Não disponível'
        try:
            vendedor = produto.find_element(By.CLASS_NAME, 'ui-search-official-store-label').text
        except:
            vendedor = 'Vendendor não encontrado'
        try:
            parcelas = produto.find_element(By.CLASS_NAME, 'ui-search-installments').text
            parcelas = formatar_preco(parcelas)
        except:
            parcelas = 'Somente a Vista'
        try:
            avaliacao = produto.find_element(By.CLASS_NAME, 'ui-search-reviews__rating-number').text
            quantidade = produto.find_element(By.CLASS_NAME, 'ui-search-reviews__amount').text
        except:
            avaliacao = 'Sem Avaliação'
            quantidade = '(0)'
        try:
            cupons = produto.find_element(By.CLASS_NAME, 'ui-search-price__second-line__label').text
            cupons = f'A vista: {cupons}' if cupons != '' else 'Não disponível'
        except:
            cupons = 'Não disponível'
        
        dados.append({
            'Nome': nome,
            'Valor': valor,
            'Vendedor': vendedor,
            'Parcelas e valor': parcelas,
            'Avaliação': avaliacao,
            'Quantidade': quantidade,
            'Cupons de descontos': cupons
        })
    
    return dados

# Links para coleta
links = [
    "https://lista.mercadolivre.com.br/chuveiro",
    "https://lista.mercadolivre.com.br/bicicleta"
]

todas_informacoes = []
for link in links:
    todas_informacoes.extend(coletar_dados(link))

# Fechar o navegador
driver.quit()

# Criar DataFrame e exportar para CSV
df = pd.DataFrame(todas_informacoes)
df.to_csv('dados_mercado_livre.csv', index=False)


