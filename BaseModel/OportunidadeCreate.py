
from pydantic import BaseModel
class OportunidadeCreate(BaseModel):
    nome: str
    area_atuacao: str
    descricao: str
    contato_email: str
    contato_telefone: str
    contato_site: str
    redes_sociais:str
    missao: str
    visao: str
    valores: str
    formas_ingresso: str
    processo_seletivo_data: str
    endereco: str    
    cidade: str
    estado: str
    diferenciais: str
    cursos_oferecidos: str
    processo_seletivo_detalhes: str
