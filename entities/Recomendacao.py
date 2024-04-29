from sqlalchemy import Column, Integer, Float, String
from configs.base import Base

class Recomendacao(Base):
    __tablename__ = 'recomendacao'
    __table_args__ = {'schema': 'recomendacao'}  # Especificando o e
    id = Column(Integer, primary_key=True)
    id_usuario = Column(String)
    id_oportunidade = Column(Integer)
    score = Column(String)

    def to_dict(self):
        return {
            "id": self.id,
            "id_usuario": self.id_usuario,
            "qtd_estrelas": self.id_oportunidade,
            "comentario": self.score
        }