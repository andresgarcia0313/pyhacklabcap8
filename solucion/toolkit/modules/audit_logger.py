"""
audit_logger.py - Registro de auditoría y evidencias del toolkit (Paso 2).

Piense en la minuta de la portería de un edificio: quién entró, a qué apartamento,
a qué hora y qué pasó. La auditoría es esa minuta: QUIÉN hizo QUÉ, CONTRA QUÉ
objetivo, CUÁNDO y con QUÉ resultado. También queda escrito lo que se negó.

Todo se guarda en toolkit/datos/. Esa ruta se calcula desde la ubicación de ESTE
archivo, no desde la carpeta en la que esté parada la terminal: ejecute el toolkit
desde donde lo ejecute, los datos quedan en el mismo lugar. La variable de entorno
TOOLKIT_DATOS cambia esa carpeta; las pruebas la usan para no mezclar sus datos con los suyos.

Archivos que se crean:
  datos/audit_AAAA-MM-DD.log  una línea por acción, un archivo por día
  datos/resultado_*.json      los hallazgos de cada módulo, que luego lee el reporte
"""
import datetime
import getpass            # getuser() dice qué usuario del sistema ejecuta el programa
import json
import logging            # el sistema de registros que trae Python
import os                 # os.getenv lee variables de entorno
import re                 # expresiones regulares: para leer de nuevo las líneas del registro
from pathlib import Path

PAQUETE = Path(__file__).resolve().parents[1]  # __file__ = este archivo; parents[1] sube a toolkit/
FORMATO = "%(asctime)s | %(levelname)-8s | %(message)s"  # fecha | nivel | mensaje
PATRON = re.compile(r"^(\S+ \S+) \| (\w+)\s*\| USUARIO=(\S+) \| ACCION=(\S+) \| "  # cada ( ) captura
                    r"OBJETIVO=(\S+) \| RESULTADO=(.*)$")  # un dato de la línea


def carpeta_datos() -> Path:
    """Carpeta de registros y resultados. La crea si no existe."""
    carpeta = Path(os.getenv("TOOLKIT_DATOS", PAQUETE / "datos"))  # la variable de entorno, o toolkit/datos
    carpeta.mkdir(parents=True, exist_ok=True)  # exist_ok=True: no falla si ya existe
    return carpeta


def configurar_logger() -> logging.Logger:
    """Prepara el registro de auditoría: cada mensaje va al archivo del día."""
    logger = logging.getLogger("toolkit")  # el mismo nombre devuelve siempre el mismo registro
    for manejador in list(logger.handlers):  # quita configuraciones anteriores, si las hay
        logger.removeHandler(manejador)
        manejador.close()  # cierra el archivo anterior
    logger.setLevel(logging.INFO)  # guarda INFO, WARNING y ERROR
    logger.propagate = False  # no repite los mensajes en la consola
    nombre = f"audit_{datetime.date.today().isoformat()}.log"  # audit_2026-10-20.log
    archivo = logging.FileHandler(carpeta_datos() / nombre, encoding="utf-8")  # el operador / une rutas
    archivo.setFormatter(logging.Formatter(FORMATO, datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(archivo)
    return logger


def _una_linea(texto) -> str:
    """Deja el texto en una sola línea: así nadie puede colar una línea falsa en el registro."""
    return " ".join(str(texto).split()) or "-"  # split() corta por espacios y saltos; join une con uno


def registrar(logger: logging.Logger, accion: str, objetivo: str, resultado,
              nivel: int = logging.INFO) -> None:  # nivel vale INFO si no se indica otro
    """Escribe una acción en el registro: usuario, acción, objetivo y resultado."""
    logger.log(nivel, "USUARIO=%s | ACCION=%s | OBJETIVO=%s | RESULTADO=%s",  # cada %s se llena en orden
               getpass.getuser(), _una_linea(accion),
               _una_linea(objetivo).replace(" ", "_"), _una_linea(resultado))  # objetivo sin espacios


def leer_auditoria() -> list[dict]:
    """Lee todas las líneas de los archivos audit_*.log y las devuelve como diccionarios."""
    entradas = []  # lista vacía que se va llenando
    for archivo in sorted(carpeta_datos().glob("audit_*.log")):  # glob busca archivos por patrón
        for linea in archivo.read_text(encoding="utf-8").splitlines():  # una línea a la vez
            m = PATRON.match(linea)  # m vale None si la línea no tiene el formato
            if m:  # m[1], m[2]... son los datos capturados por cada ( )
                entradas.append({"fecha": m[1], "nivel": m[2], "usuario": m[3],
                                 "accion": m[4], "objetivo": m[5], "resultado": m[6]})
    return entradas


def guardar_resultado(resultado: dict) -> Path:
    """Guarda en JSON lo que devolvió un módulo, con fecha y hora en el nombre."""
    marca = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # %f = microsegundos: nombres únicos
    ruta = carpeta_datos() / f"resultado_{resultado['modulo']}_{marca}.json"
    ruta.write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")  # indent: legible
    return ruta


def leer_resultados() -> list[dict]:
    """Devuelve todos los resultados guardados, del más antiguo al más reciente."""
    def fecha_del_nombre(archivo: Path) -> str:  # una función puede ir dentro de otra
        return archivo.name.split("_", 2)[2]  # "resultado_scan_20261020_..." -> "20261020_..."

    archivos = sorted(carpeta_datos().glob("resultado_*.json"), key=fecha_del_nombre)  # key: orden por fecha
    return [json.loads(a.read_text(encoding="utf-8")) for a in archivos]  # cada archivo -> diccionario
