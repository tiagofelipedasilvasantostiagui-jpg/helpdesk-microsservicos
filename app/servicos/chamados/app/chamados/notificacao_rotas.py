from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencias import usuario_atual
from app.database import get_db
from app.chamados import notificacao_servico
from app.chamados.notificacao_esquema import NotificacaoSaida

router = APIRouter(prefix="/notificacoes", tags=["Notificações"])


@router.get("", response_model=list[NotificacaoSaida])
def minhas_notificacoes(
    usuario=Depends(usuario_atual),
    db: Session = Depends(get_db),
):
    return notificacao_servico.listar(db, usuario.id)
