from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencias import usuario_atual
from app.database import get_db
from app.chamados import servico
from app.chamados.esquemas import (
    Atribuicao,
    ChamadoCriar,
    ChamadoSaida,
    ComentarioCriar,
    ComentarioSaida,
    MudancaStatus,
    Painel,
    Status,
)
from app.erros import (
    NaoEncontrado,
    RegraDeNegocio,
    SemPermissao,
)

router = APIRouter(
    prefix="/chamados",
    tags=["Chamados"],
)


def executar(operacao):
    try:
        return operacao()

    except NaoEncontrado as erro:
        raise HTTPException(
            status_code=404,
            detail=str(erro),
        )

    except SemPermissao as erro:
        raise HTTPException(
            status_code=403,
            detail=str(erro),
        )

    except RegraDeNegocio as erro:
        raise HTTPException(
            status_code=422,
            detail=str(erro),
        )

    except ConnectionError as erro:
        raise HTTPException(
            status_code=503,
            detail=str(erro),
        )


@router.post(
    "",
    response_model=ChamadoSaida,
    status_code=201,
)
def abrir_chamado(
    dados: ChamadoCriar,
    usuario=Depends(usuario_atual),
    db: Session = Depends(get_db),
):
    return executar(
        lambda: servico.abrir(db, dados, usuario)
    )


@router.get(
    "",
    response_model=list[ChamadoSaida],
)
def listar_chamados(
    status: Status | None = None,
    tecnico_id: int | None = None,
    usuario=Depends(usuario_atual),
    db: Session = Depends(get_db),
):
    return servico.listar(
        db,
        usuario,
        status,
        tecnico_id,
    )


@router.get(
    "/painel",
    response_model=Painel,
)
def painel(
    usuario=Depends(usuario_atual),
    db: Session = Depends(get_db),
):
    return servico.painel(db, usuario)


@router.get(
    "/{chamado_id}",
    response_model=ChamadoSaida,
)
def obter_chamado(
    chamado_id: int,
    usuario=Depends(usuario_atual),
    db: Session = Depends(get_db),
):
    return executar(
        lambda: servico.obter(
            db,
            chamado_id,
            usuario,
        )
    )


@router.patch(
    "/{chamado_id}/atribuir",
    response_model=ChamadoSaida,
)
def atribuir_chamado(
    chamado_id: int,
    dados: Atribuicao,
    usuario=Depends(usuario_atual),
    db: Session = Depends(get_db),
):
    return executar(
        lambda: servico.atribuir(
            db,
            chamado_id,
            dados.tecnico_id,
            usuario,
        )
    )


@router.patch(
    "/{chamado_id}/status",
    response_model=ChamadoSaida,
)
def mudar_status(
    chamado_id: int,
    dados: MudancaStatus,
    usuario=Depends(usuario_atual),
    db: Session = Depends(get_db),
):
    return executar(
        lambda: servico.mudar_status(
            db,
            chamado_id,
            dados.status,
            usuario,
        )
    )


@router.post(
    "/{chamado_id}/comentarios",
    response_model=ComentarioSaida,
    status_code=201,
)
def comentar(
    chamado_id: int,
    dados: ComentarioCriar,
    usuario=Depends(usuario_atual),
    db: Session = Depends(get_db),
):
    return executar(
        
        lambda: servico.comentar(
            db,
            chamado_id,
            dados,
            usuario,
        )
        
    )