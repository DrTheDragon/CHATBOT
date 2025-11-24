from fastapi import FastAPI, UploadFile, File, HTTPException # p entrada e saida de infos
from fastapi.middleware.cors import CORSMiddleware # evitar erro 
from pydantic import BaseModel # gerantir que chegue o dado certo
import shutil # pegar arquivos no buffer
import os
import psycopg2 # conectar no banco supabase
from datetime import datetime

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

# servidor da empresa (agora Supabase PostgreSQL)
URL_SERVIDOR_EMPRESA = "postgresql://postgres:qualqueremoresa@db.ttekfuhzypbaaugruvsr.supabase.co:6432/postgres"

def salvar_resposta_local(pergunta: str, resposta: str):
    #salva pergunta + resposta no historico
    try:
        with open("historico_respostas.txt", "a", encoding="utf-8") as f:
            f.write(f"Pergunta: {pergunta}\n")
            f.write(f"Resposta: {resposta}\n\n")
    except Exception as e:
        print(f"Erro ao salvar local: {e}")


def enviar_para_servidor_empresa(pergunta: str, resposta: str):
    # envia pergunta + resposta para o banco supabase
    try:
        conn = psycopg2.connect(URL_SERVIDOR_EMPRESA)
        cursor = conn.cursor()

        # cria tabela se não existir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS respostas_chat (
                id SERIAL PRIMARY KEY,
                pergunta TEXT NOT NULL,
                resposta TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL
            );
        """)

        # insere a pergunta e a resposta
        cursor.execute("""
            INSERT INTO respostas_chat (pergunta, resposta, timestamp)
            VALUES (%s, %s, %s)
        """, (pergunta, resposta, datetime.now()))

        conn.commit()
        cursor.close()
        conn.close()

        print("Pergunta e resposta enviadas ao Supabase.")

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

        # envia pergunta + resposta para o servidor (Supabase)
        enviar_para_servidor_empresa(request.mensagem, resposta_ia)

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

