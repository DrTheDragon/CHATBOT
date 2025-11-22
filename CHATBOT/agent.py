from mangaba import Agent, Task, Crew

def consultar_ia(pergunta_cliente, texto_catalogo):
    
    # cria o agent e define as caracteristicas
    vendedor = Agent(
        role="Atendente Virtual Especialista",
        goal="Vender produtos e tirar dúvidas usando APENAS o catálogo fornecido.",
        backstory="""
        Você é um vendedor útil, direto e carismático. 
        Você trabalha para a loja e seu objetivo é fechar vendas.
        Use emojis moderadamente.
        Se o produto não estiver no catálogo, diga educadamente que não temos.
        """,
        verbose=True 
    )

    # pergunta + script
    tarefa_venda = Task(
        description=f"""
        CONTEXTO DO CATÁLOGO ATUAL:
        ---
        {texto_catalogo}
        ---

        PERGUNTA DO CLIENTE:
        '{pergunta_cliente}'

        SUA MISSÃO:
        1. Analise o catálogo para ver se temos o que ele quer.
        2. Responda a pergunta sugerindo o produto exato e o preço.
        3. Se houver mais de uma opção, compare brevemente.
        4. Se não houver nada parecido, sugira algo próximo ou peça desculpas.
        """,
        expected_output="Uma resposta natural de chat, curta e vendedora.",
        agent=vendedor
    )

    # equiepe vai ser o gemini + managba
    equipe = Crew(
        agents=[vendedor],
        tasks=[tarefa_venda],
        verbose=True
    )

    #  kickoff() manda  pro google e espera a volta
    resultado = equipe.kickoff()

    # Retorna o texto puro para a api devolver pro site
    return str(resultado)

# --- ÁREA DE TESTE RÁPIDO ---
# Se você rodar 'python agent.py', ele executa esse teste abaixo.
# Se você importar esse arquivo em outro lugar, ele ignora isso.
if __name__ == "__main__":
    import os
    # Configuração de emergência pra testar sozinho
    os.environ["LLM_PROVIDER"] = "google"
    os.environ["MODEL_NAME"] = "gemini-2.0-flash"
    os.environ["GOOGLE_API_KEY"] = "SUA_CHAVE_AQUI_SE_FOR_TESTAR_DIRETO"
    
    catalogo_fake = "| Produto: Notebook | Preço: 2000 |\n| Produto: Mouse | Preço: 50 |"
    resposta = consultar_ia("Quero um pc barato", catalogo_fake)
    print("\nRESPOSTA DA IA:\n", resposta)
