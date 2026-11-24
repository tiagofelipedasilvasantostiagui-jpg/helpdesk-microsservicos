"""Aplicação FastAPI do microsserviço de inventário."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import DOCS_ATIVA
from app.database import Base, engine
from app.erros import NaoEncontrado, RegraDeNegocio
from app.inventario import modelos as _modelos  # noqa: F401
from app.inventario.rotas import router as inventario_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="HelpDesk TI - Inventário",
    lifespan=lifespan,
    docs_url="/docs" if DOCS_ATIVA else None,
    redoc_url=None,
)


@app.exception_handler(NaoEncontrado)
async def tratar_nao_encontrado(_request: Request, erro: NaoEncontrado):
    return JSONResponse(status_code=404, content={"detail": str(erro)})


@app.exception_handler(RegraDeNegocio)
async def tratar_regra_de_negocio(_request: Request, erro: RegraDeNegocio):
    return JSONResponse(status_code=400, content={"detail": str(erro)})


@app.get("/saude")
def saude():
    return {"servico": "inventario", "status": "ok"}


app.include_router(inventario_router)