from fastapi import FastAPI, Depends, HTTPException, status, Response 
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from fpdf import FPDF 
import random
from . import models, security, schemas
from .database import get_db, engine
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Gestor de Pelada API",
    description="API para gerenciar suas peladas de futebol.",
    version="1.0.0")


@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao Gestor de Pelada"}

@app.post("/usuarios/", response_model=schemas.Usuario)
def create_user(user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.Usuario).filter(models.Usuario.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email já registrado")
    
    hashed_password = security.get_password_hash(user.password)
    db_user = models.Usuario(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/peladas/", response_model=schemas.Pelada)
def create_pelada_for_user(
    pelada: schemas.PeladaCreate, 
    db: Session = Depends(get_db), 
    current_user: models.Usuario = Depends(security.get_current_user)):
    db_pelada = models.Pelada(**pelada.model_dump(), dono_id=current_user.id)
    db.add(db_pelada)
    db.commit()
    db.refresh(db_pelada)
    return db_pelada

@app.get("/peladas/", response_model=List[schemas.Pelada])
def read_peladas_for_user(
    db: Session = Depends(get_db), 
    current_user: models.Usuario = Depends(security.get_current_user)):
    peladas = db.query(models.Pelada).filter(models.Pelada.dono_id == current_user.id).all()
    return peladas

def get_pelada_and_check_permission(pelada_id: int, db: Session, current_user: models.Usuario):
    """Função auxiliar para verificar se a pelada existe e se o usuário tem permissão."""
    db_pelada = db.query(models.Pelada).filter(models.Pelada.id == pelada_id).first()
    if db_pelada is None:
        raise HTTPException(status_code=404, detail="Pelada não encontrada")
    if db_pelada.dono_id != current_user.id:
        raise HTTPException(status_code=403, detail="Não autorizado a acessar esta pelada")
    return db_pelada

@app.post("/peladas/{pelada_id}/jogadores/", response_model=schemas.Jogador)
def create_jogador_for_pelada(
    pelada_id: int, 
    jogador: schemas.JogadorCreate, 
    db: Session = Depends(get_db), 
    current_user: models.Usuario = Depends(security.get_current_user)):
    get_pelada_and_check_permission(pelada_id, db, current_user)
    db_jogador = models.Jogador(**jogador.model_dump(), pelada_id=pelada_id)
    db.add(db_jogador)
    db.commit()
    db.refresh(db_jogador)
    return db_jogador

@app.get("/peladas/{pelada_id}/jogadores/", response_model=List[schemas.Jogador])
def read_jogadores_from_pelada(
    pelada_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.Usuario = Depends(security.get_current_user)):
    get_pelada_and_check_permission(pelada_id, db, current_user)
    jogadores = db.query(models.Jogador).filter(models.Jogador.pelada_id == pelada_id).all()
    return jogadores

@app.get("/peladas/{pelada_id}/jogadores/{jogador_id}", response_model=schemas.Jogador)
def read_jogador_from_pelada(
    pelada_id: int,
    jogador_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)):
    get_pelada_and_check_permission(pelada_id, db, current_user)
    db_jogador = db.query(models.Jogador).filter(models.Jogador.id == jogador_id, models.Jogador.pelada_id == pelada_id).first()
    if db_jogador is None:
        raise HTTPException(status_code=404, detail="Jogador não encontrado nesta pelada")
    return db_jogador

@app.put("/peladas/{pelada_id}/jogadores/{jogador_id}", response_model=schemas.Jogador)
def update_jogador_in_pelada(
    pelada_id: int,
    jogador_id: int,
    jogador_update: schemas.JogadorCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)):
    get_pelada_and_check_permission(pelada_id, db, current_user)
    db_jogador = db.query(models.Jogador).filter(models.Jogador.id == jogador_id, models.Jogador.pelada_id == pelada_id).first()
    if db_jogador is None:
        raise HTTPException(status_code=404, detail="Jogador não encontrado nesta pelada")
    
    db_jogador.nome = jogador_update.nome
    db_jogador.posicao = jogador_update.posicao
    db_jogador.nota = jogador_update.nota
    
    db.commit()
    db.refresh(db_jogador)
    return db_jogador

@app.delete("/peladas/{pelada_id}/jogadores/{jogador_id}", response_model=dict)
def delete_jogador_in_pelada(
    pelada_id: int,
    jogador_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)):

    get_pelada_and_check_permission(pelada_id, db, current_user)
    db_jogador = db.query(models.Jogador).filter(models.Jogador.id == jogador_id, models.Jogador.pelada_id == pelada_id).first()
    if db_jogador is None:
        raise HTTPException(status_code=404, detail="Jogador não encontrado nesta pelada")
        
    db.delete(db_jogador)
    db.commit()
    return {"detail": "Jogador excluído com sucesso"}

