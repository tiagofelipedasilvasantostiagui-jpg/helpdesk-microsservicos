cat > app/servicos/chamados/app/chamados/servico.py <<'PY'
from collections import Counter
from datetime import datetime, timedelta

import httpx

from app.config import HTTP_TIMEOUT, INVENTARIO_URL, USUARIOS_URL
from app.chamados import repositorio, notificacao_servico
from app.chamados.modelos import Chamado, Comentario
from app.erros import NaoEncontrado, RegraDeNegocio, SemPermissao


HORAS_SLA = {
    "critica": 4,
    "alta": 8,
    "media": 24,
    "baixa": 72,
}

TRANSICOES = {
    "aberto": {"em_atendimento"},
    "em_atendimento": {"resolvido"},
    "resolvido": {"fechado", "em_atendimento"},
    "fechado": set(),
}

EQUIPE = ("tecnico", "admin")


def eh_equipe(usuario):
    return usuario.perfil in EQUIPE


def calcular_prazo(prioridade, inicio):
    return inicio + timedelta(hours=HORAS_SLA[prioridade])


def consultar_servico(url, token):
    try:
        resposta = httpx.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=HTTP_TIMEOUT,
        )

        if resposta.status_code == 404:
            raise NaoEncontrado("O recurso informado não foi encontrado.")

        if resposta.status_code == 401:
            raise RegraDeNegocio(
                "O serviço remoto rejeitou a autenticação."
            )

        resposta.raise_for_status()
        return resposta.json()

    except httpx.TimeoutException as erro:
        raise ConnectionError(
            "O serviço consultado demorou demais para responder."
        ) from erro

    except httpx.RequestError as erro:
        raise ConnectionError(
            "Não foi possível conectar ao serviço consultado."
        ) from erro

    except httpx.HTTPStatusError as erro:
        raise ConnectionError(
            "O serviço consultado apresentou uma falha."
        ) from erro


def validar_ativo(ativo_id, token):
    return consultar_servico(
        f"{INVENTARIO_URL}/ativos/{ativo_id}",
        token,
    )


def validar_tecnico(tecnico_id, token):
    tecnico = consultar_servico(
        f"{USUARIOS_URL}/usuarios/{tecnico_id}",
        token,
    )

    if tecnico.get("perfil") != "tecnico":
        raise RegraDeNegocio(
            f"Usuário {tecnico_id} não é técnico."
        )

    return tecnico


def abrir(db, dados, usuario):
    if dados.ativo_id is not None:
        validar_ativo(dados.ativo_id, usuario.token)

    agora = datetime.now()

    chamado = Chamado(
        **dados.model_dump(),
        solicitante_id=usuario.id,
        status="aberto",
        criado_em=agora,
        prazo_sla=calcular_prazo(dados.prioridade, agora),
    )

    chamado = repositorio.salvar(db, chamado)

    notificacao_servico.notificar(
        db,
        "ChamadoAberto",
        usuario.id,
        f"Seu chamado #{chamado.id} foi aberto. Prazo: "
        f"{chamado.prazo_sla:%d/%m %H:%M}.",
    )

    return chamado


def obter(db, chamado_id, usuario):
    chamado = repositorio.buscar_por_id(db, chamado_id)

    if chamado is None or not (
        eh_equipe(usuario) or chamado.solicitante_id == usuario.id
    ):
        raise NaoEncontrado(
            f"Chamado {chamado_id} não encontrado."
        )

    return chamado


def listar(db, usuario, status=None, tecnico_id=None):
    solicitante_id = None if eh_equipe(usuario) else usuario.id

    return repositorio.listar(
        db,
        status,
        tecnico_id,
        solicitante_id,
    )


def atribuir(db, chamado_id, tecnico_id, usuario):
    if not eh_equipe(usuario):
        raise SemPermissao(
            "Só técnicos e administradores atribuem chamados."
        )

    chamado = obter(db, chamado_id, usuario)

    if chamado.status in ("resolvido", "fechado"):
        raise RegraDeNegocio(
            "Não é possível atribuir um chamado resolvido ou fechado."
        )

    tecnico = validar_tecnico(tecnico_id, usuario.token)

    chamado.tecnico_id = tecnico["id"]

    if chamado.status == "aberto":
        chamado.status = "em_atendimento"

    chamado = repositorio.salvar(db, chamado)

    notificacao_servico.notificar(
        db,
        "ChamadoAtribuido",
        tecnico["id"],
        f"O chamado #{chamado.id} foi atribuído a você.",
    )

    return chamado


def mudar_status(db, chamado_id, novo_status, usuario):
    chamado = obter(db, chamado_id, usuario)

    pode_solicitante = (
        chamado.status == "resolvido"
        and novo_status in ("fechado", "em_atendimento")
    )

    if not (eh_equipe(usuario) or pode_solicitante):
        raise SemPermissao(
            "Você não pode mudar o status deste chamado."
        )

    if novo_status not in TRANSICOES[chamado.status]:
        raise RegraDeNegocio(
            f"Não é possível ir de '{chamado.status}' para '{novo_status}'."
        )

    if novo_status == "em_atendimento" and chamado.tecnico_id is None:
        raise RegraDeNegocio(
            "Atribua um técnico antes de iniciar o atendimento."
        )

    chamado.status = novo_status
    chamado = repositorio.salvar(db, chamado)

    if novo_status == "resolvido":
        notificacao_servico.notificar(
            db,
            "ChamadoResolvido",
            chamado.solicitante_id,
            f"Seu chamado #{chamado.id} foi resolvido. "
            "Confirme se está tudo certo.",
        )

    return chamado


def comentar(db, chamado_id, dados, usuario):
    chamado = obter(db, chamado_id, usuario)

    if chamado.status == "fechado":
        raise RegraDeNegocio(
            "Chamados fechados não recebem comentários."
        )

    comentario = Comentario(
        chamado_id=chamado.id,
        autor_id=usuario.id,
        texto=dados.texto,
        criado_em=datetime.now(),
    )

    return repositorio.salvar_comentario(db, comentario)


def painel(db, usuario):
    chamados = listar(db, usuario)
    agora = datetime.now()

    atrasados = sum(
        1 for chamado in chamados
        if chamado.status in ("aberto", "em_atendimento")
        and chamado.prazo_sla < agora
    )

    return {
        "total": len(chamados),
        "por_status": dict(
            Counter(c.status for c in chamados)
        ),
        "atrasados": atrasados,
    }
PY