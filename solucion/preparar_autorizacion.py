#!/usr/bin/env python3
"""
preparar_autorizacion.py - Crea authorization.json a partir del ejemplo. Ya viene listo.

Copia authorization.ejemplo.json y pone las fechas de vigencia desde HOY hasta
dentro de 30 días. Así el permiso del laboratorio nunca llega vencido.
Si authorization.json ya existe, no lo toca (use --forzar para rehacerlo).

Uso: python3 preparar_autorizacion.py [--forzar]
"""
import datetime
import json
import pathlib
import sys

CARPETA = pathlib.Path(__file__).resolve().parent
EJEMPLO, DESTINO = CARPETA / "authorization.ejemplo.json", CARPETA / "authorization.json"

if DESTINO.exists() and "--forzar" not in sys.argv:
    print(f"[=] {DESTINO.name} ya existe; no se modifica (use --forzar para rehacerlo)")
    sys.exit(0)
datos = json.loads(EJEMPLO.read_text(encoding="utf-8"))
hoy = datetime.date.today()
datos["fecha_inicio"] = hoy.isoformat()
datos["fecha_fin"] = (hoy + datetime.timedelta(days=30)).isoformat()
DESTINO.write_text(json.dumps(datos, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"[+] {DESTINO.name} creado: vigente del {datos['fecha_inicio']} al {datos['fecha_fin']}")
print(f"    Activos autorizados: {', '.join(datos['activos_autorizados'])}")
