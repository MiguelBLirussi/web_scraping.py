from flask import Flask, render_template, request
import pandas as pd
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

app = Flask(__name__)

# Caminho do ChromeDriver
caminho_chromedriver = "C:/Drive/chromedriver-win64/chromedriver.exe"

# Função para limpar e formatar o preço
def formatar_preco(preco):
    preco = preco.replace("\n", "").strip()
    preco = preco.replace("em", "") #Retira "em"
    preco = preco.replace("x", "x ") #Formatação idiota porque toque!
    preco = preco.replace("s juros", "")
    return preco

# Função para coletar dados dos produtos
def coletar_dados(term, quantidade):
    service = Service(executable_path=caminho_chromedriver)
    driver = webdriver.Chrome(service=service)
    url = f"https://lista.mercadolivre.com.br/{term}"
    driver.get(url)
    time.sleep(5)
    
    produtos = driver.find_elements(By.CLASS_NAME, 'ui-search-result__content')

    dados = []
    for produto in produtos[:quantidade]:
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
            cupons = f'A vista: {cupons}'
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

    driver.quit()

    # Retornar os dados
    return dados

def limpar_dados(df):
    # Remove colunas que estão apenas com valores vazios
    df = df.dropna(how='all', axis=1)
    
    # Remove linhas que estão apenas com valores vazios
    df = df.dropna(how='all', axis=0)
    
    return df


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        termo = request.form['termo']
        quantidade = int(request.form['quantidade'])

        # Coletar dados do Mercado Livre
        dados = coletar_dados(termo, quantidade)

        # Criar DataFrame com os dados coletados
        df = pd.DataFrame(dados)

        # Limpar o DataFrame
        df = limpar_dados(df)

        # Verificar o conteúdo do DataFrame
        print(df.head())  # Adicione esta linha para depuração

        # Exibir a tabela na interface
        return render_template('index.html', tables=[df.to_html(classes='data')], titles=df.columns.values)

    return render_template('index.html')



if __name__ == '__main__':
    app.run(debug=True)
