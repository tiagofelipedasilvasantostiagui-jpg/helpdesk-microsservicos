from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import DOCS_ATIVA
from app.database import Base, engine
from app.chamados import modelos, notificacao_modelo
from app.chamados.rotas import router as chamados_router
from app.chamados.notificacao_rotas import router as notificacoes_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="HelpDesk TI - Serviço de Chamados",
    description="Microsserviço responsável pelo gerenciamento de chamados.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if DOCS_ATIVA else None,
    redoc_url=None,
)


@app.get("/saude", tags=["Saúde"])
def saude():
    return {
        "servico": "chamados",
        "status": "ok",
    }


app.include_router(chamados_router)
app.include_router(notificacoes_router)
