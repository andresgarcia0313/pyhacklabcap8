#!/usr/bin/env python3
"""
validar.py - Paso 7 de la guía: comprobaciones que SÍ pueden fallar. Ya viene listo.
  7.1 el permiso es válido y la auditoría registró cada módulo y al menos una negación.
  7.2 ningún resultado guardado apunta a un objetivo fuera del permiso.
  7.3 el reporte HTML trae los hallazgos que observaron los módulos.
  7.4 el reporte muestra como texto las etiquetas HTML de un banner.
Uso: python3 validar.py [reporte.html]   (por defecto, reporte_final.html)
Sale con código 0 si todo pasa y 1 si algo falla.
"""
import pathlib
import sys
from urllib.parse import urlsplit

from toolkit.modules.audit_logger import leer_auditoria, leer_resultados
from toolkit.modules.auth_manager import AutorizacionError, cargar_autorizacion, verificar_activo_autorizado

fallos = []


def comprobar(nombre: str, ok: bool, detalle: str = "") -> None:
    print(f"  {'PASA ' if ok else 'FALLA'} | {nombre}{f' ({detalle})' if detalle else ''}")
    if not ok:
        fallos.append(nombre)


try:
    permiso = cargar_autorizacion("authorization.json")
except AutorizacionError as error:
    sys.exit(f"FALLA | {error}")
reporte = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "reporte_final.html")
if not reporte.exists():
    sys.exit(f"FALLA | No existe {reporte}. Genérelo con: python3 -m toolkit.cli report")
html = reporte.read_text(encoding="utf-8")
auditoria = leer_auditoria()

print("\n7.1 Permiso y auditoría")
comprobar("Permiso vigente", True, f"{permiso['fecha_inicio']} a {permiso['fecha_fin']}")
for modulo in ("recon", "scan", "web", "report"):
    comprobar(f"Auditoría registra {modulo}", any(e["accion"] == modulo for e in auditoria))
comprobar("Auditoría registra una negación", any(e["resultado"].startswith("DENEGADO") for e in auditoria))

print("\n7.2 Solo objetivos autorizados")
for r in leer_resultados():
    equipo = urlsplit(r["objetivo"]).hostname if r["modulo"] == "web" else r["objetivo"]
    comprobar(f"{r['modulo']} sobre {r['objetivo']}", verificar_activo_autorizado(equipo, permiso))

print("\n7.3 Hallazgos observados en el reporte")
for texto in ("vsftpd 2.3.4", "OpenSSH 4", "Apache 2.2", "Falta la cabecera X-Frame-Options",
              "localhost resuelve a"):
    comprobar(texto, texto in html)
comprobar("Hallazgos numerados desde HALL-001", "HALL-001" in html)

print("\n7.4 Escape del HTML")
comprobar("La etiqueta del banner aparece como texto", "&lt;b&gt;correo.lab&lt;/b&gt;" in html)
comprobar("La etiqueta del banner no llega cruda", "<b>correo.lab</b>" not in html)

print(f"\nResultado final: {'TODO PASA' if not fallos else f'{len(fallos)} FALLO(S): {fallos}'}")
sys.exit(1 if fallos else 0)
