from fastapi import FastAPI, UploadFile, File, HTTPException # p entrada e saida de infos
from fastapi.middleware.cors import CORSMiddleware # evitar erro 
from pydantic import BaseModel # gerantir que chegue o dado certo
import shutil # pegar arquivos no buffer
import os
import requests # enviar p empresa

from agent import consultar_ia
from until import carregar_dados_como_txt

app = FastAPI()

# --- CONFIGS ---
origins = ["*"]  # isso aqui e pro navegador nao dar erro, o certo e deixar o dominio do site

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True, # aceitar cookies
    allow_methods=["*"], # a web pode usar todas as acoes
    allow_headers=["*"], # aceitar qualquer header do front
)

# converte a string json num objeto python
class ChatRequest(BaseModel):
    mensagem: str 

PASTA_UPLOADS = "uploads"
os.makedirs(PASTA_UPLOADS, exist_ok=True) # garante q a pasta exitse


# --- BD ---

URL_SERVIDOR_EMPRESA = "https://sua-empresa.com/api/receber" # dom da empresa
def salvar_resposta_local(pergunta: str, resposta: str):
    #salva pergunta + resposta no historico
    try:
        with open("historico_respostas.txt", "a", encoding="utf-8") as f:
            f.write(f"Pergunta: {pergunta}\n")
            f.write(f"Resposta: {resposta}\n")
            f.write("-" * 20 + "\n") # Separador visual
    except Exception as e:
        print(f"Erro ao salvar local: {e}")

def enviar_para_servidor_empresa(resposta: str):
    #envia resposta para o server so envia se tiver a url
    if "sua-empresa.com" in URL_SERVIDOR_EMPRESA: 
        return 

    try:
        payload = {"resposta": resposta}
        # timeout=2 garante que o chat nao trava se a empresa demorar pra responder
        r = requests.post(URL_SERVIDOR_EMPRESA, json=payload, timeout=2)
        print("Enviado para servidor da empresa:", r.status_code)
    except Exception as e:
        print("Erro ao enviar para servidor da empresa (mas o chat segue):", e)


# --- ENDPOINT ---

# se get for usado, home sera executado
@app.get("/")
def home():
    return {"status": "rodando sem problemas"}

# se post for p upload, recebe o arquivo e salva
@app.post("/upload")
async def upload_catalogo(file: UploadFile = File(...)):
    try:
        caminho_arquivo = os.path.join(PASTA_UPLOADS, file.filename)

        # salva o arquivo localmente
        with open(caminho_arquivo, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"mensagem": f"arquivo {file.filename} recebido com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao salvar arquivo: {str(e)}")

# se post for enviado para /chat, valida json, chama ia e retorna a resp
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # carrega os dado do arquivo mais recente
        texto_catalogo = carregar_dados_como_txt()

        if "ERRO" in texto_catalogo:
            return {"resposta": texto_catalogo}

        # chama o agente
        resposta_ia = consultar_ia(request.mensagem, texto_catalogo)

        # salva no TXT local pergunta e resposta
        salvar_resposta_local(request.mensagem, resposta_ia)

        # renta enviar para o server
        enviar_para_servidor_empresa(resposta_ia)
        return {"resposta": resposta_ia}

    except Exception as e:
        print(f"Erro no chat: {e}") # mostra no terminal
        raise HTTPException(status_code=500, detail=str(e))

# rota extra p ler o histórico TXT no navegador
@app.get("/historico")
async def get_historico():
    try:
        if not os.path.exists("historico_respostas.txt"):
            return {"historico": "Nenhum histórico encontrado."}

        with open("historico_respostas.txt", "r", encoding="utf-8") as f:
            conteudo = f.read()

        return {"historico": conteudo}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#swagger
#uvicorn main:app --reload
#http://127.0.0.1:8000/docs