@app.post("/peladas/{pelada_id}/sorteio-times/", response_model=schemas.SorteioResponse)
def sortear_times_in_pelada(
    pelada_id: int,
    request: schemas.SorteioRequest, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)):
    get_pelada_and_check_permission(pelada_id, db, current_user)
    ids_dos_jogadores = request.jogadores_ids
    
    if len(ids_dos_jogadores) != 20:
        raise HTTPException(status_code=400, detail="O sorteio requer exatamente 20 jogadores.")

    jogadores_para_sorteio = db.query(models.Jogador).filter(models.Jogador.pelada_id == pelada_id, models.Jogador.id.in_(ids_dos_jogadores)).all()
    
    if len(jogadores_para_sorteio) != 20:
        raise HTTPException(status_code=404, detail="Um ou mais IDs de jogadores não foram encontrados nesta pelada.")
        
    jogadores_por_nota = {}
    for j in jogadores_para_sorteio:
        if j.nota not in jogadores_por_nota:
            jogadores_por_nota[j.nota] = []
        jogadores_por_nota[j.nota].append(j)
    
    for nota in jogadores_por_nota:
        random.shuffle(jogadores_por_nota[nota])

    jogadores_ordenados = []
    for nota in sorted(jogadores_por_nota.keys(), reverse=True):
        jogadores_ordenados.extend(jogadores_por_nota[nota])

    times = {"time_A": [], "time_B": [], "time_C": [], "time_D": []}
    nomes_times = list(times.keys())
    
    for i, jogador in enumerate(jogadores_ordenados):
        rodada_par = (i // 4) % 2 == 0
        if rodada_par:
            indice_time = i % 4
        else:
            indice_time = 3 - (i % 4)
        
        times[nomes_times[indice_time]].append(jogador)
            
    return times

@app.post("/peladas/{pelada_id}/partidas/", response_model=schemas.Partida)
def registrar_partida(
    pelada_id: int,
    partida_data: schemas.PartidaCreate, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)):
  
    db_pelada = get_pelada_and_check_permission(pelada_id, db, current_user)
    
    if len(db_pelada.partidas) >= 4:
        raise HTTPException(status_code=400, detail="Esta pelada já atingiu o limite de 4 jogos.")
    
    nova_partida = models.Partida(data=partida_data.data, pelada_id=pelada_id)
    db.add(nova_partida)
    db.commit()
    db.refresh(nova_partida)

    for est in partida_data.estatisticas:
        nova_estatistica = models.EstatisticaPartida(
            partida_id=nova_partida.id,
            jogador_id=est.jogador_id,
            gols=est.gols,
            assistencias=est.assistencias
        )
        db.add(nova_estatistica)
    
    db.commit()
    db.refresh(nova_partida) 
    return nova_partida

@app.get("/peladas/{pelada_id}/ranking/", response_model=List[schemas.JogadorRanking])
def get_ranking_da_pelada(
    pelada_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)):
    
    get_pelada_and_check_permission(pelada_id, db, current_user)

    resultado = (
        db.query(
            models.Jogador.id.label("jogador_id"),
            models.Jogador.nome.label("nome"),
            func.sum(models.EstatisticaPartida.gols).label("total_gols"),
            func.sum(models.EstatisticaPartida.assistencias).label("total_assistencias")
        )
        .join(models.EstatisticaPartida, models.Jogador.id == models.EstatisticaPartida.jogador_id)
        .filter(models.Jogador.pelada_id == pelada_id)
        .group_by(models.Jogador.id, models.Jogador.nome)
        .order_by(
            func.sum(models.EstatisticaPartida.gols).desc(),
            func.sum(models.EstatisticaPartida.assistencias).desc()
        )
        .all()
    )
    return resultado


@app.get("/peladas/{pelada_id}/ranking/pdf", response_class=Response)
def get_ranking_pdf(
    pelada_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)):
    
    db_pelada = get_pelada_and_check_permission(pelada_id, db, current_user)
    
    ranking_data = (
        db.query(
            models.Jogador.id,
            models.Jogador.nome,
            func.sum(models.EstatisticaPartida.gols).label("total_gols"),
            func.sum(models.EstatisticaPartida.assistencias).label("total_assistencias")
        )
        .join(models.EstatisticaPartida, models.Jogador.id == models.EstatisticaPartida.jogador_id)
        .filter(models.Jogador.pelada_id == pelada_id)
        .group_by(models.Jogador.id, models.Jogador.nome)
        .order_by(
            func.sum(models.EstatisticaPartida.gols).desc(),
            func.sum(models.EstatisticaPartida.assistencias).desc()
        )
        .all()
    )

  
    pdf = FPDF()
    pdf.add_page()
    
   
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Ranking da Pelada: {db_pelada.nome}", ln=True, align="C")
    pdf.ln(10)

    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(20, 10, "Pos", 1, 0, "C")
    pdf.cell(100, 10, "Nome", 1, 0, "C")
    pdf.cell(30, 10, "Gols", 1, 0, "C")
    pdf.cell(30, 10, "Assist.", 1, 1, "C")

    pdf.set_font("Arial", "", 12)
    for i, jogador in enumerate(ranking_data):
        pdf.cell(20, 10, str(i + 1), 1, 0, "C")
        pdf.cell(100, 10, jogador.nome, 1, 0, "L")
        pdf.cell(30, 10, str(jogador.total_gols), 1, 0, "C")
        pdf.cell(30, 10, str(jogador.total_assistencias), 1, 1, "C")
        
    pdf_output = pdf.output(dest='S')
    
    return Response(content=bytes(pdf_output), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=ranking_{pelada_id}.pdf"})
