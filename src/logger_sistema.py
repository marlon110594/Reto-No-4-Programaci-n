"""
Módulo encargado de registrar eventos y errores en un archivo de logs plano.
Cumple con el requisito de persistir auditoría únicamente mediante manejo de archivos.
"""

import os
from datetime import datetime


class LoggerSistema:
	"""Clase utilitaria para escribir eventos operativos y excepciones en archivo."""

	def __init__(self, ruta_archivo: str = "logs/eventos_sistema.log"):
		# Se guarda la ruta del archivo de registro
		self.ruta_archivo = ruta_archivo
		# Se crea el directorio contenedor si aún no existe en el sistema de archivos
		directorio = os.path.dirname(self.ruta_archivo)
		if directorio and not os.path.exists(directorio):
			os.makedirs(directorio)

	def registrar_evento(self, nivel: str, modulo: str, mensaje: str) -> None:
		"""
		Escribe una línea formateada con marca de tiempo en el archivo de logs.
		Incluye manejo de errores propio para evitar caídas por fallos de E/S.
		"""
		marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		linea = f"[{marca_tiempo}] [{nivel.upper()}] [{modulo}] {mensaje}\n"

		try:
			# Se abre el archivo en modo 'append' (a) con codificación UTF-8
			with open(self.ruta_archivo, mode="a", encoding="utf-8") as archivo:
				archivo.write(linea)
		except OSError as error_io:
			# Fallback en consola si el disco está protegido o lleno
			print(f"[FALLO CRÍTICO DE LOG] No se pudo escribir en disco: {error_io}")
