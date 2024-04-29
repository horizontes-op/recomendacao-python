from pydantic import BaseModel
class RecomendacaoCreate(BaseModel):
    id_usuario: str
    id_oportunidade: int
    score: float

