# o main.py vai salvar o JSON neste arquivo aqui
# basicamente esse arquivo procura o o ultimo estoque enviado
import pandas as pd
import os
import glob
import json

# pasta
PASTA_UPLOADS = "uploads"

# procura arquvio mais novo
def encontrar_ultimo_catalogo():
    # Se a pasta não existe cria ela
    if not os.path.exists(PASTA_UPLOADS):
        os.makedirs(PASTA_UPLOADS)
        return None

    # pega todos os arquivos da pasta
    arquivos = glob.glob(os.path.join(PASTA_UPLOADS, "*"))
    
    if not arquivos:
        return None

    # pega o mais recente
    return max(arquivos, key=os.path.getmtime)
def carregar_dados_como_txt():
    #parte de encontrar o arquivo igual
    arquivo = encontrar_ultimo_catalogo() 
    
    try:
        # se for json
        if arquivo.endswith(".json"):
           
            df = pd.read_json(arquivo)
        elif arquivo.endswith(".xlsx") or arquivo.endswith(".xls"):
            # se for excel
            df = pd.read_excel(arquivo)
        elif arquivo.endswith(".csv"):
            # se for csv
            df = pd.read_csv(arquivo)
        else:
            return "Formato não suportado!"

        # deixa o arquivo legivel p o gemini
        texto_final = df.to_markdown(index=False)
        return texto_final

    except Exception as e:
        return f"Erro ao ler: {e}"



