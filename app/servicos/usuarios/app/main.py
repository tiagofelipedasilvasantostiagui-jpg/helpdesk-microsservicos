import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.config import DOCS_ATIVA
from app.database import Base, engine, SessionLocal
from app.auth import senhas
from app.auth.rotas import router as auth_router
from app.usuarios import modelos
from app.usuarios.modelos import Usuario
from app.usuarios.rotas import router as usuarios_router


def carregar_dados_exemplo():
    if os.getenv("DADOS_EXEMPLO", "1") != "1":
        return

    with SessionLocal() as db:
        if db.query(Usuario).first():
            return

        senha = os.getenv("SENHA_EXEMPLO", "Helpdesk2026")

        exemplos = [
            ("Admin TI", "admin@empresa.com", "admin"),
            ("Ana Souza", "ana@empresa.com", "solicitante"),
            ("Bruno Lima", "bruno@empresa.com", "solicitante"),
            ("Carla Dias", "carla@empresa.com", "tecnico"),
            ("Diego Rocha", "diego@empresa.com", "tecnico"),
        ]

        for nome, email, perfil in exemplos:
            usuario = Usuario(
                nome=nome,
                email=email,
                perfil=perfil,
                senha_hash=senhas.gerar_hash(senha),
                ativo=True,
            )
            db.add(usuario)

        db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    carregar_dados_exemplo()
    yield


app = FastAPI(
    title="HelpDesk TI - Serviço de Usuários",
    description="Microsserviço responsável por usuários e autenticação.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if DOCS_ATIVA else None,
    redoc_url=None,
)


@app.exception_handler(IntegrityError)
async def tratar_conflito(request: Request, erro: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={
            "detail": "O registro conflita com outro já existente."
        },
    )


@app.get("/saude", tags=["Saúde"])
def saude():
    return {
        "servico": "usuarios",
        "status": "ok",
    }


app.include_router(auth_router)
app.include_router(usuarios_router)