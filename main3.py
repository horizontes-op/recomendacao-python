from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from configs.connection import DBConnectionHandler
from entities.Recomendacao import Recomendacao
from repository.Recomendacao import RecomendacaoRepository
from BaseModel.RecomendacaoCreate import RecomendacaoCreate
from BaseModel.AlunoCreate import AlunoId 
from BaseModel.OportunidadeCreate import OportunidadeCreate
from BaseModel.FeedBackCreate import FeedbackCreate
from repository.FeedbackRepository import FeedbackRepository
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from models import Oportunidade, Recomendacao
import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json

from dotenv import load_dotenv
from pathlib import Path
from unidecode import unidecode

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("API key não encontrada. Certifique-se de que o arquivo .env está configurado corretamente.")

# ----------------- FAISS ----------------- #
OPENAI_API_KEY = api_key
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model="text-embedding-3-large")
faiss_db = FAISS.load_local("teste", embeddings, allow_dangerous_deserialization=True)

app = FastAPI()
recomendacao_repo = RecomendacaoRepository()

@app.get("/recomendacao/")
def get_recomendacoes():
    return recomendacao_repo.select()

@app.post("/recomendacao/")
def create_recomendacao(recomendacao_data: RecomendacaoCreate):
    return recomendacao_repo.insert(recomendacao_data.id_usuario, recomendacao_data.id_oportunidade, recomendacao_data.score)

def filter_oportunidades(results, aluno):
    disp = aluno["disponibilidade_de_deslocamento"]
    al_cidade = aluno["cidade"]
    al_estado = aluno["uf"]
    if disp == "cidade":
        results = [x for x in results if (unidecode(x['Cidade'])).lower() == unidecode(al_cidade).lower()]
    elif disp == "estado":
        results = [x for x in results if (unidecode(x['Estado'])).lower() == unidecode(al_estado).lower()]
    return results

@app.post('/search')
async def search(input: AlunoId):
    id = input.id_aluno
    url = f'http://3.140.128.237:8080/aluno/{id}'
    response = requests.get(url)
    # parse response to a dict
    aluno = response.json()
    query = f'Me encontro no nivel de escolaridade {aluno["escolaridade"]}. Tenho interesse em {aluno["areas_interesse"]}. Sobre mim: {aluno["descricao"]}'
    if aluno["disponibilidade_de_deslocamento"] == "cidade" or aluno["disponibilidade_de_deslocamento"] == "estado":
        results = faiss_db.similarity_search_with_score(query, 100)
        info = [json.loads(x[0].page_content.replace("'", '"')) for x in results]
        filtered_results = filter_oportunidades(info, aluno)
        if len(filtered_results) == 0:
            return {'text': info[:5]}
        if len(filtered_results) > 5:
            return {'text': filtered_results[:5]}
        return {'text': filtered_results}
    else:
        results = faiss_db.similarity_search_with_score(query, 5)
        info = [json.loads(x[0].page_content.replace("'", '"')) for x in results]
        return {'text': info}

@app.post('/feedback')
async def feedback(input: FeedbackCreate):
    repo = FeedbackRepository()
    return repo.insert(input.id_usuario, input.qtd_estrelas, input.comentario)

@app.get('/feedback')
async def get_feedback():
    repo = FeedbackRepository()
    return repo.select()




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5005)