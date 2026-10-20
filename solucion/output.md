<!-- Idioma del documento: es-CO (español de Colombia) -->
# Salidas reales del laboratorio 8

Ejecución del 2026-10-20 en Linux con Python 3.14.8, Jinja2 3.1.6 y pytest 9.1.1, con el simulador corriendo. Cada bloque muestra el comando y su salida sin editar. Las fechas, la huella del permiso y los nombres de archivo cambian en cada ejecución. Las rutas absolutas se acortan a `pyhacklabcap8/`. Los datos de esta corrida se guardaron en una carpeta temporal (variable `TOOLKIT_DATOS`).

## Paso 1: permiso vigente

```bash
python3 preparar_autorizacion.py --forzar
```

```text
[+] authorization.json creado: vigente del 2026-10-20 al 2026-11-19
    Activos autorizados: 127.0.0.1, localhost
(código de salida: 0)
```

## Paso 1: qué objetivos acepta el permiso

```bash
python3 pasos/paso1_autorizacion.py
```

```text
Cliente: Laboratorio local del curso | Vigencia: 2026-10-20 a 2026-11-19
Huella: d849d0441f0e7113

Objetivo               ¿Autorizado?
127.0.0.1              sí
127.0.0.10             NO
localhost              sí
LOCALHOST              sí
localhost.ejemplo.com  NO
192.0.2.10             NO
(código de salida: 0)
```

## Paso 2: auditoría en una carpeta temporal

```bash
python3 pasos/paso2_auditoria.py
```

```text
--- audit_2026-10-20.log ---
2026-10-20 15:47:08 | INFO     | USUARIO=<usuario> | ACCION=scan | OBJETIVO=127.0.0.1 | RESULTADO=2 hallazgo(s)
2026-10-20 15:47:08 | WARNING  | USUARIO=<usuario> | ACCION=scan | OBJETIVO=192.0.2.10 | RESULTADO=DENEGADO: no autorizado línea falsa

Entradas leídas de vuelta: 2
(código de salida: 0)
```

## Paso 3: los tres módulos (simulador corriendo)

```bash
python3 pasos/paso3_modulos.py
```

```text
recon localhost -> ['127.0.0.1']

scan 127.0.0.1, puertos 20021 y 20023 ->
{
  "20021": "220 (vsFTPd 2.3.4)",
  "20023": "cerrado"
}

web -> estado 200, Server: Apache/2.2.8 (Ubuntu) DAV/2
  [HIGH] Cabecera Server: versión antigua expuesta. Apache 2.2 terminó su soporte en 2017
  [MEDIUM] Falta la cabecera Content-Security-Policy
  [MEDIUM] Falta la cabecera X-Frame-Options
  [MEDIUM] Falta la cabecera X-Content-Type-Options
(código de salida: 0)
```

## Paso 4: ayuda de la CLI

```bash
python3 -m toolkit.cli --help
```

```text
usage: toolkit [-h] [--auth AUTH] MODULO ...

Toolkit de pruebas de seguridad autorizadas. Solo con permiso escrito.

positional arguments:
  MODULO
    recon      resolver un nombre a sus direcciones IP
    scan       leer los banners (saludos) de puertos TCP
    web        revisar las cabeceras de seguridad de una página
    report     generar el reporte con los hallazgos guardados

options:
  -h, --help   show this help message and exit
  --auth AUTH  archivo de autorización
(código de salida: 0)
```

## Paso 4: recon

```bash
python3 -m toolkit.cli recon localhost
```

```text
================================================================
  TOOLKIT DE PRUEBAS AUTORIZADAS - solo con permiso escrito
================================================================
[AUTH] Cliente: Laboratorio local del curso | Huella: d849d0441f0e7113
  [INFO  ] localhost resuelve a 127.0.0.1
[OK] 1 hallazgo(s) guardados en ../../../../../../../../../../../..$TOOLKIT_DATOS/resultado_recon_20261020_154709_351457.json
(código de salida: 0)
```

## Paso 4: scan

```bash
python3 -m toolkit.cli scan 127.0.0.1
```

