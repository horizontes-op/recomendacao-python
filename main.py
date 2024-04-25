from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import requests
import json

import uvicorn
import os
from dotenv import load_dotenv
from pathlib import Path

# Carregar variáveis de ambiente do arquivo .env
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Usar a chave de API carregada do arquivo .env
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("API key não encontrada. Certifique-se de que o arquivo .env está configurado corretamente.")

OPENAI_API_KEY = api_key
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model="text-embedding-3-large")
new_db = FAISS.load_local("./data/instituicoes_faiss", embeddings, allow_dangerous_deserialization=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)

class AlunoId(BaseModel):
    id_aluno: str

@app.get('/')
async def home():
    return {'hello': 'world'}

@app.post('/search')
async def search(input: AlunoId):
    id = input.id_aluno
    url = f'http://18.225.57.8:8080/aluno/{id}'
    response = requests.get(url)
    # parse response to a dict
    aluno = response.json()
    query = f'Sou de {aluno["cidade"]}-{aluno["uf"]}. Meu nome é {aluno["nome"]} {aluno["sobrenome"]}. meu genero é {aluno["genero"]}.
    minha escolaridade é {aluno["escolaridade"]}. minha renda per capita é {aluno["renda_per_capita"]}. meu turno disponível é {aluno["turno_disponivel"]}.
    eu estudo/estudei em {aluno["estudoEm"]}. minha disponibilidade de deslocamento em km é {aluno["disponibilidade_de_deslocamento"]}.
    minha modalidade de ensino é {aluno["modalidade_do_ensino"]}. minhas areas de interesse são {aluno["areas_interesse"]}. tipos de oportunidades que busco são {aluno["tipo_oportunidade"]}.
    minha descrição é {aluno["descricao"]}'
     
    results = new_db.similarity_search(query, 5)
    return {'text': [json.loads(x.page_content.replace("'", "\"")) for x in results]}