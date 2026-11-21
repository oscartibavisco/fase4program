# Jerarquía de excepciones del dominio para el Software.
class ErrorSistemaFJ(Exception):
    codigo = "ERR-SYS"

    def __init__(self, mensaje: str, codigo: str | None = None) -> None:
        super().__init__(mensaje)
        if codigo:
            self.codigo = codigo


class ValidacionDatosError(ErrorSistemaFJ):
    codigo = "ERR-VAL"


class ServicioNoDisponibleError(ErrorSistemaFJ):
    codigo = "ERR-SRV"


class OperacionReservaError(ErrorSistemaFJ):
    codigo = "ERR-RES"


class CalculoInconsistenteError(ErrorSistemaFJ):
    codigo = "ERR-CAL"