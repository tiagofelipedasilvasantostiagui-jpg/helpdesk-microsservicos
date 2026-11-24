import time

from collections import defaultdict
from threading import Lock

from app.config import (
    LOGIN_JANELA_SEGUNDOS,
    LOGIN_MAX_FALHAS,
)

_falhas = defaultdict(list)
_trava = Lock()


def _recentes(chave, agora):
    _falhas[chave] = [
        t for t in _falhas[chave]
        if agora - t < LOGIN_JANELA_SEGUNDOS
    ]

    return _falhas[chave]


def bloqueado(chave):
    with _trava:
        return len(
            _recentes(chave, time.monotonic())
        ) >= LOGIN_MAX_FALHAS


def registrar_falha(chave):
    with _trava:
        agora = time.monotonic()
        _recentes(chave, agora).append(agora)


def limpar(chave):
    with _trava:
        _falhas.pop(chave, None)