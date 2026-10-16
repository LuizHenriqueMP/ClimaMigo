
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Carrega as variáveis do .env
load_dotenv()

MODELO_GROQ = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)

# Configuração do modelo
llm = ChatGroq(
    model=MODELO_GROQ,
    temperature=0.3,
    max_retries=2,
    timeout=30,
)

# Instruções para gerar recomendações meteorológicas
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        Você é o assistente meteorológico do ClimaMigo.
        Responda em português brasileiro, de forma clara,
        amigável e objetiva.

        Use somente as informações meteorológicas fornecidas.
        Recomende roupas e acessórios adequados ao clima.
        Considere temperatura, chuva, vento e mudanças
        previstas para as próximas horas.

        Não invente dados meteorológicos.
        Se alguma informação não estiver disponível,
        não afirme que ela foi verificada.
        """
    ),
    (
        "human",
        """
        Cidade: {cidade}

        Dados da previsão:
        {previsao}

        Gere uma recomendação prática para o usuário.
        """
    ),
])

# Encadeia o prompt e o modelo
cadeia = prompt | llm


def gerar_recomendacao(cidade, previsao):
    try:
        resposta = cadeia.invoke({
            "cidade": str(cidade),
            "previsao": str(previsao),
        })

        return resposta.content

    except Exception as erro:
        print(
            f"Erro no LangChain/Groq: "
            f"{type(erro).__name__}: {erro}"
        )
        raise RuntimeError(
            "Não foi possível gerar a recomendação "
            "com o modelo de linguagem."
        ) from erro
