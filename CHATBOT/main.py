from fastapi import FastAPI, UploadFile, File, HTTPException #p entrada e saida de infos
from fastapi.middleware.cors import CORSMiddleware #evitar erro 
from pydantic import BaseModel #gerantir que chegue o dado certo
import shutil #pegar arquivos no buffer
import os

from agent import consultar_ia
from until import carregar_dados_como_txt

app = FastAPI()

origins = ["*"]  # isso aqui e pro navegador nao dar erro, o certo e deixar o dominio do site

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True, #aceitar cookies
    allow_methods=["*"], # a web pode usar todas as acoes
    allow_headers=["*"], # aceitar qualquer header do front
)

# converte a string json num objeto python
class ChatRequest(BaseModel):
    mensagem: str 

PASTA_UPLOADS = "uploads"
os.makedirs(PASTA_UPLOADS, exist_ok=True) # garante q a pasta exitse

# ENDPOINT

# se get for usado, home sera executado
@app.get("/")
def home():
    return {"status": "rodando sem problemas"}

# se post for p upload, recebe o arquivo e salva
@app.post("/upload")
async def upload_catalogo(file: UploadFile = File(...)):
    try:
        caminho_arquivo = os.path.join(PASTA_UPLOADS, file.filename)
        # Salva o arquivo localmente
        with open(caminho_arquivo, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {"mensagem": f"arquivo {file.filename} recebido com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao salvar arquivo: {str(e)}")
        
# Se post for enviado para /chat, valida json, chama ia e retorna a resp
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Carrega os dado do arquivo mais recente
        texto_catalogo = carregar_dados_como_txt()
        
        if not texto_catalogo:
            return {"resposta": "Nenhum catálogo encontrado. Por favor, faça o upload primeiro."}

        # chama o agente 
        resposta_ia = consultar_ia(request.mensagem, texto_catalogo)
        
        return {"resposta": resposta_ia}
    
    except Exception as e:
        print(f"Erro no chat: {e}") # mostra no terminal
        raise HTTPException(status_code=500, detail=str(e))
