"""Exceções de domínio do microsserviço de inventário."""


class NaoEncontrado(Exception):
    pass


class RegraDeNegocio(Exception):
    pass