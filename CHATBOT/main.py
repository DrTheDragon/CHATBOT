from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import psycopg2
from datetime import datetime

from agent import consultar_ia
from until import carregar_dados_como_txt


# ==============================
# CONFIG DO FASTAPI
# ==============================
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    mensagem: str


PASTA_UPLOADS = "uploads"
os.makedirs(PASTA_UPLOADS, exist_ok=True)


# ==============================
# CONFIG BANCO DE DADOS SUPABASE
# ==============================
DATABASE_URL = "postgresql://postgres:qualquerempresa@db.ttekfuhzypbaaugruvsr.supabase.co:5432/postgres"


def salvar_no_banco(pergunta: str, resposta: str):
    """Salva pergunta e resposta no banco Supabase"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Criar tabela se não existir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historico_chat (
                id SERIAL PRIMARY KEY,
                pergunta TEXT NOT NULL,
                resposta TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL
            );
        """)

        # Inserir os dados
        cursor.execute("""
            INSERT INTO historico_chat (pergunta, resposta, timestamp)
            VALUES (%s, %s, %s)
        """, (pergunta, resposta, datetime.now()))

        conn.commit()
        cursor.close()
        conn.close()

        print("Dados enviados ao banco Supabase.")

    except Exception as e:
        print("❌ ERRO ao salvar no banco Supabase:", e)



# ==============================
# ROTAS DA API
# ==============================
@app.get("/")
def home():
    return {"status": "rodando sem problemas"}



@app.post("/upload")
async def upload_catalogo(file: UploadFile = File(...)):
    try:
        caminho_arquivo = os.path.join(PASTA_UPLOADS, file.filename)

        with open(caminho_arquivo, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"mensagem": f"arquivo {file.filename} recebido com sucesso!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao salvar arquivo: {str(e)}")



@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # carregar dados do catalogo
        texto_catalogo = carregar_dados_como_txt()

        if "ERRO" in texto_catalogo:
            return {"resposta": texto_catalogo}

        # IA responde
        resposta_ia = consultar_ia(request.mensagem, texto_catalogo)

        # salvar no banco Supabase
        salvar_no_banco(request.mensagem, resposta_ia)

        # responder ao front
        return {"resposta": resposta_ia}

    except Exception as e:
        print(f"Erro no chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/historico")
async def get_historico():
    """Lê os dados do banco Supabase"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        cursor.execute("SELECT pergunta, resposta, timestamp FROM historico_chat ORDER BY id DESC")
        registros = cursor.fetchall()

        cursor.close()
        conn.close()

        historico = [
            {
                "pergunta": r[0],
                "resposta": r[1],
                "timestamp": r[2].isoformat()
            }
            for r in registros
        ]

        return {"historico": historico}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
