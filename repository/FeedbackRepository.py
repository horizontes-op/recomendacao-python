from configs.connection import DBConnectionHandler
from entities.Feedback import Feedback

class FeedbackRepository:
    def select(self):
        with DBConnectionHandler() as db:
            data = db.session.query(Feedback).all()
            dados_formatados = [feedback.to_dict() for feedback in data]
            return dados_formatados
    def insert (self, id_usuario, qtd_estrelas, comentario):
        with DBConnectionHandler() as db:
            feedback = Feedback( id_usuario = id_usuario,qtd_estrelas= qtd_estrelas,comentario=comentario)
            db.session.add(feedback)
            db.session.commit()     
            return feedback.to_dict()