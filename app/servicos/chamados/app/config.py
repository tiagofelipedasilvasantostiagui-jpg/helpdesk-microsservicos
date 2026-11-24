import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./chamados.db"
)

JWT_SEGREDO = os.getenv("JWT_SEGREDO", "")
JWT_ALGORITMO = "HS256"
JWT_EMISSOR = os.getenv("JWT_EMISSOR", "helpdesk-ti")

USUARIOS_URL = os.getenv(
    "USUARIOS_URL",
    "http://usuarios:8000"
)

INVENTARIO_URL = os.getenv(
    "INVENTARIO_URL",
    "http://inventario:8000"
)

HTTP_TIMEOUT = float(
    os.getenv("HTTP_TIMEOUT", "3")
)

DOCS_ATIVA = os.getenv("DOCS", "1") == "1"

if len(JWT_SEGREDO) < 32:
    raise RuntimeError("JWT_SEGREDO precisa ter pelo menos 32 caracteres.")