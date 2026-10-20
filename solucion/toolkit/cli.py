"""
cli.py - Interfaz de línea de comandos (CLI) del toolkit (Paso 4).

CLI (Command Line Interface, interfaz de línea de comandos): el programa se
maneja escribiendo órdenes en la terminal, por ejemplo:
    python3 -m toolkit.cli scan 127.0.0.1 --puertos 20021,20022

Cada orden sigue el mismo camino, sin atajos:
    permiso válido -> objetivo autorizado -> módulo -> evidencia -> auditoría
Si algo falla, el programa se detiene, lo deja en el registro y sale con código 1.

El PARSER (analizador) es la pieza de argparse que lee lo que usted escribió y lo
separa en partes: la orden (scan), el objetivo (127.0.0.1) y las opciones (--puertos).
"""
import argparse  # lee las opciones escritas en la terminal y genera la ayuda (--help)
import ipaddress
import logging
import os        # os.path.relpath acorta una ruta para mostrarla
import socket
from pathlib import Path
from urllib.parse import urlsplit  # separa una URL en partes: esquema, equipo, puerto...

from toolkit.modules import escaner  # módulos del Paso 3 (archivo toolkit/modules/escaner.py)
from toolkit.modules.audit_logger import configurar_logger, guardar_resultado, registrar  # Paso 2
from toolkit.modules.auth_manager import (AutorizacionError, cargar_autorizacion,  # Paso 1
                                          huella_autorizacion, verificar_activo_autorizado)


def _puertos(texto: str) -> list[int]:
    """Convierte "20021,20022" en [20021, 20022] y rechaza valores fuera de 1-65535."""
    puertos = [int(p) for p in texto.split(",")]  # "cada trozo p, convertido en número"; int() falla si no lo es
    if not all(1 <= p <= 65535 for p in puertos):  # all: ¿TODOS los puertos están entre 1 y 65535?
        raise argparse.ArgumentTypeError("los puertos van de 1 a 65535")
    return puertos


def _exigir_activo(objetivo: str, auth: dict) -> None:
    """Detiene todo si el objetivo no está en el permiso o si sale del propio equipo."""
    if not verificar_activo_autorizado(objetivo, auth):
        raise AutorizacionError(f"El objetivo '{objetivo}' NO está en los activos autorizados")
    ip = ipaddress.ip_address(socket.gethostbyname(objetivo))  # nombre -> IP ("localhost" -> 127.0.0.1)
    if not ip.is_loopback:  # barrera extra del laboratorio: solo 127.x.x.x, su propio equipo
        raise AutorizacionError(f"'{objetivo}' es {ip}: el laboratorio solo trabaja en 127.0.0.0/8")


def ejecutar_modulo(args: argparse.Namespace, auth: dict) -> dict:
    """Comprueba el objetivo y llama al módulo pedido."""
    if args.comando == "web":
        url = urlsplit(args.objetivo)
        if url.scheme not in ("http", "https"):
            raise AutorizacionError("La URL debe empezar por http:// o https://")
        _exigir_activo(url.hostname or "", auth)  # se revisa el equipo de la URL; "or" da "" si no hay equipo
        return escaner.revisar_web(args.objetivo, args.timeout)
    _exigir_activo(args.objetivo, auth)
    if args.comando == "recon":
        return escaner.reconocer(args.objetivo)
    return escaner.escanear(args.objetivo, args.puertos, args.timeout)


def construir_parser() -> argparse.ArgumentParser:
    """Define las órdenes (subcomandos) y sus opciones."""
    parser = argparse.ArgumentParser(prog="toolkit", description="Toolkit de pruebas de "
                                     "seguridad autorizadas. Solo con permiso escrito.")
    parser.add_argument("--auth", default="authorization.json", help="archivo de autorización")
    sub = parser.add_subparsers(dest="comando", metavar="MODULO", required=True)  # dest: dónde queda la orden
    # metavar: nombre que muestra la ayuda; required=True: sin orden no arranca
    recon = sub.add_parser("recon", help="resolver un nombre a sus direcciones IP")
    recon.add_argument("objetivo", help="nombre o IP, por ejemplo localhost")
    scan = sub.add_parser("scan", help="leer los banners (saludos) de puertos TCP")
    scan.add_argument("objetivo", help="IP o nombre, por ejemplo 127.0.0.1")
    scan.add_argument("--puertos", type=_puertos, default="20021,20022,20023,20025,20080",
                      help="puertos separados por comas")
    web = sub.add_parser("web", help="revisar las cabeceras de seguridad de una página")
    web.add_argument("objetivo", metavar="url", help="por ejemplo http://127.0.0.1:20080/")
    for orden in (scan, web):  # las dos órdenes que se conectan aceptan --timeout
        orden.add_argument("--timeout", type=float, default=1.0, help="segundos de espera por conexión")
    report = sub.add_parser("report", help="generar el reporte con los hallazgos guardados")
    report.add_argument("--formato", choices=["html", "markdown"], default="html", help="html o markdown")
    report.add_argument("--salida", type=Path, default=Path("reporte_final.html"), help="archivo del reporte")
    return parser


def main(argv: list[str] | None = None) -> int:  # argv: las palabras de la orden; None = las de la terminal
    """Punto de entrada: devuelve 0 si todo salió bien y 1 si se negó o falló."""
    args = construir_parser().parse_args(argv)
    logger = configurar_logger()
    objetivo = getattr(args, "objetivo", "N/A")  # getattr: el objetivo si existe; "N/A" en report, que no tiene
    print("=" * 64 + "\n  TOOLKIT DE PRUEBAS AUTORIZADAS - solo con permiso escrito\n" + "=" * 64)  # "=" * 64 repite el signo 64 veces; "\n" = salto de línea
    try:
        auth = cargar_autorizacion(args.auth)  # sin permiso válido no se hace NADA, ni el reporte
        print(f"[AUTH] Cliente: {auth['cliente']} | Huella: {huella_autorizacion(auth)}")
        if args.comando == "report":
            from toolkit.modules.report_generator import generar_reporte  # solo report usa Jinja2
            total = generar_reporte(auth, args.formato, args.salida)
            registrar(logger, "report", "N/A", f"formato={args.formato} hallazgos={total}")
            print(f"[OK] Reporte con {total} hallazgo(s) en: {args.salida}")
            return 0
        resultado = ejecutar_modulo(args, auth)
    except AutorizacionError as error:  # permiso ausente, vencido u objetivo no autorizado
        registrar(logger, args.comando, objetivo, f"DENEGADO: {error}", logging.WARNING)  # WARNING: advertencia
        print(f"[DENEGADO] {error}")
        return 1
    except OSError as error:  # fallas de red o de archivos: el destino no responde, etc.
        registrar(logger, args.comando, objetivo, f"ERROR: {error}", logging.ERROR)
        print(f"[ERROR] {error}")
        return 1
    ruta = guardar_resultado(resultado)
    registrar(logger, args.comando, objetivo, f"{len(resultado['hallazgos'])} hallazgo(s) en {ruta.name}")
    for h in resultado["hallazgos"]:
        print(f"  [{h['severidad']:<6}] {h['descripcion']}")  # :<6 rellena a 6 espacios para alinear
    print(f"[OK] {len(resultado['hallazgos'])} hallazgo(s) guardados en {os.path.relpath(ruta)}")  # ruta corta
    return 0


if __name__ == "__main__":  # __name__ vale "__main__" solo cuando este archivo se ejecuta directamente
    raise SystemExit(main())  # entrega al sistema el código de salida 0 o 1
