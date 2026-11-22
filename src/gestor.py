"""
Controlador principal del sistema Software FJ.
Gestiona colecciones internas en memoria (sin base de datos) y centraliza
el manejo avanzado de excepciones (try/except, else, finally) con auditoría en logs.
"""

from typing import List, Optional
from src.excepciones import ErrorSistemaFJ, DatoInvalidoError
from src.logger_sistema import LoggerSistema
from src.modelos import Cliente, Servicio, Reserva


class SistemaGestionFJ:
	"""Orquestador de clientes, servicios y reservas en memoria."""

	def __init__(self, logger: Optional[LoggerSistema] = None):
		# Listas internas para almacenamiento en memoria (sin motor de base de datos)
		self._clientes: List[Cliente] = []
		self._servicios: List[Servicio] = []
		self._reservas: List[Reserva] = []
		self._logger = logger or LoggerSistema()
		self._logger.registrar_evento("INFO", "SistemaGestionFJ", "Sistema inicializado correctamente.")

	def registrar_cliente(self, cliente: Cliente) -> bool:
		"""Registra un cliente validando duplicados con bloque try/except/else."""
		try:
			if any(c.id == cliente.id for c in self._clientes):
				raise DatoInvalidoError(f"Ya existe un cliente registrado con ID '{cliente.id}'.")
			if any(c.correo == cliente.correo for c in self._clientes):
				raise DatoInvalidoError(f"El correo '{cliente.correo}' ya pertenece a otro cliente.")
		except ErrorSistemaFJ as err:
			self._logger.registrar_evento("ERROR", "Clientes", f"Fallo al registrar cliente: {err}")
			print(f"  [ERROR CONTROLADO] {err}")
			return False
		else:
			# Se ejecuta únicamente si el bloque try finalizó sin lanzar excepciones
			self._clientes.append(cliente)
			msg = f"Cliente registrado exitosamente: {cliente.obtener_resumen()}"
			self._logger.registrar_evento("INFO", "Clientes", msg)
			print(f"  [OK] {msg}")
			return True

	def agregar_servicio(self, servicio: Servicio) -> bool:
		"""Agrega un servicio al catálogo usando try/except/else."""
		try:
			if any(s.id == servicio.id for s in self._servicios):
				raise DatoInvalidoError(f"Ya existe un servicio con ID '{servicio.id}'.")
		except ErrorSistemaFJ as err:
			self._logger.registrar_evento("ERROR", "Servicios", f"Fallo al agregar servicio: {err}")
			print(f"  [ERROR CONTROLADO] {err}")
			return False
		else:
			self._servicios.append(servicio)
			msg = f"Servicio añadido: {servicio.describir_servicio()} | Tarifa: ${servicio.tarifa_base_hora:,.2f}/h"
			self._logger.registrar_evento("INFO", "Servicios", msg)
			print(f"  [OK] {msg}")
			return True

	def crear_reserva(
		self,
		id_reserva: str,
		id_cliente: str,
		id_servicio: str,
		duracion_horas: int,
		descuento: float = 0.0,
	) -> Optional[Reserva]:
		"""
		Crea una reserva vinculando cliente y servicio.
		Implementa try/except/else/finally para garantizar trazabilidad completa.
		"""
		nueva_reserva: Optional[Reserva] = None
		try:
			cliente = next((c for c in self._clientes if c.id == id_cliente), None)
			if not cliente:
				raise DatoInvalidoError(f"No se encontró cliente con ID '{id_cliente}'.")

			servicio = next((s for s in self._servicios if s.id == id_servicio), None)
			if not servicio:
				raise DatoInvalidoError(f"No se encontró servicio con ID '{id_servicio}'.")

			if any(r.id == id_reserva for r in self._reservas):
				raise DatoInvalidoError(f"El ID de reserva '{id_reserva}' ya está en uso.")

			nueva_reserva = Reserva(id_reserva, cliente, servicio, duracion_horas, descuento)

		except ErrorSistemaFJ as err:
			causa = f" | Causa raíz: {err.__cause__}" if err.__cause__ else ""
			detalle = f"Error al crear reserva '{id_reserva}': {err}{causa}"
			self._logger.registrar_evento("ERROR", "Reservas", detalle)
			print(f"  [ERROR CONTROLADO] {detalle}")
			return None
		else:
			self._reservas.append(nueva_reserva)
			msg = f"Reserva creada: {nueva_reserva.obtener_resumen()}"
			self._logger.registrar_evento("INFO", "Reservas", msg)
			print(f"  [OK] {msg}")
			return nueva_reserva
		finally:
			# Se ejecuta siempre, haya ocurrido error o éxito
			self._logger.registrar_evento(
				"AUDIT", "Reservas", f"Finalizado intento de transacción para reserva '{id_reserva}'."
			)

	def gestionar_estado_reserva(self, id_reserva: str, accion: str) -> bool:
		"""Ejecuta confirmar, procesar o cancelar sobre una reserva con manejo de excepciones."""
		try:
			reserva = next((r for r in self._reservas if r.id == id_reserva), None)
			if not reserva:
				raise DatoInvalidoError(f"No existe la reserva '{id_reserva}'.")

			accion_norm = accion.strip().lower()
			if accion_norm == "confirmar":
				reserva.confirmar()
			elif accion_norm == "procesar":
				reserva.procesar()
			elif accion_norm == "cancelar":
				reserva.cancelar()
			else:
				raise DatoInvalidoError(f"Acción desconocida: '{accion}'.")

		except ErrorSistemaFJ as err:
			self._logger.registrar_evento("ERROR", "EstadosReserva", f"Acción '{accion}' fallida: {err}")
			print(f"  [ERROR CONTROLADO] {err}")
			return False
		else:
			msg = f"Reserva '{id_reserva}' actualizada -> Nuevo estado: {reserva.estado}"
			self._logger.registrar_evento("INFO", "EstadosReserva", msg)
			print(f"  [OK] {msg}")
			return True

	def generar_reporte_consola(self) -> None:
		"""Muestra el resumen final del estado en memoria tras las simulaciones."""
		print("\n" + "=" * 75)
		print("RESUMEN FINAL EN MEMORIA - SOFTWARE FJ")
		print("=" * 75)
		print(f"Total Clientes activos : {len(self._clientes)}")
		print(f"Total Servicios activos: {len(self._servicios)}")
		print(f"Total Reservas válidas : {len(self._reservas)}")
		print("-" * 75)
		for reserva in self._reservas:
			print(f"  • {reserva.obtener_resumen()}")
		print("=" * 75)
