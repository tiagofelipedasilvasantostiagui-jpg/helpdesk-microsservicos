from app.auth import senhas
from app.usuarios import repositorio
from app.usuarios.esquemas import UsuarioCriar
from app.usuarios.modelos import Usuario


class RegraDeNegocio(Exception):
    pass


class NaoEncontrado(Exception):
    pass


def criar(db, dados: UsuarioCriar):
    email = dados.email.lower()

    if repositorio.buscar_por_email(db, email):
        raise RegraDeNegocio(
            "Já existe um usuário com este e-mail."
        )

    usuario = Usuario(
        nome=dados.nome,
        email=email,
        perfil=dados.perfil,
        senha_hash=senhas.gerar_hash(dados.senha),
    )

    return repositorio.salvar(db, usuario)


def buscar_por_email(db, email):
    return repositorio.buscar_por_email(
        db,
        email.lower(),
    )


def obter(db, usuario_id):
    usuario = repositorio.buscar_por_id(
        db,
        usuario_id,
    )

    if usuario is None:
        raise NaoEncontrado(
            f"Usuário {usuario_id} não encontrado."
        )

    return usuario


def obter_tecnico(db, usuario_id):
    usuario = obter(db, usuario_id)

    if usuario.perfil != "tecnico":
        raise RegraDeNegocio(
            f"Usuário {usuario_id} não é técnico."
        )

    return usuario


def listar(db, perfil=None):
    return repositorio.listar(db, perfil)