```text
================================================================
  TOOLKIT DE PRUEBAS AUTORIZADAS - solo con permiso escrito
================================================================
[AUTH] Cliente: Laboratorio local del curso | Huella: d849d0441f0e7113
  [HIGH  ] Puerto 20021: versión antigua expuesta. vsftpd 2.3.4 tiene una puerta trasera pública (CVE-2011-2523)
  [HIGH  ] Puerto 20022: versión antigua expuesta. OpenSSH 4 está sin soporte desde hace más de quince años
  [LOW   ] Puerto 20025: el servicio dice qué software usa
  [INFO  ] Puerto 20080 abierto sin banner
[OK] 4 hallazgo(s) guardados en ../../../../../../../../../../../..$TOOLKIT_DATOS/resultado_scan_20261020_154710_509635.json
(código de salida: 0)
```

## Paso 4: web

```bash
python3 -m toolkit.cli web http://127.0.0.1:20080/
```

```text
================================================================
  TOOLKIT DE PRUEBAS AUTORIZADAS - solo con permiso escrito
================================================================
[AUTH] Cliente: Laboratorio local del curso | Huella: d849d0441f0e7113
  [HIGH  ] Cabecera Server: versión antigua expuesta. Apache 2.2 terminó su soporte en 2017
  [MEDIUM] Falta la cabecera Content-Security-Policy
  [MEDIUM] Falta la cabecera X-Frame-Options
  [MEDIUM] Falta la cabecera X-Content-Type-Options
[OK] 4 hallazgo(s) guardados en ../../../../../../../../../../../..$TOOLKIT_DATOS/resultado_web_20261020_154710_692291.json
(código de salida: 0)
```

## Paso 4: objetivo no autorizado

```bash
python3 -m toolkit.cli scan 127.0.0.10
```

```text
================================================================
  TOOLKIT DE PRUEBAS AUTORIZADAS - solo con permiso escrito
================================================================
[AUTH] Cliente: Laboratorio local del curso | Huella: d849d0441f0e7113
[DENEGADO] El objetivo '127.0.0.10' NO está en los activos autorizados
(código de salida: 1)
```

## Paso 4: minuta del día

```bash
tail -n 2 $TOOLKIT_DATOS/audit_*.log
```

```text
2026-10-20 15:47:10 | INFO     | USUARIO=andres | ACCION=web | OBJETIVO=http://127.0.0.1:20080/ | RESULTADO=4 hallazgo(s) en resultado_web_20261020_154710_692291.json
2026-10-20 15:47:10 | WARNING  | USUARIO=andres | ACCION=scan | OBJETIVO=127.0.0.10 | RESULTADO=DENEGADO: El objetivo '127.0.0.10' NO está en los activos autorizados
(código de salida: 0)
```

## Paso 5: reporte HTML

```bash
python3 -m toolkit.cli report --salida /tmp/reportes/reporte_final.html
```

```text
================================================================
  TOOLKIT DE PRUEBAS AUTORIZADAS - solo con permiso escrito
================================================================
[AUTH] Cliente: Laboratorio local del curso | Huella: d849d0441f0e7113
[OK] Reporte con 9 hallazgo(s) en: /tmp/reportes/reporte_final.html
(código de salida: 0)
```

## Paso 5: reporte Markdown

```bash
python3 -m toolkit.cli report --formato markdown --salida /tmp/reportes/reporte_final.md
```

```text
================================================================
  TOOLKIT DE PRUEBAS AUTORIZADAS - solo con permiso escrito
================================================================
[AUTH] Cliente: Laboratorio local del curso | Huella: d849d0441f0e7113
[OK] Reporte con 9 hallazgo(s) en: /tmp/reportes/reporte_final.md
(código de salida: 0)
```

## Paso 5: contenido del reporte Markdown

```bash
cat /tmp/reportes/reporte_final.md
```

