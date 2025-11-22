# Cria a lore do bot e acessa a key
import os
import sys

os.environ["LLM_PROVIDER"] = "google"
os.environ["MODEL_NAME"] = "gemini-2.0-flash" 
os.environ["GOOGLE_API_KEY"] = "chave"

from mangaba import Agent, Task, Crew

def consultar_ia(pergunta_cliente, texto_catalogo):
    
    # agente
    vendedor = Agent(
        role="atendente virtual especialista",
        goal="vender produtos usando o catalogo.",
        backstory="Você e um vendedor útil. Se não tiver o produto, avise.",
        verbose=True 
    )

    # tarefa
    tarefa = Task(
        description=f"""
        CATÁLOGO ATUAL:
        ---
        {texto_catalogo}
        ---

        CLIENTE PERGUNTOU: '{pergunta_cliente}'

        responda sugerindo o produto e preço.
        """,
        expected_output="resposta curta.",
        agent=vendedor
    )

    # executa
    equipe = Crew(agents=[vendedor], tasks=[tarefa], verbose=True)
    resultado = equipe.kickoff()

    return str(resultado)

