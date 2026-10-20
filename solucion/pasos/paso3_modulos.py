"""
Paso 3: probar los tres módulos directamente (con el simulador corriendo).
Uso: python3 pasos/paso3_modulos.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from toolkit.modules import escaner  # noqa: E402

print("recon localhost ->", escaner.reconocer("localhost")["detalle"])
print("\nscan 127.0.0.1, puertos 20021 y 20023 ->")
print(json.dumps(escaner.escanear("127.0.0.1", [20021, 20023], 1.0)["detalle"], indent=2))
web = escaner.revisar_web("http://127.0.0.1:20080/", 2.0)
print(f"\nweb -> estado {web['detalle']['estado']}, Server: {web['detalle']['server']}")
for h in web["hallazgos"]:
    print(f"  [{h['severidad']}] {h['descripcion']}")
