import logging
from pathlib import Path
from typing import Callable, Any

from modelo.cliente import Cliente
from modelo.servicio import Servicio
from modelo.reserva import Reserva
from excepciones.errores import (
    ErrorSistemaFJ,
    ValidacionDatosError,
    ServicioNoDisponibleError,
    OperacionReservaError,
    CalculoInconsistenteError,
)


# Apunta siempre a fase4programa/logs/sistema_fj.log sin importar desde dónde se ejecute.
BASE_PROYECTO = Path(__file__).resolve().parent.parent


def crear_logger(ruta: str | Path | None = None) -> logging.Logger:
    archivo_log = Path(ruta) if ruta is not None else (BASE_PROYECTO / "logs" / "sistema_fj.log")
    if not archivo_log.is_absolute():
        archivo_log = BASE_PROYECTO / archivo_log
    archivo_log.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        fh = logging.FileHandler(archivo_log, mode="a", encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(fh)
    return logger


# Gestiona clientes, servicios y reservas en memoria y registra eventos y errores en el log.
class GestorSistemaFJ:
    def __init__(self, ruta_log: str | Path | None = None) -> None:
        self.logger = crear_logger(ruta_log)
        self._clientes: dict[str, Cliente] = {}
        self._servicios: dict[str, Servicio] = {}
        self._reservas: dict[str, Reserva] = {}

    def agregar_cliente(self, cliente: Cliente | None) -> str:
        if cliente is None:
            raise ValidacionDatosError("Falta el objeto Cliente (parámetro obligatorio).")
        if cliente.id in self._clientes:
            raise OperacionReservaError(f"Ya existe un cliente con ID '{cliente.id}'.")
        self._clientes[cliente.id] = cliente
        return cliente.describir()

    def buscar_cliente(self, id_cliente: str) -> Cliente:
        if not id_cliente or id_cliente.strip().upper() not in self._clientes:
            raise ValidacionDatosError(f"Cliente '{id_cliente}' no encontrado.")
        return self._clientes[id_cliente.strip().upper()]

    def agregar_servicio(self, servicio: Servicio | None) -> str:
        if servicio is None:
            raise ValidacionDatosError("Falta el objeto Servicio (parámetro obligatorio).")
        if servicio.id in self._servicios:
            raise OperacionReservaError(f"Ya existe un servicio con ID '{servicio.id}'.")
        self._servicios[servicio.id] = servicio
        return servicio.describir()

    def buscar_servicio(self, id_servicio: str) -> Servicio:
        if not id_servicio or id_servicio.strip().upper() not in self._servicios:
            raise ServicioNoDisponibleError(f"El servicio '{id_servicio}' no existe.")
        servicio = self._servicios[id_servicio.strip().upper()]
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no está disponible.")
        return servicio

    def crear_reserva(
        self,
        id_reserva: str,
        id_cliente: str,
        id_servicio: str,
        horas: int,
        **kwargs: Any,
    ) -> str:
        clave_reserva = id_reserva.strip().upper() if isinstance(id_reserva, str) else ""
        if clave_reserva in self._reservas:
            raise OperacionReservaError(f"Ya existe una reserva con ID '{clave_reserva}'.")

        cliente = self.buscar_cliente(id_cliente)
        if not cliente.activo:
            raise OperacionReservaError(f"El cliente '{cliente.nombre}' está inactivo.")

        servicio = self.buscar_servicio(id_servicio)

        try:
            reserva = Reserva(
                id_reserva=id_reserva,
                cliente=cliente,
                servicio=servicio,
                horas=horas,
                **kwargs,
            )
        except (ValidacionDatosError, CalculoInconsistenteError, OperacionReservaError) as exc:
            raise OperacionReservaError("Error en parámetros de la reserva.") from exc

        self._reservas[reserva.id] = reserva
        return reserva.describir()

    def buscar_reserva(self, id_reserva: str) -> Reserva:
        if not id_reserva or id_reserva.strip().upper() not in self._reservas:
            raise OperacionReservaError(f"Reserva '{id_reserva}' no encontrada.")
        return self._reservas[id_reserva.strip().upper()]

    # Ejecuta una operación mostrando resultado en consola y registrando el evento en el log.
    def correr_op(self, numero: int, etiqueta: str, accion: Callable[[], Any]) -> Any:
        self.logger.info(f"Op {numero} [{etiqueta}] -> Inicio")
        resultado = None
        try:
            resultado = accion()
        except ErrorSistemaFJ as exc:
            causa = f" (Causa: {exc.__cause__})" if exc.__cause__ else ""
            mensaje = f"[{exc.codigo}] {exc}{causa}"
            print(f"[ERROR] Op {numero} - {etiqueta}: {mensaje}")
            self.logger.error(f"Op {numero} [{etiqueta}] -> {mensaje}")
        except Exception as exc:
            mensaje = f"Error inesperado: {exc}"
            print(f"[ERROR] Op {numero} - {etiqueta}: {mensaje}")
            self.logger.error(f"Op {numero} [{etiqueta}] -> {mensaje}")
        else:
            print(f"[OK] Op {numero} - {etiqueta}: {resultado}")
            self.logger.info(f"Op {numero} [{etiqueta}] -> OK: {resultado}")
        finally:
            self.logger.info(f"Fin Op {numero} [{etiqueta}]")
        return resultado

    def listar_resumen(self) -> None:
        print("\n--- Clientes ---")
        for c in self._clientes.values():
            print(" ", c.describir())
        print("\n--- Servicios ---")
        for s in self._servicios.values():
            print(" ", s.describir())
        print("\n--- Reservas ---")
        for r in self._reservas.values():
            print(" ", r.describir())