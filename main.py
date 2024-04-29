from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from models import Oportunidade, Recomendacao, Feedback
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


# ----------------- Database ----------------- #
env_path = Path(".") / '.env'
load_dotenv(dotenv_path=env_path)
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")

# ----------------- Database ----------------- #

postgres_url = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

engine = create_engine(postgres_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

# ----------------- Config OpenAPI ----------------- #
# Carregar variáveis de ambiente do arquivo .env

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("API key não encontrada. Certifique-se de que o arquivo .env está configurado corretamente.")

# ----------------- FAISS ----------------- #

OPENAI_API_KEY = api_key
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model="text-embedding-3-large")
faiss_db = FAISS.load_local("oportunidades_embeddings", embeddings, allow_dangerous_deserialization=True)

# ----------------- FastAPI ----------------- #

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)

# ----------------- Search ----------------- #

class AlunoId(BaseModel):
    id_aluno: str

@app.get('/')
async def home():
    return {'hello': 'world'}

# Ensure read_oportunidades_nome uses dependency injection correctly
@app.get("/oportunidades/nome/{nome}", response_model=List[Oportunidade])
def read_oportunidades_nome(*, session: Session = Depends(get_session), nome: str):
    oportunidades = session.exec(select(Oportunidade).where(Oportunidade.nome == nome)).first()
    return oportunidades


# Update save_recomendacoes to use a session from FastAPI's dependency system
def save_recomendacoes(results, aluno_id, session: Session):
    for result in results:
        # Ensure you pass a session instance here
        oportunidade = read_oportunidades_nome(session=session, nome=result["nome"])
        print(oportunidade)
        if oportunidade:
            id_opo = oportunidade.id
            recomendacao = Recomendacao(id_usuario=aluno_id, id_oportunidade=id_opo)
            print(recomendacao)
            create_recomendacao(session=session, recomendacao=recomendacao)

@app.post('/search')
async def search(input: AlunoId, session: Session = Depends(get_session)):
    id = input.id_aluno
    url = f'http://3.140.128.237:8080/aluno/{id}'
    response = requests.get(url)
    # parse response to a dict
    aluno = response.json()
    query = f'Me encontro no nivel de escolaridade {aluno["escolaridade"]}. Tenho interesse em {aluno["areas_interesse"]}. Sobre mim: {aluno["descricao"]}'
    match_results = None
    if aluno["disponibilidade_de_deslocamento"] == "cidade" or aluno["disponibilidade_de_deslocamento"] == "estado":
        results = faiss_db.similarity_search_with_score(query, 103)
        info = [json.loads(x[0].page_content.replace("'", '"')) for x in results]
        filtered_results = filter_oportunidades(info, aluno)
        if len(filtered_results) == 0:
            match_results = info[:5]
        elif len(filtered_results) > 5:
            match_results = filtered_results[:5]
        else:
            match_results = filtered_results
    else:
        results = faiss_db.similarity_search_with_score(query, 5)
        info = [json.loads(x[0].page_content.replace("'", '"')) for x in results]
        match_results = info
    save_recomendacoes(match_results, id, session)
    return {'text': match_results}



def filter_oportunidades(results, aluno):
    disp = aluno["disponibilidade_de_deslocamento"]
    al_cidade = aluno["cidade"]
    al_estado = aluno["uf"]
    if disp == "cidade":
        results = [x for x in results if (unidecode(x['cidade'])).lower() == unidecode(al_cidade).lower()]
    elif disp == "estado":
        results = [x for x in results if (unidecode(x['uf'])).lower() == unidecode(al_estado).lower()]
    return results

# ----------------- Oportunidade ----------------- #


@app.post("/oportunidades/", response_model=Oportunidade)
def create_oportunidade(*, session: Session = Depends(get_session), oportunidade: Oportunidade):
    dict_oportunidade = oportunidade.dict()
    for key in dict_oportunidade:
        if dict_oportunidade[key] != None:
            if not isinstance(dict_oportunidade[key], str):
                dict_oportunidade[key] = str(dict_oportunidade[key])
    db_oportunidade = Oportunidade.model_validate(dict_oportunidade)
    session.add(db_oportunidade)
    session.commit()
    session.refresh(db_oportunidade)
    return db_oportunidade


