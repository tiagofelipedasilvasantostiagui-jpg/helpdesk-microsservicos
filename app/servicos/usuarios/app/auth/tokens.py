from datetime import datetime, timedelta, timezone

import jwt

from app.config import (
    JWT_ALGORITMO,
    JWT_EMISSOR,
    JWT_SEGREDO,
    TOKEN_MINUTOS,
)


class TokenInvalido(Exception):
    pass


def criar(usuario_id: int, perfil: str):
    agora = datetime.now(timezone.utc)

    expira = agora + timedelta(minutes=TOKEN_MINUTOS)

    dados = {
        "sub": str(usuario_id),
        "perfil": perfil,
        "iat": agora,
        "exp": expira,
        "iss": JWT_EMISSOR,
    }

    token = jwt.encode(
        dados,
        JWT_SEGREDO,
        algorithm=JWT_ALGORITMO,
    )

    return token, expira


def ler(token: str):
    try:
        dados = jwt.decode(
            token,
            JWT_SEGREDO,
            algorithms=[JWT_ALGORITMO],
            issuer=JWT_EMISSOR,
            options={
                "require": ["exp", "iat", "sub", "iss", "perfil"]
            },
        )

        return {
            "id": int(dados["sub"]),
            "perfil": str(dados["perfil"]),
        }

    except (jwt.PyJWTError, ValueError, KeyError) as erro:
        raise TokenInvalido() from erro