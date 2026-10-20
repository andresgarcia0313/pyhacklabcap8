#!/usr/bin/env bash
# Ejecuta el laboratorio 8 completo en local y se detiene en el primer fallo:
# entorno -> permiso -> pruebas -> simulador -> pasos 1 a 3 -> CLI -> reporte -> validación -> limpieza.
# Usa la carpeta datos_comprobacion/ para no mezclarse con sus datos de toolkit/datos/.
# Uso: ./ejecutar_laboratorio.sh
set -euo pipefail
cd "$(dirname "$0")"

# Archivos que construye el estudiante y el paso de la guía que los crea
faltan=0
for par in toolkit/modules/auth_manager.py:1 toolkit/modules/audit_logger.py:2 toolkit/modules/escaner.py:3 \
           toolkit/cli.py:4 toolkit/modules/report_generator.py:5 toolkit/templates/reporte.html:5 \
           toolkit/tests/test_autorizacion.py:6; do
  if [[ ! -f "${par%%:*}" ]]; then
    echo "[!] Falta ${par%%:*}: se crea en el Paso ${par##*:} de la guía"
    faltan=1
  fi
done
[[ $faltan -eq 0 ]] || exit 1

PID_SIM=""
detener_simulador() {
  if [[ -n "$PID_SIM" ]] && kill -0 "$PID_SIM" 2>/dev/null; then
    kill "$PID_SIM" && wait "$PID_SIM" 2>/dev/null || true
  fi
  PID_SIM=""
}
trap detener_simulador EXIT

puerto_abierto() {
  python3 -c "import socket; socket.create_connection(('127.0.0.1', 20022), 1)" 2>/dev/null
}

titulo() { printf '\n========== %s ==========\n' "$1"; }
debe_fallar() {  # ejecuta un comando que DEBE terminar con código 1
  if "$@"; then echo "[!] Se esperaba una negación y el comando terminó bien"; exit 1; fi
  echo "    -> negado con código 1, como se esperaba"
}

titulo "Paso 0: entorno virtual, dependencias y permiso"
# --system-site-packages reutiliza jinja2 y pytest si ya están instalados (funciona sin Internet)
[[ -d .venv ]] || python3 -m venv --system-site-packages .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python3 -m pip install -q -r requirements.txt
python3 -c "import jinja2, pytest; print('Dependencias OK, jinja2', jinja2.__version__, '| pytest', pytest.__version__)"
python3 preparar_autorizacion.py

titulo "Paso 6: pruebas automáticas (sin simulador)"
python3 -m pytest

export TOOLKIT_DATOS="$PWD/datos_comprobacion"
rm -rf -- "${TOOLKIT_DATOS:?}"

titulo "Simulador"
if puerto_abierto; then echo "[!] El puerto 20022 ya está en uso. Ejecute ./limpiar.sh y vuelva a intentarlo."; exit 1; fi
python3 simulador_servicios.py &
PID_SIM=$!
for _ in $(seq 1 20); do puerto_abierto && break; sleep 0.25; done
puerto_abierto || { echo "[!] El simulador no arrancó"; exit 1; }

titulo "Pasos 1 a 3: comprobaciones"
python3 pasos/paso1_autorizacion.py
python3 pasos/paso2_auditoria.py
python3 pasos/paso3_modulos.py

titulo "Paso 4: la CLI con permiso y sin permiso"
python3 -m toolkit.cli recon localhost
python3 -m toolkit.cli scan 127.0.0.1
python3 -m toolkit.cli web http://127.0.0.1:20080/
debe_fallar python3 -m toolkit.cli scan 127.0.0.10

titulo "Paso 5: reporte"
python3 -m toolkit.cli report --salida "$TOOLKIT_DATOS/reporte_final.html"
python3 -m toolkit.cli report --formato markdown --salida "$TOOLKIT_DATOS/reporte_final.md"
debe_fallar python3 -m toolkit.cli --auth no_existe.json report --salida "$TOOLKIT_DATOS/sin_permiso.html"

titulo "Paso 7: validación"
python3 validar.py "$TOOLKIT_DATOS/reporte_final.html"

titulo "Paso 9: limpieza"
detener_simulador
pgrep -af '^python[0-9.]* (\./)?simulador_servicios\.py' || echo "Sin procesos del laboratorio activos"
echo; echo "LABORATORIO COMPLETADO"
