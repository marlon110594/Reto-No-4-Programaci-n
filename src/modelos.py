"""
Módulo de modelos del dominio para Software FJ.
Implementa:
- Abstracción (EntidadSistema, Servicio)
- Encapsulación (propiedades y atributos privados)
- Herencia y Polimorfismo (ReservaSala, AlquilerEquipo, AsesoriaEspecializada)
- Sobrecarga de métodos (calcular_costo y aplicar_ajuste)
- Encadenamiento de excepciones (raise ... from ...)
"""

from abc import ABC, abstractmethod
from functools import singledispatchmethod
import re

from src.excepciones import (
    DatoInvalidoError,
    ParametroFaltanteError,
    OperacionNoPermitidaError,
    ServicioNoDisponibleError,
    ReservaInvalidaError,
)


class EntidadSistema(ABC):
    """Clase abstracta base que representa cualquier entidad gestionable del sistema."""

    def __init__(self, id_entidad: str):
        if not id_entidad or not isinstance(id_entidad, str) or not id_entidad.strip():
            raise ParametroFaltanteError("El identificador de la entidad es obligatorio.")
        self._id = id_entidad.strip()

    @property
    def id(self) -> str:
        """Getter encapsulado del identificador único."""
        return self._id

    @abstractmethod
    def validar_integridad(self) -> bool:
        """Método abstracto obligatorio para verificar la validez interna del objeto."""
        pass

    @abstractmethod
    def obtener_resumen(self) -> str:
        """Método abstracto obligatorio para representar textualmente la entidad."""
        pass


class Cliente(EntidadSistema):
    """Representa un cliente de Software FJ con validaciones estrictas de datos personales."""

    def __init__(self, id_cliente: str, nombre: str, correo: str, telefono: str):
        super().__init__(id_cliente)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self._activo = True

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 3:
            raise DatoInvalidoError(
                f"El nombre '{valor}' es inválido. Debe tener al menos 3 caracteres."
            )
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        if not valor or not isinstance(valor, str):
            raise ParametroFaltanteError("El correo electrónico es obligatorio.")
        patron_email = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not re.match(patron_email, valor.strip()):
            raise DatoInvalidoError(f"Formato de correo electrónico inválido: '{valor}'.")
        self._correo = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        if not valor or not isinstance(valor, str):
            raise ParametroFaltanteError("El teléfono de contacto es obligatorio.")
        solo_digitos = re.sub(r"\D", "", valor)
        if len(solo_digitos) < 7 or len(solo_digitos) > 15:
            raise DatoInvalidoError(
                f"El teléfono '{valor}' debe contener entre 7 y 15 dígitos numéricos."
            )
        self._telefono = solo_digitos

    def validar_integridad(self) -> bool:
        return bool(self._id and self._nombre and self._correo and self._telefono)

    def obtener_resumen(self) -> str:
        return f"Cliente [{self.id}] {self.nombre} | Email: {self.correo} | Tel: {self.telefono}"


