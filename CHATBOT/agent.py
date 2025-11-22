import os
from mangaba_ai import MangabaAgent
from dotenv import load_dotenv

# importa  função de leitura 
from utils import carregar_dados

# Carrega configus
load_dotenv()

# congifgs da chave
if not os.getenv("GOOGLE_API_KEY"):
    os.environ["LLM_PROVIDER"] = "google"
    os.environ["MODEL_NAME"] = "gemini-2.0-flash"
    os.environ["GOOGLE_API_KEY"] = "AIzaSyDE-Ss-lBJS9ytaQeSd90Z_ESPWkDoZfk8"

def gerar_resposta_do_vendedor(mensagem_usuario, contexto_do_catalogo):
    """
    Função Mestra da IA.
    Recebe: Pergunta do Cliente + Texto do Catálogo
    Retorna: A resposta do Vendedor
    """
    
    print("AGENTE: Recebi os dados. Preparando cérebro...")

    # inicializa o Manga
    try:
        agent = MangabaAgent()
    except Exception as e:
        return f"Erro ao ligar a IA: {e}"
