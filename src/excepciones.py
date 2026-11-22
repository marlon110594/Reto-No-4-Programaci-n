"""
Módulo de excepciones personalizadas para el sistema de gestión de Software FJ.
Permite capturar y diferenciar errores específicos del negocio manteniendo la estabilidad.
"""


class ErrorSistemaFJ(Exception):
	"""Excepción base de la cual heredan todos los errores del sistema."""

	def __init__(self, mensaje: str, codigo_error: str = "ERR-000"):
		# Se almacena el código técnico del error junto con el mensaje descriptivo
		self.codigo_error = codigo_error
		self.mensaje = mensaje
		super().__init__(f"[{codigo_error}] {mensaje}")


class DatoInvalidoError(ErrorSistemaFJ):
	"""Se lanza cuando un atributo recibe un formato, tipo o rango no permitido."""

	def __init__(self, mensaje: str):
		super().__init__(mensaje, codigo_error="ERR-DATO")


class ParametroFaltanteError(ErrorSistemaFJ):
	"""Se lanza cuando se omite un campo obligatorio o llega vacío/None."""

	def __init__(self, mensaje: str):
		super().__init__(mensaje, codigo_error="ERR-PARAM")


class OperacionNoPermitidaError(ErrorSistemaFJ):
	"""Se lanza al intentar transiciones de estado inválidas o acciones prohibidas."""

	def __init__(self, mensaje: str):
		super().__init__(mensaje, codigo_error="ERR-OPER")


class ServicioNoDisponibleError(ErrorSistemaFJ):
	"""Se lanza cuando se intenta reservar un servicio inactivo o sin cupo/equipo."""

	def __init__(self, mensaje: str):
		super().__init__(mensaje, codigo_error="ERR-SERV")


class ReservaInvalidaError(ErrorSistemaFJ):
	"""Se lanza cuando falla el proceso de creación, validación o cálculo de una reserva."""

	def __init__(self, mensaje: str):
		super().__init__(mensaje, codigo_error="ERR-RESV")