class Servicio(EntidadSistema, ABC):
    """Clase abstracta que modela los servicios ofertados por Software FJ."""

    def __init__(self, id_servicio: str, nombre: str, tarifa_base_hora: float, disponible: bool = True):
        super().__init__(id_servicio)
        if not nombre or not nombre.strip():
            raise ParametroFaltanteError("El nombre del servicio no puede estar vacío.")
        if not isinstance(tarifa_base_hora, (int, float)) or tarifa_base_hora <= 0:
            raise DatoInvalidoError(
                f"La tarifa base ({tarifa_base_hora}) debe ser un número positivo mayor a cero."
            )
        self._nombre = nombre.strip()
        self._tarifa_base_hora = float(tarifa_base_hora)
        self._disponible = bool(disponible)

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_base_hora(self) -> float:
        return self._tarifa_base_hora

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, estado: bool) -> None:
        self._disponible = bool(estado)

    @abstractmethod
    def validar_parametros(self, horas: int) -> None:
        """Valida restricciones particulares del servicio según las horas solicitadas."""
        pass

    @abstractmethod
    def describir_servicio(self) -> str:
        """Retorna descripción detallada polimórfica de cada tipo de servicio."""
        pass

    def calcular_costo(
        self,
        horas: int,
        descuento_porcentaje: float = 0.0,
        incluir_iva: bool = True,
        tasa_iva: float = 0.19,
    ) -> float:
        """Calcula el costo aplicando descuento opcional e IVA opcional."""
        self.validar_parametros(horas)
        if not (0 <= descuento_porcentaje <= 100):
            raise DatoInvalidoError("El porcentaje de descuento debe estar entre 0 y 100.")
        if tasa_iva < 0:
            raise DatoInvalidoError("La tasa de IVA no puede ser negativa.")

        subtotal = self._tarifa_base_hora * horas
        valor_descuento = subtotal * (descuento_porcentaje / 100.0)
        base_gravable = subtotal - valor_descuento
        total = base_gravable * (1 + tasa_iva) if incluir_iva else base_gravable
        return round(total, 2)

    def validar_integridad(self) -> bool:
        return self._tarifa_base_hora > 0 and bool(self._nombre)

    def obtener_resumen(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return f"Servicio [{self.id}] {self.nombre} (${self.tarifa_base_hora:,.2f}/h) - {estado}"


class ReservaSala(Servicio):
    """Servicio especializado: Reserva de salas tecnológicas y de reuniones."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base_hora: float,
        capacidad_personas: int,
        tiene_videoconferencia: bool = True,
        disponible: bool = True,
    ):
        super().__init__(id_servicio, nombre, tarifa_base_hora, disponible)
        if not isinstance(capacidad_personas, int) or capacidad_personas <= 0:
            raise DatoInvalidoError("La capacidad de la sala debe ser un entero positivo.")
        self.capacidad_personas = capacidad_personas
        self.tiene_videoconferencia = tiene_videoconferencia

    def validar_parametros(self, horas: int) -> None:
        if not isinstance(horas, int) or horas < 1 or horas > 12:
            raise DatoInvalidoError(
                f"Las reservas de sala deben ser entre 1 y 12 horas (recibido: {horas})."
            )

    def describir_servicio(self) -> str:
        equip = "con equipo de videoconferencia" if self.tiene_videoconferencia else "estándar"
        return f"Sala '{self.nombre}' (Capacidad: {self.capacidad_personas} personas, {equip})"


class AlquilerEquipo(Servicio):
    """Servicio especializado: Alquiler de hardware y estaciones de trabajo."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base_hora: float,
        categoria_hardware: str,
        deposito_garantia: float,
        disponible: bool = True,
    ):
        super().__init__(id_servicio, nombre, tarifa_base_hora, disponible)
        if not categoria_hardware or not categoria_hardware.strip():
            raise ParametroFaltanteError("La categoría de hardware es obligatoria.")
        if deposito_garantia < 0:
            raise DatoInvalidoError("El depósito de garantía no puede ser negativo.")
        self.categoria_hardware = categoria_hardware.strip()
        self.deposito_garantia = float(deposito_garantia)

    def validar_parametros(self, horas: int) -> None:
        if not isinstance(horas, int) or horas < 2:
            raise DatoInvalidoError(
                f"El alquiler de equipos requiere mínimo 2 horas (recibido: {horas})."
            )

    def calcular_costo(
        self,
        horas: int,
        descuento_porcentaje: float = 0.0,
        incluir_iva: bool = True,
        tasa_iva: float = 0.19,
    ) -> float:
        """Sobrescribe el cálculo agregando el depósito de garantía reembolsable."""
        costo_base = super().calcular_costo(horas, descuento_porcentaje, incluir_iva, tasa_iva)
        return round(costo_base + self.deposito_garantia, 2)

    def describir_servicio(self) -> str:
        return (
            f"Equipo '{self.nombre}' [Categoría: {self.categoria_hardware}] "
            f"(Depósito garantía: ${self.deposito_garantia:,.2f})"
        )


