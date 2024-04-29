from configs.connection import DBConnectionHandler
from entities.Recomendacao import Recomendacao

class RecomendacaoRepository:
        def select(self):
            with DBConnectionHandler() as db:
                data = db.session.query(Recomendacao).all()
                dados_formatados = [recomendacao.to_dict() for recomendacao in data]
                return dados_formatados
        
        def insert(self, id_usuario, id_oportunidade, score):
            with DBConnectionHandler() as db:
                recomendacao = Recomendacao(id_usuario=id_usuario, id_oportunidade=id_oportunidade, score=score)
                db.session.add(recomendacao)
                db.session.commit()
                return recomendacao.to_dict()
        