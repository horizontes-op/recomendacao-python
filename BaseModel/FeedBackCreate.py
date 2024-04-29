from pydantic import BaseModel
class FeedbackCreate(BaseModel):
    id_usuario: str
    qtd_estrelas: int
    comentario: str
  