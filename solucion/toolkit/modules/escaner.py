"""
escaner.py - Los tres módulos de prueba del toolkit (Paso 3).

  reconocer(nombre)            resuelve un nombre a sus direcciones IP.
  escanear(host, puertos, t)   se conecta a cada puerto y lee su banner, como en el laboratorio 4.
  revisar_web(url, t)          pide la página y revisa sus cabeceras HTTP.

Los tres devuelven un diccionario con la misma forma:
  {"modulo": ..., "objetivo": ..., "detalle": ..., "hallazgos": [...]}
Cada hallazgo sale de lo que el módulo OBSERVÓ y trae su evidencia. Nada se inventa.
Este archivo no revisa permisos: eso lo hace la CLI (Paso 4) antes de llamarlo.

Siglas: TCP (Transmission Control Protocol, protocolo de control de transmisión),
HTTP (Hypertext Transfer Protocol, protocolo de transferencia de hipertexto),
URL (Uniform Resource Locator, dirección de una página) y CVE (Common
Vulnerabilities and Exposures, identificador público de una vulnerabilidad).
"""
import socket            # conexiones de red de bajo nivel
import urllib.error      # los errores que puede devolver una petición web
import urllib.request    # peticiones HTTP con la librería que trae Python

VERSIONES_ANTIGUAS = {  # diccionario: texto que delata una versión antigua -> por qué es un riesgo
    "vsFTPd 2.3.4": "vsftpd 2.3.4 tiene una puerta trasera pública (CVE-2011-2523)",
    "OpenSSH_4.": "OpenSSH 4 está sin soporte desde hace más de quince años",
    "Apache/2.2": "Apache 2.2 terminó su soporte en 2017",
}
CABECERAS_SEGURIDAD = {  # cabeceras que protegen a quien visita la página -> para qué sirven
    "Content-Security-Policy": "limita de dónde puede cargar código la página",
    "X-Frame-Options": "impide que otra página la muestre dentro de un marco",
    "X-Content-Type-Options": "evita que el navegador adivine el tipo de archivo",
}


def hallazgo(severidad: str, descripcion: str, recomendacion: str, evidencia: str) -> dict:
    """Arma un hallazgo con los cuatro datos que pide un reporte."""
    return {"severidad": severidad, "descripcion": descripcion,
            "recomendacion": recomendacion, "evidencia": evidencia}


def _por_version(donde: str, texto: str) -> dict:
    """Clasifica un texto que revela software: HIGH si es una versión antigua, LOW si no."""
    for antigua, motivo in VERSIONES_ANTIGUAS.items():  # .items() entrega pares (clave, valor)
        if antigua in texto:  # ¿el texto contiene la versión antigua?
            return hallazgo("HIGH", f"{donde}: versión antigua expuesta. {motivo}",
                            "Actualizar el servicio a una versión con soporte", texto)
    return hallazgo("LOW", f"{donde}: el servicio dice qué software usa",
                    "Ocultar el producto y la versión en la configuración del servicio", texto)


def reconocer(nombre: str) -> dict:
    """Resuelve un nombre (por ejemplo, localhost) a sus direcciones IPv4."""
    respuestas = socket.getaddrinfo(nombre, None, socket.AF_INET)  # pregunta al sistema; AF_INET = IPv4
    ips = sorted({r[4][0] for r in respuestas})  # { } sin repetidos; r[4][0] es la IP de cada respuesta
    encontrado = hallazgo("INFO", f"{nombre} resuelve a {', '.join(ips)}",
                          "Confirmar que todas las direcciones estén en el permiso", ", ".join(ips))
    return {"modulo": "recon", "objetivo": nombre, "detalle": ips, "hallazgos": [encontrado]}


def leer_banner(host: str, puerto: int, timeout: float) -> str | None:
    """Devuelve el banner, "" si el puerto está abierto pero callado, o None si está cerrado."""
    try:
        with socket.create_connection((host, puerto), timeout=timeout) as conexion:  # with cierra solo
            try:
                return conexion.recv(1024).decode("utf-8", errors="replace").strip()  # bytes -> texto
            except TimeoutError:  # se conectó, pero el servicio no dijo nada a tiempo
                return ""
    except OSError:  # conexión rechazada: puerto cerrado
        return None


def escanear(host: str, puertos: list[int], timeout: float) -> dict:
    """Lee el banner de cada puerto y convierte lo observado en hallazgos."""
    detalle, hallazgos = {}, []  # dos variables en una línea: diccionario vacío y lista vacía
    for puerto in puertos:
        banner = leer_banner(host, puerto, timeout)
        if banner is None:  # "is None" pregunta si no hay nada
            detalle[puerto] = "cerrado"
        elif banner == "":  # elif = "si no, y si..."
            detalle[puerto] = "abierto, sin banner"
            hallazgos.append(hallazgo("INFO", f"Puerto {puerto} abierto sin banner",
                                      "Revisarlo con un módulo específico (por ejemplo, web)", "-"))
        else:  # hay banner: se clasifica
            detalle[puerto] = banner
            hallazgos.append(_por_version(f"Puerto {puerto}", banner))
    return {"modulo": "scan", "objetivo": host, "detalle": detalle, "hallazgos": hallazgos}


def revisar_web(url: str, timeout: float) -> dict:
    """Pide la URL y revisa las cabeceras de seguridad y la cabecera Server."""
    navegador = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # {} = sin proxy: va directo
    pedido = urllib.request.Request(url, headers={"User-Agent": "toolkit-lab08 (prueba autorizada)"})
    try:
        with navegador.open(pedido, timeout=timeout) as respuesta:  # hace la petición GET
            estado, cabeceras = respuesta.status, respuesta.headers  # 200 y las cabeceras recibidas
    except urllib.error.HTTPError as error:  # 404, 500...: la respuesta también trae cabeceras
        estado, cabeceras = error.code, error.headers
    hallazgos = [hallazgo("MEDIUM", f"Falta la cabecera {nombre}", f"Agregarla: {uso}", url)
                 for nombre, uso in CABECERAS_SEGURIDAD.items() if nombre not in cabeceras]  # solo faltantes
    servidor = cabeceras.get("Server", "")  # .get devuelve "" si la cabecera no existe
    if any(c.isdigit() for c in servidor):  # ¿algún carácter es un dígito? entonces muestra versión
        hallazgos.insert(0, _por_version("Cabecera Server", servidor))  # insert(0, ...) lo pone de primero
    return {"modulo": "web", "objetivo": url, "detalle": {"estado": estado, "server": servidor},
            "hallazgos": hallazgos}