@app.get("/oportunidades/", response_model=List[Oportunidade])
def read_oportunidades(
    *,
    session: Session = Depends(get_session)
):
    oportunidades = session.exec(select(Oportunidade)).all()
    return oportunidades



@app.get("/oportunidades/{oportunidade_id}", response_model=Oportunidade)
def read_oportunidade(*, session: Session = Depends(get_session), oportunidade_id: int):
    oportunidade = session.get(Oportunidade, oportunidade_id)
    if not oportunidade:
        raise HTTPException(status_code=404, detail="Oportunidade not found")
    return oportunidade

@app.patch("/oportunidades/{oportunidade_id}", response_model=Oportunidade)
def update_oportunidade(
    *, session: Session = Depends(get_session), oportunidade_id: int, oportunidade: Oportunidade
):
    db_oportunidade = session.get(Oportunidade, oportunidade_id)
    if not db_oportunidade:
        raise HTTPException(status_code=404, detail="Oportunidade not found")
    oportunidade_data = oportunidade.model_dump(exclude_unset=True)
    for key, value in oportunidade_data.items():
        setattr(db_oportunidade, key, value)
    session.add(db_oportunidade)
    session.commit()
    session.refresh(db_oportunidade)
    return db_oportunidade


@app.delete("/oportunidades/{oportunidade_id}")
def delete_oportunidade(*, session: Session = Depends(get_session), oportunidade_id: int):
    oportunidade = session.get(Oportunidade, oportunidade_id)
    if not oportunidade:
        raise HTTPException(status_code=404, detail="Oportunidade not found")
    session.delete(oportunidade)
    session.commit()
    return {"ok": True}


# ----------------- Recomendacao ----------------- #


def create_recomendacao(*, session: Session = Depends(get_session), recomendacao: Recomendacao):
    db_recomendacao = Recomendacao.model_validate(recomendacao)
    print(db_recomendacao)
    session.add(db_recomendacao)
    session.commit()
    session.refresh(db_recomendacao)
    return db_recomendacao

@app.get("/recomendacoes/", response_model=List[Recomendacao])
def read_recomendacoes(
    *,
    session: Session = Depends(get_session)
):
    recomendacoes = session.exec(select(Recomendacao)).all()
    return recomendacoes

@app.get("/recomendacoes/{recomendacao_id}", response_model=Recomendacao)
def read_recomendacao(*, session: Session = Depends(get_session), recomendacao_id: int):
    recomendacao = session.get(Recomendacao, recomendacao_id)
    if not recomendacao:
        raise HTTPException(status_code=404, detail="Recomendacao not found")
    return recomendacao

@app.get("/recomendacoes/aluno/{aluno_id}", response_model=List[Recomendacao])
def read_recomendacoes_aluno(*, session: Session = Depends(get_session), aluno_id: str):
    recomendacoes = session.exec(select(Recomendacao).where(Recomendacao.id_aluno == aluno_id)).all()
    return recomendacoes

# ----------------- Feedback ----------------- #

@app.post("/feedback/", response_model=Feedback)
def create_feedback(*, session: Session = Depends(get_session), feedback: Feedback):
    db_feedback = Feedback.model_validate(feedback)
    session.add(db_feedback)
    session.commit()
    session.refresh(db_feedback)
    return db_feedback

@app.get("/feedback/", response_model=List[Feedback])
def read_feedbacks(
    *,
    session: Session = Depends(get_session)
):
    feedbacks = session.exec(select(Feedback)).all()
    return feedbacks

@app.get("/feedback/{feedback_id}", response_model=Feedback)
def read_feedback(*, session: Session = Depends(get_session), feedback_id: int):
    feedback = session.get(Feedback, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback

@app.get("/feedback/aluno/{aluno_id}", response_model=List[Feedback])
def read_feedbacks_aluno(*, session: Session = Depends(get_session), aluno_id: str):
    feedbacks = session.exec(select(Feedback).where(Feedback.id_aluno == aluno_id)).all()
    return feedbacks



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)