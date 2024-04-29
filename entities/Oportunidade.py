
from sqlalchemy import Column, Integer, Float, String
from configs.base import Base

class Oportunidade():
    __tablename__ = 'oportunidade'
    __table_args__ = {'schema': 'oportunidade'} 
    id=  Column(Integer, primary_key=True)
    nome= Column(String)
    area_atuacao= Column(String)
    descricao= Column(String)
    contato_email= Column(String)
    contato_telefone= Column(String)
    contato_site= Column(String)
    redes_sociais=Column(String)
    missao= Column(String)
    visao= Column(String)
    valores= Column(String)
    formas_ingresso= Column(String)
    processo_seletivo_data= Column(String)
    endereco= Column(String)    
    cidade= Column(String)
    estado= Column(String)
    diferenciais= Column(String)
    cursos_oferecidos= Column(String)
    processo_seletivo_detalhes= Column(String)


    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "area_atuacao": self.area_atuacao,
            "descricao": self.descricao,
            "contato_email": self.contato_email,
            "contato_telefone": self.contato_telefone,
            "contato_site": self.contato_site,
            "redes_sociais": self.redes_sociais,
            "missao": self.missao,
            "visao": self.visao,
            "valores": self.valores,
            "formas_ingresso": self.formas_ingresso,
            "processo_seletivo_data": self.processo_seletivo_data,
            "endereco": self.endereco,
            "cidade": self.cidade,
            "estado": self.estado,
            "diferenciais": self.diferenciais,
            "cursos_oferecidos": self.cursos_oferecidos,
            "processo_seletivo_detalhes": self.processo_seletivo_detalhes
        }