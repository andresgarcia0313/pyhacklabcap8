"""
auth_manager.py - Control de autorización del toolkit (Paso 1).

Este texto entre tres comillas es un DOCSTRING: una nota para quien lee. Python no la ejecuta.

Un cerrajero serio no abre una puerta sin ver antes la orden del dueño. Aquí pasa
lo mismo: nada se prueba sin permiso escrito. El permiso vive en authorization.json
y este módulo lo revisa ANTES de cualquier conexión:
  1. que el archivo exista y sea JSON válido;
  2. que traiga todos los campos obligatorios;
  3. que hoy esté dentro de las fechas de vigencia;
  4. que el objetivo esté en la lista de activos autorizados.

Siglas: JSON (JavaScript Object Notation, formato de texto para datos), IP (Internet
Protocol, dirección de un equipo en la red), CIDR (Classless Inter-Domain Routing,
forma de escribir una red, como 192.0.2.0/24) y SHA-256 (Secure Hash Algorithm,
cálculo que saca una huella digital de un texto).
"""
import datetime           # fechas: qué día es hoy y cómo leer "2026-10-20"
import hashlib            # huellas digitales (hash) de un texto
import ipaddress          # entiende IP y redes; las compara como números, no como texto
import json               # lee y escribe archivos JSON
from pathlib import Path  # Path representa la ruta de un archivo

CAMPOS_REQUERIDOS = ["cliente", "contacto_autorizado", "identificador",  # lista: campos obligatorios
                     "activos_autorizados", "fecha_inicio", "fecha_fin", "tipo_prueba"]
# "identificador" es el número del permiso firmado en papel o en PDF. Este JSON no es una firma.


class AutorizacionError(Exception):  # un tipo de ERROR propio; hereda de Exception, la base de los errores
    """Error que detiene el toolkit cuando no hay un permiso válido."""


def cargar_autorizacion(ruta: str | Path) -> dict:  # str | Path: acepta un texto O una ruta; -> dict: devuelve un diccionario
    """Lee el archivo de autorización y comprueba campos y vigencia. Devuelve sus datos."""
    ruta = Path(ruta)  # texto -> ruta, para poder preguntarle si existe
    if not ruta.exists():  # sin archivo no hay permiso
        raise AutorizacionError(f"Archivo de autorización no encontrado: {ruta}")  # f"...{ruta}": la f mete el valor de ruta en el texto
    try:  # try: intente esto; si ocurre el error de "except", atiéndalo allá
        datos = json.loads(ruta.read_text(encoding="utf-8"))  # texto JSON -> diccionario de Python
    except json.JSONDecodeError as error:  # el archivo no es JSON válido (falta una coma, una comilla...)
        raise AutorizacionError(f"{ruta} no es un JSON válido: {error}") from error  # from error: conserva la causa original
    faltantes = [c for c in CAMPOS_REQUERIDOS if not datos.get(c)]  # se lee: "cada campo c de la lista, si viene vacío o no está"
    if faltantes:  # una lista con elementos cuenta como verdadera
        raise AutorizacionError("Campos obligatorios faltantes: " + ", ".join(faltantes))  # join une la lista con comas
    try:
        inicio = datetime.date.fromisoformat(datos["fecha_inicio"])  # "2026-10-20" -> fecha
        fin = datetime.date.fromisoformat(datos["fecha_fin"])  # falla si no viene como AAAA-MM-DD
    except ValueError:
        raise AutorizacionError("Fechas con formato inválido: use AAAA-MM-DD "
                                "o ejecute python3 preparar_autorizacion.py") from None  # from None: muestra solo este mensaje
    hoy = datetime.date.today()  # la fecha de su computador
    if not inicio <= hoy <= fin:  # se lee: "hoy está entre inicio y fin"
        raise AutorizacionError(f"Autorización fuera de vigencia ({inicio} a {fin}). Hoy: {hoy}")
    return datos  # todo en orden: entrega el permiso


def _como_ip(texto: str):  # el guion bajo inicial indica "uso interno de este archivo"
    """Devuelve la IP si el texto es una dirección, o None si es un nombre como 'localhost'."""
    try:
        return ipaddress.ip_address(texto)  # "127.0.0.1" -> dirección IP
    except ValueError:  # no es una IP: es un nombre
        return None  # None significa "nada"


def verificar_activo_autorizado(objetivo: str, autorizacion: dict) -> bool:
    """Indica si el objetivo está autorizado: IP dentro de una red listada o nombre idéntico.

    "127.0.0.10" empieza con el mismo texto que "127.0.0.1", pero es otro equipo.
    Por eso no se compara como texto: ipaddress compara las direcciones como números.
    """
    ip = _como_ip(objetivo)
    for activo in autorizacion.get("activos_autorizados", []):  # recorre cada activo del permiso
        if ip is None:  # el objetivo es un nombre: debe coincidir completo
            if objetivo.lower() == activo.lower():  # .lower() pasa a minúsculas antes de comparar
                return True  # return termina la función y entrega el resultado
            continue  # continue salta al siguiente activo
        try:
            red = ipaddress.ip_network(activo, strict=False)  # "127.0.0.1" = un equipo; "x/24" = una red
        except ValueError:  # este activo es un nombre: no aplica a una IP
            continue
        if ip in red:  # "in" pregunta si la IP pertenece a la red, calculado con números
            return True
    return False  # ningún activo coincidió


def huella_autorizacion(autorizacion: dict) -> str:
    """Huella corta (SHA-256) del permiso: si alguien cambia el archivo, la huella cambia."""
    contenido = json.dumps(autorizacion, sort_keys=True, ensure_ascii=False)  # mismo contenido, mismo texto
    huella = hashlib.sha256(contenido.encode("utf-8"))  # encode: texto -> bytes, que es lo que sha256 sabe leer
    return huella.hexdigest()[:16]  # hexdigest: la huella en letras y números; [:16] = los primeros 16
