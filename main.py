"""
Punto de entrada principal del Sistema Integral de Gestión de Clientes, Servicios y Reservas.
Empresa: Software FJ - UNAD Programación (213023) Fase 4.
Ejecuta 12 escenarios simulados (válidos e inválidos) sin interrumpir el flujo del programa.
"""

from src.excepciones import ErrorSistemaFJ
from src.logger_sistema import LoggerSistema
from src.gestor import SistemaGestionFJ
from src.modelos import (
	Cliente,
	ReservaSala,
	AlquilerEquipo,
	AsesoriaEspecializada,
)


def ejecutar_simulacion() -> None:
	logger = LoggerSistema("logs/eventos_sistema.log")
	sistema = SistemaGestionFJ(logger)

	print("\n--- INICIANDO SIMULACIÓN DE 12 OPERACIONES EN SOFTWARE FJ ---\n")

	# 1. Registro válido de Cliente 1
	print("[Operación 1] Registro válido de cliente:")
	try:
		c1 = Cliente("CLI-001", "Laura Gómez", "laura.gomez@empresa.com", "3104567890")
		sistema.registrar_cliente(c1)
	except ErrorSistemaFJ as e:
		logger.registrar_evento("ERROR", "Main", str(e))

	# 2. Registro válido de Cliente 2
	print("\n[Operación 2] Registro válido de segundo cliente:")
	try:
		c2 = Cliente("CLI-002", "Carlos Mendoza", "cmendoza@techcol.co", "3209876543")
		sistema.registrar_cliente(c2)
	except ErrorSistemaFJ as e:
		logger.registrar_evento("ERROR", "Main", str(e))

	# 3. Registro inválido de Cliente (correo mal formado y teléfono corto)
	print("\n[Operación 3] Registro inválido de cliente (correo sin dominio):")
	try:
		c_invalido = Cliente("CLI-003", "Andrés Ruiz", "andres_correo_invalido", "123")
		sistema.registrar_cliente(c_invalido)
	except ErrorSistemaFJ as e:
		logger.registrar_evento("ERROR", "Main", f"Bloqueado en instanciación de Cliente: {e}")
		print(f"  [ERROR CONTROLADO] {e}")

	# 4. Registro inválido de Cliente duplicado
	print("\n[Operación 4] Registro inválido de cliente con correo duplicado:")
	try:
		c_duplicado = Cliente("CLI-004", "Laura G.", "laura.gomez@empresa.com", "3001112233")
		sistema.registrar_cliente(c_duplicado)
	except ErrorSistemaFJ as e:
		logger.registrar_evento("ERROR", "Main", str(e))

	# 5. Creación correcta de tres servicios especializados (Polimorfismo)
	print("\n[Operación 5] Creación válida de 3 servicios especializados:")
	try:
		s_sala = ReservaSala("SRV-01", "Sala Innovación Ágil", 85000, capacidad_personas=12)
		s_equipo = AlquilerEquipo(
			"SRV-02", "Workstation GPU RTX", 45000, "Computación Alto Rendimiento", deposito_garantia=100000
		)
		s_asesoria = AsesoriaEspecializada(
			"SRV-03", "Arquitectura Cloud", 120000, "Computación en la Nube", consultor_senior=True
		)
		s_inactivo = ReservaSala("SRV-04", "Sala Mantenimiento", 60000, capacidad_personas=6, disponible=False)

		sistema.agregar_servicio(s_sala)
		sistema.agregar_servicio(s_equipo)
		sistema.agregar_servicio(s_asesoria)
		sistema.agregar_servicio(s_inactivo)
	except ErrorSistemaFJ as e:
		logger.registrar_evento("ERROR", "Main", str(e))

	# 6. Creación incorrecta de servicio (tarifa negativa)
	print("\n[Operación 6] Creación inválida de servicio con tarifa negativa:")
	try:
		s_error = AlquilerEquipo("SRV-99", "Proyector 4K", -25000, "Audiovisual", 50000)
		sistema.agregar_servicio(s_error)
	except ErrorSistemaFJ as e:
		logger.registrar_evento("ERROR", "Main", f"Bloqueado en instanciación de Servicio: {e}")
		print(f"  [ERROR CONTROLADO] {e}")

	# 7. Reserva exitosa de Sala con descuento (prueba de sobrecarga de cálculo)
	print("\n[Operación 7] Reserva exitosa de Sala (4 horas, 10% descuento):")
	res1 = sistema.crear_reserva("RES-101", "CLI-001", "SRV-01", duracion_horas=4, descuento=10.0)

	# 8. Reserva exitosa de Equipo y uso de sobrecarga @singledispatchmethod
	print("\n[Operación 8] Reserva exitosa de Equipo (3 horas) y ajuste sobrecargado a 5 horas:")
	res2 = sistema.crear_reserva("RES-102", "CLI-002", "SRV-02", duracion_horas=3)
	if res2:
		nuevo_total = res2.aplicar_ajuste(5)  # Invoca sobrecarga para int (actualiza horas)
		msg_ajuste = f"Ajuste sobrecargado aplicado a RES-102 -> Nuevo total: ${nuevo_total:,.2f}"
		logger.registrar_evento("INFO", "Main", msg_ajuste)
		print(f"  [OK] {msg_ajuste}")

	# 9. Reserva fallida por encadenamiento de excepciones (alquiler mínimo 2 horas, se pide 1)
	print("\n[Operación 9] Reserva fallida por duración inferior al mínimo (1h en alquiler de equipo):")
	sistema.crear_reserva("RES-103", "CLI-001", "SRV-02", duracion_horas=1)

	# 10. Reserva fallida por servicio no disponible
	print("\n[Operación 10] Reserva fallida por servicio no disponible:")
	sistema.crear_reserva("RES-104", "CLI-002", "SRV-04", duracion_horas=2)

	# 11. Flujo válido de estados: Confirmar y Procesar RES-101
	print("\n[Operación 11] Transición válida de estados (PENDIENTE -> CONFIRMADA -> PROCESADA):")
	sistema.gestionar_estado_reserva("RES-101", "confirmar")
	sistema.gestionar_estado_reserva("RES-101", "procesar")

	# 12. Operación no permitida: Intentar cancelar una reserva ya PROCESADA
	print("\n[Operación 12] Operación prohibida (cancelar reserva ya procesada):")
	sistema.gestionar_estado_reserva("RES-101", "cancelar")

	# Reporte final verificando que la aplicación concluyó sin interrupciones
	sistema.generar_reporte_consola()
	print("\nRegistro detallado guardado en: logs/eventos_sistema.log")


if __name__ == "__main__":
	ejecutar_simulacion()
