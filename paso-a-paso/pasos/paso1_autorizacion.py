"""
Paso 1: revisar el permiso y probar qué objetivos acepta.
Uso (desde la carpeta del laboratorio): python3 pasos/paso1_autorizacion.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from toolkit.modules.auth_manager import (AutorizacionError, cargar_autorizacion,  # noqa: E402
                                          huella_autorizacion, verificar_activo_autorizado)

try:
    permiso = cargar_autorizacion("authorization.json")
except AutorizacionError as error:
    sys.exit(f"[AUTH] {error}")
print(f"Cliente: {permiso['cliente']} | Vigencia: {permiso['fecha_inicio']} a {permiso['fecha_fin']}")
print(f"Huella: {huella_autorizacion(permiso)}\n")
print(f"{'Objetivo':<22} ¿Autorizado?")
for objetivo in ["127.0.0.1", "127.0.0.10", "localhost", "LOCALHOST", "localhost.ejemplo.com", "192.0.2.10"]:
    print(f"{objetivo:<22} {'sí' if verificar_activo_autorizado(objetivo, permiso) else 'NO'}")
