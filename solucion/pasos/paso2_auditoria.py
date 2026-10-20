"""
Paso 2: escribir dos acciones en un registro de prueba y leerlas de vuelta.
Usa una carpeta temporal: no toca su registro real.
Uso: python3 pasos/paso2_auditoria.py
"""
import logging
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from toolkit.modules.audit_logger import configurar_logger, leer_auditoria, registrar  # noqa: E402

with tempfile.TemporaryDirectory() as carpeta:
    os.environ["TOOLKIT_DATOS"] = carpeta  # la carpeta de datos pasa a ser la temporal
    logger = configurar_logger()
    registrar(logger, "scan", "127.0.0.1", "2 hallazgo(s)")
    registrar(logger, "scan", "192.0.2.10", "DENEGADO: no autorizado\nlínea falsa", logging.WARNING)
    for nombre in os.listdir(carpeta):
        print(f"--- {nombre} ---")
        with open(os.path.join(carpeta, nombre), encoding="utf-8") as archivo:
            print(archivo.read().replace(os.getenv("USER", "?"), "<usuario>"), end="")
    print(f"\nEntradas leídas de vuelta: {len(leer_auditoria())}")
    logging.getLogger("toolkit").handlers[0].close()
