from pydantic import BaseModel
from typing import List

class JogadorBase(BaseModel):
    nome: str
    nota: float

class JogadorCreate(JogadorBase):
    pass

class Jogador(JogadorBase):
    id: int
    pelada_id: int

    class Config:
        from_attributes = True

class PeladaBase(BaseModel):
    nome: str

class PeladaCreate(PeladaBase):
    pass

class Pelada(PeladaBase):
    id: int
    dono_id: int
    jogadores: List[Jogador] = []

    class Config:
        from_attributes = True

class UsuarioBase(BaseModel):
    email: str

class UsuarioCreate(UsuarioBase):
    password: str

class Usuario(UsuarioBase):
    id: int
    peladas: List[Pelada] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class SorteioRequest(BaseModel):
    jogadores_ids: List[int]

class SorteioResponse(BaseModel):
    time_A: List[Jogador]
    time_B: List[Jogador]
    time_C: List[Jogador]
    time_D: List[Jogador]

class EstatisticaJogadorCreate(BaseModel):
    jogador_id: int
    gols: int = 0
    assistencias: int = 0

class PartidaCreate(BaseModel):
    data: str # ex: "2025-06-06"
    estatisticas: List[EstatisticaJogadorCreate]

class Partida(PartidaCreate):
    id: int
    
    class Config:
        from_attributes = True

class JogadorRanking(BaseModel):
    jogador_id: int
    nome: str
    total_gols: int
    total_assistencias: int