from sqlalchemy import select
from sqlalchemy.orm import Session

from app.chamados.modelos import Chamado, Comentario


def salvar(db: Session, chamado: Chamado):
    db.add(chamado)
    db.commit()
    db.refresh(chamado)
    return chamado


def salvar_comentario(db: Session, comentario: Comentario):
    db.add(comentario)
    db.commit()
    db.refresh(comentario)
    return comentario


def buscar_por_id(db: Session, chamado_id: int):
    return db.get(Chamado, chamado_id)


def listar(
    db: Session,
    status=None,
    tecnico_id=None,
    solicitante_id=None,
):
    consulta = select(Chamado).order_by(Chamado.id)

    if solicitante_id is not None:
        consulta = consulta.where(
            Chamado.solicitante_id == solicitante_id
        )

    if status:
        consulta = consulta.where(
            Chamado.status == status
        )

    if tecnico_id:
        consulta = consulta.where(
            Chamado.tecnico_id == tecnico_id
        )

    return list(db.scalars(consulta))