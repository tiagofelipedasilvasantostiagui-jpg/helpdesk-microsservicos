from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.chamados.notificacao_modelo import Notificacao


def notificar(db: Session, tipo: str, destinatario_id: int, mensagem: str):
    aviso = Notificacao(
        tipo=tipo,
        destinatario_id=destinatario_id,
        mensagem=mensagem,
        criada_em=datetime.now(),
    )
    db.add(aviso)
    db.commit()
    db.refresh(aviso)
    return aviso


def listar(db: Session, destinatario_id: int):
    consulta = (
        select(Notificacao)
        .where(Notificacao.destinatario_id == destinatario_id)
        .order_by(Notificacao.id)
    )
    return list(db.scalars(consulta))
