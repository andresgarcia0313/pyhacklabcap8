#!/usr/bin/env bash
# Paso 9: deja el entorno limpio. Detiene el simulador si quedó corriendo.
# Uso: ./limpiar.sh                 (conserva registros, resultados y reportes)
#      ./limpiar.sh --borrar-datos  (además borra toolkit/datos/, datos_comprobacion/ y reporte_final.*)
set -euo pipefail
cd "$(dirname "$0")"

if pkill -f '^python[0-9.]* (\./)?simulador_servicios\.py'; then
  for _ in $(seq 1 20); do  # espera hasta 5 s a que el proceso termine
    pgrep -f '^python[0-9.]* (\./)?simulador_servicios\.py' >/dev/null || break
    sleep 0.25
  done
  echo "[+] Simulador detenido"
else
  echo "[=] El simulador no estaba corriendo"
fi

if [[ "${1:-}" == "--borrar-datos" ]]; then
  rm -rf -- toolkit/datos datos_comprobacion
  rm -f -- reporte_final.html reporte_final.md
  echo "[+] Registros, resultados y reportes borrados"
else
  echo "[=] Datos conservados en toolkit/datos/ (trátelos como confidenciales)"
fi
