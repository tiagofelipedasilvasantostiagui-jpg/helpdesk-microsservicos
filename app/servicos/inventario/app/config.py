"""Configurações do microsserviço de inventário."""
import logging
import os
import secrets

log = logging.getLogger("helpdesk-inventario")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./inventario.db")

JWT_SEGREDO = os.getenv("JWT_SEGREDO") or ""
if len(JWT_SEGREDO) < 32:
    if JWT_SEGREDO:
        log.warning("JWT_SEGREDO tem menos de 32 caracteres; usando um segredo aleatório.")
    JWT_SEGREDO = secrets.token_urlsafe(48)

JWT_ALGORITMO = "HS256"
JWT_EMISSOR = "helpdesk-ti"
DOCS_ATIVA = os.getenv("DOCS", "1") == "1"