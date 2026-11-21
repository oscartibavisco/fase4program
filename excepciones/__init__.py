# Exporta las excepciones personalizadas del sistema.
from excepciones.errores import (
    ErrorSistemaFJ,
    ValidacionDatosError,
    ServicioNoDisponibleError,
    OperacionReservaError,
    CalculoInconsistenteError,
)

__all__ = [
    "ErrorSistemaFJ",
    "ValidacionDatosError",
    "ServicioNoDisponibleError",
    "OperacionReservaError",
    "CalculoInconsistenteError",
]