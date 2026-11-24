"""Validação dos tokens JWT no microsserviço de inventário."""
from dataclasses import dataclass
import jwt

from app.config import JWT_ALGORITMO, JWT_EMISSOR, JWT_SEGREDO


class TokenInvalido(Exception):
    pass


@dataclass
class DadosToken:
    id: int
    perfil: str


def ler_dados(token: str) -> DadosToken:
    try:
        dados = jwt.decode(
            token,
            JWT_SEGREDO,
            algorithms=[JWT_ALGORITMO],
            issuer=JWT_EMISSOR,
            options={"require": ["exp", "iat", "sub", "iss"]},
        )
        usuario_id = int(dados["sub"])
        perfil = str(dados["perfil"])
        if not perfil:
            raise TokenInvalido()
        return DadosToken(id=usuario_id, perfil=perfil)
    except (jwt.PyJWTError, ValueError, KeyError) as erro:
        raise TokenInvalido() from erro