
from sqlalchemy import Column, Integer, Float, String
from configs.base import Base

class Feedback(Base):
    __tablename__ = 'feedback'
    __table_args__ = {'schema': 'feedback'} 
    id=  Column(Integer, primary_key=True)
    id_usuario= Column(String)
    qtd_estrelas= Column(Integer)
    comentario= Column(String)
  

    def to_dict(self):
        return {
            "id": self.id,
            "id_usuario": self.id_usuario,
            "qtd_estrelas": self.qtd_estrelas,
            "comentario": self.comentario
        }