class AsesoriaEspecializada(Servicio):
    """Servicio especializado: Consultoría técnica en ingeniería y desarrollo."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base_hora: float,
        especialidad: str,
        consultor_senior: bool = False,
        disponible: bool = True,
    ):
        super().__init__(id_servicio, nombre, tarifa_base_hora, disponible)
        if not especialidad or not especialidad.strip():
            raise ParametroFaltanteError("La especialidad de la asesoría es obligatoria.")
        self.especialidad = especialidad.strip()
        self.consultor_senior = consultor_senior

    def validar_parametros(self, horas: int) -> None:
        if not isinstance(horas, int) or horas < 1 or horas > 40:
            raise DatoInvalidoError(
                f"La asesoría especializada admite entre 1 y 40 horas (recibido: {horas})."
            )

    def calcular_costo(
        self,
        horas: int,
        descuento_porcentaje: float = 0.0,
        incluir_iva: bool = True,
        tasa_iva: float = 0.19,
    ) -> float:
        """Aplica un recargo del 25% si el consultor asignado es nivel Senior."""
        costo = super().calcular_costo(horas, descuento_porcentaje, incluir_iva, tasa_iva)
        if self.consultor_senior:
            costo *= 1.25
        return round(costo, 2)

    def describir_servicio(self) -> str:
        nivel = "Consultor Senior (+25%)" if self.consultor_senior else "Consultor Estándar"
        return f"Asesoría '{self.nombre}' en {self.especialidad} ({nivel})"


class Reserva(EntidadSistema):
    """Integra Cliente, Servicio y duración gestionando el ciclo de vida de la reserva."""

    ESTADOS_VALIDOS = ("PENDIENTE", "CONFIRMADA", "PROCESADA", "CANCELADA")

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion_horas: int,
        descuento: float = 0.0,
    ):
        super().__init__(id_reserva)
        if not isinstance(cliente, Cliente) or not cliente.validar_integridad():
            raise DatoInvalidoError("La reserva requiere un objeto Cliente válido.")
        if not isinstance(servicio, Servicio) or not servicio.validar_integridad():
            raise DatoInvalidoError("La reserva requiere un objeto Servicio válido.")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{servicio.nombre}' no se encuentra disponible actualmente."
            )

        self._cliente = cliente
        self._servicio = servicio
        self._duracion_horas = duracion_horas
        self._descuento = descuento
        self._estado = "PENDIENTE"

        try:
            self._costo_total = self._servicio.calcular_costo(
                horas=self._duracion_horas,
                descuento_porcentaje=self._descuento,
            )
        except Exception as err:
            raise ReservaInvalidaError(
                f"No fue posible inicializar la reserva '{id_reserva}' por error en parámetros."
            ) from err

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo_total(self) -> float:
        return self._costo_total

    @singledispatchmethod
    def aplicar_ajuste(self, ajuste) -> float:
        """Método sobrecargado por tipo de dato para recalcular el costo de la reserva."""
        raise DatoInvalidoError(f"Tipo de ajuste no soportado: {type(ajuste).__name__}")

    @aplicar_ajuste.register
    def _(self, ajuste: float) -> float:
        """Sobrecarga 1: Si recibe float (entre 0 y 100), aplica nuevo porcentaje de descuento."""
        self._descuento = ajuste
        self._costo_total = self._servicio.calcular_costo(self._duracion_horas, self._descuento)
        return self._costo_total

    @aplicar_ajuste.register
    def _(self, ajuste: int) -> float:
        """Sobrecarga 2: Si recibe int, actualiza la duración en horas de la reserva."""
        if self._estado != "PENDIENTE":
            raise OperacionNoPermitidaError("Solo se puede modificar duración en estado PENDIENTE.")
        self._duracion_horas = ajuste
        self._costo_total = self._servicio.calcular_costo(self._duracion_horas, self._descuento)
        return self._costo_total

    def confirmar(self) -> None:
        """Cambia el estado de PENDIENTE a CONFIRMADA."""
        if self._estado != "PENDIENTE":
            raise OperacionNoPermitidaError(
                f"No se puede confirmar la reserva '{self.id}' en estado '{self._estado}'."
            )
        self._estado = "CONFIRMADA"

    def procesar(self) -> None:
        """Ejecuta el servicio y marca la reserva como PROCESADA."""
        if self._estado != "CONFIRMADA":
            raise OperacionNoPermitidaError(
                f"La reserva '{self.id}' debe estar CONFIRMADA antes de procesarse (actual: '{self._estado}')."
            )
        self._estado = "PROCESADA"

    def cancelar(self) -> None:
        """Cancela la reserva siempre que aún no haya sido PROCESADA."""
        if self._estado == "PROCESADA":
            raise OperacionNoPermitidaError(
                f"Imposible cancelar la reserva '{self.id}' porque ya fue PROCESADA."
            )
        if self._estado == "CANCELADA":
            raise OperacionNoPermitidaError(f"La reserva '{self.id}' ya se encuentra CANCELADA.")
        self._estado = "CANCELADA"

    def validar_integridad(self) -> bool:
        return self._estado in self.ESTADOS_VALIDOS and self._costo_total > 0

    def obtener_resumen(self) -> str:
        return (
            f"Reserva [{self.id}] | Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio.nombre} ({self._duracion_horas}h) | "
            f"Total: ${self._costo_total:,.2f} | Estado: {self._estado}"
        )