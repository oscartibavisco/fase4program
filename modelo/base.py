from abc import ABC, abstractmethod


# Clase base abstracta para entidades con identificador único.
class EntidadBase(ABC):
    def __init__(self, id_entidad: str) -> None:
        if not isinstance(id_entidad, str) or not id_entidad.strip():
            raise ValueError("El identificador no puede estar vacío.")
        self._id = id_entidad.strip().upper()

    @property
    def id(self) -> str:
        return self._id

    @abstractmethod
    def describir(self) -> str:
        pass