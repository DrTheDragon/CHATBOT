# O main.py vai salvar o JSON neste arquivo aqui.
# O utils só precisa ler ele.
import pandas as pd
import json

def carregar_dados_como_txt():
    #parte de encontrar o arquivo igual ante
    arquivo = encontrar_ultimo_catalogo() 
    
    try:
        # se for json, 
        if arquivo.endswith(".json"):
           
            df = pd.read_json(arquivo)
        elif arquivo.endswith(".xlsx") or arquivo.endswith(".xls"):
            # Mse for excel
            df = pd.read_excel(arquivo)
        elif arquivo.endswith(".csv"):
            # se for csv
            df = pd.read_csv(arquivo)
        else:
            return "Formato não suportado!"

        # deixa o arquivo legivwel p o gemini
        texto_final = df.to_markdown(index=False)
        return texto_final

    except Exception as e:
        return f"Erro ao ler: {e}"
