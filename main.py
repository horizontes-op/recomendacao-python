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
    url = f'http://localhost:8080/aluno/{id}'
    response = requests.get(url)
    # parse response to a dict
    aluno = response.json()
    query = f'Sou de {aluno["cidade"]}-{aluno["uf"]}. Tenho interesse em: {aluno["areas_interesse"]}. {aluno["descricao"]}'
    results = new_db.similarity_search(query, 5)
    return {'text': [json.loads(x.page_content.replace("'", "\"")) for x in results]}