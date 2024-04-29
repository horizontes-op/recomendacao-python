from configs.connection import DBConnectionHandler
from entities.Oportunidade import Oportunidade

class OportunidadeRepository:
        def select(self):
           with DBConnectionHandler() as db:
               data = db.session.query(Oportunidade).all()
               dados_formatados = [oportunidade.to_dict() for oportunidade in data]
               return dados_formatados
        def insert(self, *oportunidade):
            with DBConnectionHandler() as db:
                db.session.add(oportunidade)
                db.session.commit()
                return oportunidade.to_dict()