```text
# Reporte de pruebas de seguridad autorizadas

Confidencial. Generado el 2026-10-20 15:47:11.

## 1. Proyecto

- Cliente: Laboratorio local del curso
- Identificador del permiso: PERMISO-LAB08-001
- Tipo de prueba: caja_gris
- Vigencia: 2026-10-20 a 2026-11-19
- Huella de la autorización: `d849d0441f0e7113`

## 2. Resumen

CRITICAL: 0, HIGH: 3, MEDIUM: 3, LOW: 1, INFO: 2

Severidades: CRITICAL (crítica), HIGH (alta), MEDIUM (media), LOW (baja), INFO (informativa).

## 3. Hallazgos

| ID | Severidad | Módulo | Descripción | Evidencia | Recomendación |
|---|---|---|---|---|---|
| HALL-001 | HIGH | scan | Puerto 20021: versión antigua expuesta. vsftpd 2.3.4 tiene una puerta trasera pública (CVE-2011-2523) | 220 (vsFTPd 2.3.4) | Actualizar el servicio a una versión con soporte |
| HALL-002 | HIGH | scan | Puerto 20022: versión antigua expuesta. OpenSSH 4 está sin soporte desde hace más de quince años | SSH-2.0-OpenSSH_4.7p1 Debian-8ubuntu1 | Actualizar el servicio a una versión con soporte |
| HALL-003 | HIGH | web | Cabecera Server: versión antigua expuesta. Apache 2.2 terminó su soporte en 2017 | Apache/2.2.8 (Ubuntu) DAV/2 | Actualizar el servicio a una versión con soporte |
| HALL-004 | MEDIUM | web | Falta la cabecera Content-Security-Policy | http://127.0.0.***:20080/ | Agregarla: limita de dónde puede cargar código la página |
| HALL-005 | MEDIUM | web | Falta la cabecera X-Frame-Options | http://127.0.0.***:20080/ | Agregarla: impide que otra página la muestre dentro de un marco |
| HALL-006 | MEDIUM | web | Falta la cabecera X-Content-Type-Options | http://127.0.0.***:20080/ | Agregarla: evita que el navegador adivine el tipo de archivo |
| HALL-007 | LOW | scan | Puerto 20025: el servicio dice qué software usa | 220 &lt;b>correo.lab&lt;/b> ESMTP Postfix | Ocultar el producto y la versión en la configuración del servicio |
| HALL-008 | INFO | recon | localhost resuelve a 127.0.0.*** | 127.0.0.*** | Confirmar que todas las direcciones estén en el permiso |
| HALL-009 | INFO | scan | Puerto 20080 abierto sin banner | - | Revisarlo con un módulo específico (por ejemplo, web) |

## 4. Registro de auditoría

5 acción(es) registradas.
(código de salida: 0)
```

## Paso 5: reporte sin permiso

```bash
python3 -m toolkit.cli --auth no_existe.json report --salida sin_permiso.html
```

```text
================================================================
  TOOLKIT DE PRUEBAS AUTORIZADAS - solo con permiso escrito
================================================================
[DENEGADO] Archivo de autorización no encontrado: no_existe.json
(código de salida: 1)
```

## Paso 6: todas las pruebas

```bash
python3 -m pytest -v
```

```text
============================= test session starts ==============================
platform linux -- Python 3.14.8, pytest-9.1.1, pluggy-1.7.0
rootdir: pyhacklabcap8/solucion
configfile: pytest.ini
testpaths: toolkit/tests
plugins: typeguard-4.4.4
collected 34 items

toolkit/tests/test_auditoria.py .....                                    [ 14%]
toolkit/tests/test_autorizacion.py .............                         [ 52%]
toolkit/tests/test_cli.py ......                                         [ 70%]
toolkit/tests/test_escaner.py .....                                      [ 85%]
toolkit/tests/test_reporte.py .....                                      [100%]

============================== 34 passed in 1.23s ==============================
(código de salida: 0)
```

## Paso 7: validación

```bash
python3 validar.py /tmp/reportes/reporte_final.html
```

```text

7.1 Permiso y auditoría
  PASA  | Permiso vigente (2026-10-20 a 2026-11-19)
  PASA  | Auditoría registra recon
  PASA  | Auditoría registra scan
  PASA  | Auditoría registra web
  PASA  | Auditoría registra report
  PASA  | Auditoría registra una negación

7.2 Solo objetivos autorizados
  PASA  | recon sobre localhost
  PASA  | scan sobre 127.0.0.1
  PASA  | web sobre http://127.0.0.1:20080/

7.3 Hallazgos observados en el reporte
  PASA  | vsftpd 2.3.4
  PASA  | OpenSSH 4
  PASA  | Apache 2.2
  PASA  | Falta la cabecera X-Frame-Options
  PASA  | localhost resuelve a
  PASA  | Hallazgos numerados desde HALL-001

7.4 Escape del HTML
  PASA  | La etiqueta del banner aparece como texto
  PASA  | La etiqueta del banner no llega cruda

Resultado final: TODO PASA
(código de salida: 0)
```

## Control de cambios

| Versión | Fecha | Autor | Descripción del cambio |
|---|---|---|---|
| 1.0.0 | 2026-10-20 | Andrés García | Salidas reales de la ejecución completa del laboratorio. |
