from sqlmodel import Field, Relationship, SQLModel, MetaData
from typing import Optional

class Oportunidade(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    area_atuacao: str
    descricao: str
    contato_email: Optional[str] = None
    contato_telefone: Optional[str] = None
    contato_site: Optional[str] = None
    redes_sociais: Optional[str] = None
    missao: str
    visao: str
    valores: str
    formas_ingresso: Optional[str] = None
    processo_seletivo_data: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    uf: Optional[str] = None
    diferenciais: Optional[str] = None
    cursos_oferecidos: Optional[str] = None
    processo_seletivo_detalhes: Optional[str] = None

    metadata = MetaData(schema="oportunidade")

class Recomendacao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: str
    id_oportunidade: int

    metadata = MetaData(schema="recomendacao")

class Feedback(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: str
    qtd_estrelas: float
    comentario: str

    metadata = MetaData(schema="feedback")