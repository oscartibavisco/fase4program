from modelo.base import EntidadBase
from modelo.cliente import Cliente
from modelo.servicio import Servicio
from excepciones.errores import ValidacionDatosError, OperacionReservaError, CalculoInconsistenteError


class EstadoReserva:
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    PROCESADA = "PROCESADA"


# Integra cliente, servicio, duración y estado con control de transiciones y costos.
class Reserva(EntidadBase):
    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        horas: int,
        impuesto: float = 0.19,
        descuento: float = 0.0,
        ajuste_tarifa: float | str = 0.0,
        **kwargs,
    ) -> None:
        try:
            super().__init__(id_reserva)
        except ValueError as exc:
            raise ValidacionDatosError("ID de reserva inválido.") from exc

        if not isinstance(cliente, Cliente):
            raise ValidacionDatosError("El cliente de la reserva no es válido.")
        if not isinstance(servicio, Servicio):
            raise ValidacionDatosError("El servicio de la reserva no es válido.")
        if not servicio.disponible:
            raise OperacionReservaError(f"El servicio '{servicio.nombre}' no está disponible.")

        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas
        self._extras = dict(kwargs)
        self._estado = EstadoReserva.PENDIENTE
        self._motivo_cancelacion: str | None = None
        self._total = self.recalcular_total(
            horas=horas,
            impuesto=impuesto,
            descuento=descuento,
            ajuste_tarifa=ajuste_tarifa,
        )

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def horas(self) -> int:
        return self._horas

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def total(self) -> float:
        return self._total

    def recalcular_total(
        self,
        horas: int | None = None,
        impuesto: float = 0.19,
        descuento: float = 0.0,
        ajuste_tarifa: float | str = 0.0,
    ) -> float:
        horas_eval = self._horas if horas is None else horas
        try:
            total = self._servicio.calcular_costo(
                horas=horas_eval,
                impuesto=impuesto,
                descuento=descuento,
                ajuste_tarifa=ajuste_tarifa,
                **self._extras,
            )
        except (ValidacionDatosError, CalculoInconsistenteError) as exc:
            raise CalculoInconsistenteError(f"No se pudo calcular el costo de la reserva {self.id}.") from exc

        if horas is not None:
            self._horas = horas
        self._total = total
        return total

    def confirmar(self) -> str:
        if self._estado == EstadoReserva.CANCELADA:
            raise OperacionReservaError(f"No se puede confirmar [{self.id}] porque está CANCELADA.")
        if self._estado == EstadoReserva.PROCESADA:
            raise OperacionReservaError(f"La reserva [{self.id}] ya fue PROCESADA.")
        if not self._servicio.disponible:
            raise OperacionReservaError(f"El servicio '{self._servicio.nombre}' no está disponible.")

        self._estado = EstadoReserva.CONFIRMADA
        return f"Reserva [{self.id}] CONFIRMADA (${self._total:,.2f})"

    def cancelar(self, motivo: str = "Cancelada por el usuario") -> str:
        if self._estado == EstadoReserva.PROCESADA:
            raise OperacionReservaError(f"No se puede cancelar [{self.id}] en estado PROCESADA.")
        if self._estado == EstadoReserva.CANCELADA:
            raise OperacionReservaError(f"La reserva [{self.id}] ya está CANCELADA.")

        self._estado = EstadoReserva.CANCELADA
        self._motivo_cancelacion = motivo.strip() if motivo and motivo.strip() else "Sin motivo especificado"
        return f"Reserva [{self.id}] CANCELADA - {self._motivo_cancelacion}"

    def procesar(self) -> str:
        if self._estado != EstadoReserva.CONFIRMADA:
            raise OperacionReservaError(
                f"Solo se pueden procesar reservas CONFIRMADAS; [{self.id}] está en {self._estado}."
            )
        self._estado = EstadoReserva.PROCESADA
        return f"Reserva [{self.id}] PROCESADA (${self._total:,.2f})"

    def describir(self) -> str:
        return (
            f"Reserva [{self.id}] | {self._cliente.nombre} | {self._servicio.nombre} | "
            f"{self._horas}h | ${self._total:,.2f} | {self._estado}"
        )