#!/usr/bin/env python3
"""
simulador_servicios.py - Servicios de práctica en su propio equipo (127.0.0.1). Ya viene listo.

Publica los banners de una máquina de práctica con software antiguo. Solo envía
textos: no hay ningún servicio vulnerable de verdad, y nada sale de su computador.

  20021  FTP   (File Transfer Protocol)    220 (vsFTPd 2.3.4)
  20022  SSH   (Secure Shell)              SSH-2.0-OpenSSH_4.7p1 Debian-8ubuntu1
  20025  SMTP  (Simple Mail Transfer)      un saludo con etiquetas HTML, para probar el reporte
  20080  HTTP  (web)                       Server: Apache/2.2.8, sin cabeceras de seguridad
  20023  queda CERRADO a propósito.

Uso: python3 simulador_servicios.py      (Ctrl+C para detenerlo)
"""
import http.server
import socketserver
import threading

HOST = "127.0.0.1"  # solo su equipo
BANNERS = {
    20021: b"220 (vsFTPd 2.3.4)\r\n",
    20022: b"SSH-2.0-OpenSSH_4.7p1 Debian-8ubuntu1\r\n",
    20025: b"220 <b>correo.lab</b> ESMTP Postfix\r\n",
}
PUERTO_WEB = 20080


class Banner(socketserver.BaseRequestHandler):
    """Envía el banner del puerto y cierra la conexión."""

    def handle(self):
        self.request.sendall(BANNERS[self.server.server_address[1]])


class Web(http.server.BaseHTTPRequestHandler):
    """Página web antigua: muestra su versión y no envía cabeceras de seguridad."""

    def version_string(self):
        return "Apache/2.2.8 (Ubuntu) DAV/2"

    def do_GET(self):
        cuerpo = "<html><body><h1>Intranet de pruebas</h1></body></html>".encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def log_message(self, *args):  # sin mensajes por cada visita
        pass


class Servidor(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def iniciar() -> list:
    servidores = [Servidor((HOST, p), Banner) for p in BANNERS]
    servidores.append(http.server.ThreadingHTTPServer((HOST, PUERTO_WEB), Web))
    for s in servidores:
        threading.Thread(target=s.serve_forever, daemon=True).start()
    return servidores


if __name__ == "__main__":
    activos = iniciar()
    print(f"[+] Simulador escuchando en {HOST}: puertos {', '.join(str(p) for p in [*BANNERS, PUERTO_WEB])}", flush=True)
    print("    Ctrl+C para detenerlo", flush=True)
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("\n[+] Simulador detenido")
    finally:
        for s in activos:
            s.shutdown()
            s.server_close()
