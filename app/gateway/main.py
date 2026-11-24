import os
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, Response

WEB = Path(__file__).resolve().parent.parent / "web"

USUARIOS_URL = os.getenv("USUARIOS_URL", "http://usuarios:8000")
INVENTARIO_URL = os.getenv("INVENTARIO_URL", "http://inventario:8000")
CHAMADOS_URL = os.getenv("CHAMADOS_URL", "http://chamados:8000")
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "5"))

ROTAS = {
    "/auth": USUARIOS_URL,
    "/usuarios": USUARIOS_URL,
    "/ativos": INVENTARIO_URL,
    "/chamados": CHAMADOS_URL,
    "/notificacoes": CHAMADOS_URL,
}


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    app.state.cliente = httpx.AsyncClient(
        timeout=httpx.Timeout(HTTP_TIMEOUT)
    )
    yield
    await app.state.cliente.aclose()


app = FastAPI(
    title="HelpDesk TI - API Gateway",
    version="3.0.0",
    lifespan=ciclo_de_vida,
)


@app.get("/saude", tags=["Saúde"])
async def saude():
    resultados = {}
    for nome, url in (
        ("usuarios", USUARIOS_URL),
        ("inventario", INVENTARIO_URL),
        ("chamados", CHAMADOS_URL),
    ):
        try:
            resposta = await app.state.cliente.get(f"{url}/saude")
            resultados[nome] = "ok" if resposta.is_success else "indisponivel"
        except httpx.HTTPError:
            resultados[nome] = "indisponivel"

    saudavel = all(status == "ok" for status in resultados.values())
    return JSONResponse(
        status_code=200 if saudavel else 503,
        content={"status": "ok" if saudavel else "degradado", "servicos": resultados},
    )


@app.get("/", include_in_schema=False)
async def tela_inicial():
    return FileResponse(WEB / "index.html")


@app.get("/app.js", include_in_schema=False)
async def script():
    return FileResponse(WEB / "app.js", media_type="text/javascript")


@app.get("/estilo.css", include_in_schema=False)
async def estilo():
    return FileResponse(WEB / "estilo.css", media_type="text/css")


@app.api_route(
    "/{caminho:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
)
async def encaminhar(caminho: str, request: Request):
    caminho_completo = "/" + caminho

    destino = None
    for prefixo, url in ROTAS.items():
        if caminho_completo == prefixo or caminho_completo.startswith(prefixo + "/"):
            destino = url
            break

    if destino is None:
        return JSONResponse(
            status_code=404,
            content={"detail": "Rota não encontrada no Gateway."},
        )

    url_final = destino + caminho_completo
    if request.url.query:
        url_final += "?" + request.url.query

    cabecalhos = dict(request.headers)
    cabecalhos.pop("host", None)

    corpo = await request.body()

    try:
        resposta = await app.state.cliente.request(
            method=request.method,
            url=url_final,
            headers=cabecalhos,
            content=corpo,
        )
    except (httpx.TimeoutException, httpx.RequestError):
        return JSONResponse(
            status_code=503,
            content={"detail": "Serviço temporariamente indisponível."},
        )

    cabecalhos_resposta = {
        chave: valor
        for chave, valor in resposta.headers.items()
        if chave.lower() not in (
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection",
        )
    }

    return Response(
        content=resposta.content,
        status_code=resposta.status_code,
        headers=cabecalhos_resposta,
    )
