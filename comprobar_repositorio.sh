#!/usr/bin/env bash
# Comprobación integral para el instructor, antes de publicar cambios:
#   1. el material de apoyo es idéntico en paso-a-paso/ y solucion/;
#   2. el código de la guía es idéntico al de solucion/ y cada archivo tiene máximo 100 líneas de código;
#   3. la solución pasa el laboratorio completo;
#   4. un estudiante que pegue exactamente el código de la guía también lo pasa;
#   5. los enlaces internos de los documentos existen;
#   6. lint de Python y de shell sin avisos.
# Uso: ./comprobar_repositorio.sh
set -euo pipefail
cd "$(dirname "$0")"

titulo() { printf '\n########## %s ##########\n' "$1"; }

titulo "1. Material de apoyo idéntico en ambas carpetas"
for f in simulador_servicios.py preparar_autorizacion.py authorization.ejemplo.json validar.py pasos \
         ejecutar_laboratorio.sh limpiar.sh requirements.txt pytest.ini toolkit/__init__.py \
         toolkit/modules/__init__.py toolkit/tests/__init__.py toolkit/tests/conftest.py \
         toolkit/tests/test_auditoria.py toolkit/tests/test_escaner.py toolkit/tests/test_cli.py \
         toolkit/tests/test_reporte.py; do
  diff -rq --exclude=__pycache__ "paso-a-paso/$f" "solucion/$f"
  echo "PASS | $f"
done

titulo "2. Código de la guía frente a la solución"
python3 herramientas/comprobar_guia.py

titulo "3. Laboratorio completo con la solución"
solucion/ejecutar_laboratorio.sh

titulo "4. Laboratorio completo como estudiante (código copiado de la guía)"
ESTUDIANTE="$(mktemp -d)"
trap 'rm -rf -- "${ESTUDIANTE:?}"' EXIT
cp -r paso-a-paso/. "$ESTUDIANTE/"
rm -rf -- "${ESTUDIANTE:?}/.venv" "${ESTUDIANTE:?}/toolkit/datos" "${ESTUDIANTE:?}/authorization.json"
python3 herramientas/comprobar_guia.py --escribir "$ESTUDIANTE" > /dev/null
"$ESTUDIANTE/ejecutar_laboratorio.sh"

titulo "5. Enlaces internos de los documentos"
python3 - <<'PY'
import pathlib, re, sys
def texto_sin_codigo(md):  # los bloques y fragmentos de código no contienen enlaces
    return re.sub(r"```.*?```|`[^`]*`", "", md.read_text(encoding="utf-8"), flags=re.DOTALL)
rotos = [f"{md}: {destino}" for md in pathlib.Path(".").rglob("*.md") if ".venv" not in md.parts
         for destino in re.findall(r"\]\(([^)#:]+)\)", texto_sin_codigo(md))
         if not (md.parent / destino).exists()]
print("\n".join(f"FAIL | enlace roto en {r}" for r in rotos) or "PASS | todos los enlaces internos existen")
sys.exit(1 if rotos else 0)
PY

titulo "6. Lint"
ruff check --no-cache .
shellcheck ./*.sh paso-a-paso/*.sh solucion/*.sh
echo "shellcheck sin avisos"

echo; echo "REPOSITORIO CORRECTO"
