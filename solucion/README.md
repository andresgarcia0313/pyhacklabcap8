<!-- Idioma del documento: es-CO (español de Colombia) -->
# Solución del laboratorio 8

Esta carpeta es **la respuesta**: el toolkit terminado y funcionando. Si todavía no hace la práctica, empiece por la guía [`../paso-a-paso/README.md`](../paso-a-paso/README.md) y vuelva aquí solo para comparar.

## Ejecutarla

```bash
./ejecutar_laboratorio.sh
```

Prepara el entorno, crea el permiso si falta, corre las 34 pruebas, levanta el simulador, recorre los pasos 1 a 5 (con una negación a propósito), valida el reporte y limpia. Debe terminar con `LABORATORIO COMPLETADO`. Las salidas reales de cada paso están en [`output.md`](output.md).

## Los siete archivos de la respuesta

| Archivo | Paso de la guía | Qué hace |
|---|---|---|
| `toolkit/modules/auth_manager.py` | 1 | Lee el permiso, revisa campos y vigencia, y compara objetivos con `ipaddress`. |
| `toolkit/modules/audit_logger.py` | 2 | Registro de auditoría diario y resultados de cada módulo en JSON (JavaScript Object Notation). |
| `toolkit/modules/escaner.py` | 3 | Módulos `recon`, `scan` (banners TCP) y `web` (cabeceras HTTP), con hallazgos y evidencia. |
| `toolkit/cli.py` | 4 | CLI con `argparse`: permiso, objetivo, módulo, evidencia y auditoría. |
| `toolkit/templates/reporte.html` | 5 | Plantilla Jinja2 del reporte. |
| `toolkit/modules/report_generator.py` | 5 | Reporte HTML o Markdown con escape, sin repetidos y con datos sensibles ocultos. |
| `toolkit/tests/test_autorizacion.py` | 6 | Pruebas del permiso con pytest. |

El resto de archivos es el mismo material de apoyo de `paso-a-paso/`: simulador, permiso de ejemplo, comprobaciones por paso, pruebas, validación y scripts.

## Comparar con su trabajo

Desde `paso-a-paso/`:

```bash
diff toolkit/modules/auth_manager.py ../solucion/toolkit/modules/auth_manager.py
```

Si no hay salida, su archivo es idéntico a la respuesta. Si hay diferencias, no siempre son errores: lo que cuenta es que `python3 validar.py` y las pruebas pasen.

## Control de cambios

| Versión | Fecha | Autor | Descripción del cambio |
|---|---|---|---|
| 1.0.0 | 2026-10-20 | Andrés García | Solución del laboratorio 8 separada de la guía paso a paso. |
