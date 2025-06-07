from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    peladas = relationship("Pelada", back_populates="dono")

class Pelada(Base):
    __tablename__ = "peladas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    dono_id = Column(Integer, ForeignKey("usuarios.id"))

    dono = relationship("Usuario", back_populates="peladas")
    jogadores = relationship("Jogador", back_populates="pelada")
    partidas = relationship("Partida", back_populates="pelada")

class Jogador(Base):
    __tablename__ = "jogadores"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    posicao = Column(String)
    nota = Column(Float)
    
    pelada_id = Column(Integer, ForeignKey("peladas.id")) # <-- CAMPO NOVO
    pelada = relationship("Pelada", back_populates="jogadores")

class Partida(Base):
    __tablename__ = "partidas"
    id = Column(Integer, primary_key=True, index=True)
    data = Column(String, index=True)
    
    pelada_id = Column(Integer, ForeignKey("peladas.id")) # <-- CAMPO NOVO
    pelada = relationship("Pelada", back_populates="partidas")
    estatisticas = relationship("EstatisticaPartida", back_populates="partida")

class EstatisticaPartida(Base):
    __tablename__ = "estatisticas_partida"
    id = Column(Integer, primary_key=True, index=True)
    gols = Column(Integer, default=0)
    assistencias = Column(Integer, default=0)
    
    jogador_id = Column(Integer, ForeignKey("jogadores.id"))
    partida_id = Column(Integer, ForeignKey("partidas.id"))
    
    partida = relationship("Partida", back_populates="estatisticas")