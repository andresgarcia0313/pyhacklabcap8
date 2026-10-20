<!-- Idioma del documento: es-CO (español de Colombia) -->
# Laboratorio 8: toolkit de pruebas de seguridad autorizadas

Curso Seguridad informática con Python, capítulo 8: integración y entrega de un toolkit ético.

En este laboratorio usted junta en un solo programa lo que construyó en los capítulos anteriores, como la lectura de banners del [laboratorio 4](https://github.com/andresgarcia0313/pyhacklabcap4). El resultado es una CLI (Command Line Interface, interfaz de línea de comandos) que:

- **se niega a trabajar sin permiso escrito y vigente**, y compara cada objetivo con las direcciones autorizadas;
- **deja constancia** de cada acción, permitida o negada, en un registro de auditoría;
- ejecuta tres módulos (`recon`, `scan` y `web`) que producen **hallazgos con evidencia**;
- genera un **reporte HTML o Markdown** solo con lo que los módulos observaron;
- viene con **34 pruebas automáticas** con pytest.

Todo ocurre **en su propio equipo, sin máquinas virtuales**. Un simulador incluido publica en `127.0.0.1` servicios con software antiguo, y el toolkit solo acepta direcciones de su propio equipo: ningún paquete sale de su computador.

## Dos lados: la práctica y la respuesta

| Carpeta | Qué contiene | Quién la usa |
|---|---|---|
| [`paso-a-paso/`](paso-a-paso/) | **La práctica.** La guía [`paso-a-paso/README.md`](paso-a-paso/README.md) y el material de apoyo (simulador, permiso de ejemplo, comprobaciones por paso, pruebas y validación). Usted crea los siete archivos del toolkit pegando el código de la guía, comentado línea a línea. | Estudiante |
| [`solucion/`](solucion/) | **La respuesta.** Los siete archivos terminados y el laboratorio completo funcionando, con sus salidas reales en [`solucion/output.md`](solucion/output.md). | Estudiante que quiera comparar, e instructor |

Recomendación: haga primero la práctica y abra la solución solo para comparar cuando algo no le funcione (`diff toolkit/cli.py ../solucion/toolkit/cli.py`).

## Empezar

```bash
git clone https://github.com/andresgarcia0313/pyhacklabcap8.git
cd pyhacklabcap8/paso-a-paso
```

Luego abra [`paso-a-paso/README.md`](paso-a-paso/README.md) y siga el Paso 0.

¿Solo quiere ver el toolkit funcionando? Desde la carpeta `pyhacklabcap8`, ejecute la solución:

```bash
cd solucion
./ejecutar_laboratorio.sh
```

## Qué va a aprender

1. Validar un permiso escrito (campos, vigencia y activos) antes de cualquier conexión.
2. Comparar direcciones y redes con `ipaddress`, nunca como texto.
3. Registrar cada acción con `logging` en un archivo que no se puede adulterar con saltos de línea.
4. Unir varios módulos detrás de una CLI con `argparse` y códigos de salida.
5. Generar reportes con Jinja2, con el HTML escapado y los datos sensibles ocultos.
6. Escribir pruebas con pytest, incluidas pruebas con varios casos y pruebas de errores.

No necesita ser experto en Python: la guía y los comentarios del código lo explican. Requisitos: Python 3.10 o superior en Linux, macOS o Windows con WSL (Windows Subsystem for Linux, subsistema de Linux para Windows).

## Para el instructor

- `./comprobar_repositorio.sh`: verifica que el material de apoyo sea igual en ambas carpetas y que el código de la guía sea idéntico al de la solución. Además ejecuta el laboratorio completo dos veces, con la solución y con el código copiado de la guía, como lo haría un estudiante. Debe terminar en `REPOSITORIO CORRECTO`.
- `herramientas/comprobar_guia.py`: la parte de esa verificación que compara la guía con la solución y cuenta las líneas de código de cada archivo.

## Uso responsable

Use este toolkit solo sobre sistemas con autorización escrita y vigente. El permiso del laboratorio autoriza solo `127.0.0.1` y `localhost`, y la CLI rechaza cualquier dirección fuera de `127.0.0.0/8`.

## Control de cambios

| Versión | Fecha | Autor | Descripción del cambio |
|---|---|---|---|
| 1.0.0 | 2026-10-20 | Andrés García | Laboratorio 8 en ejecución local: permiso con comparación de redes, auditoría, tres módulos con hallazgos observados, reporte escapado, 34 pruebas, guía paso a paso y solución. |
