"""Pruebas de los módulos (Paso 3). Cada prueba levanta su propio servicio en 127.0.0.1. Ya vienen listas."""
import http.server
import socket
import socketserver
import threading

import pytest

from toolkit.modules import escaner


def _en_hilo(servidor):
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    return servidor.server_address[1]


@pytest.fixture
def puerto_con_banner():
    class Banner(socketserver.BaseRequestHandler):
        def handle(self):
            self.request.sendall(b"SSH-2.0-OpenSSH_4.7p1 Debian\r\n")
    servidor = socketserver.TCPServer(("127.0.0.1", 0), Banner)  # puerto 0: el sistema elige uno libre
    yield _en_hilo(servidor)
    servidor.shutdown()
    servidor.server_close()


@pytest.fixture
def puerto_cerrado():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]  # al salir del with se libera: queda cerrado


def test_banner_antiguo_es_high(puerto_con_banner):
    r = escaner.escanear("127.0.0.1", [puerto_con_banner], 1.0)
    assert r["hallazgos"][0]["severidad"] == "HIGH"
    assert "OpenSSH_4.7p1" in r["hallazgos"][0]["evidencia"]


def test_puerto_cerrado_no_produce_hallazgos(puerto_cerrado):
    r = escaner.escanear("127.0.0.1", [puerto_cerrado], 1.0)
    assert r["detalle"] == {puerto_cerrado: "cerrado"} and r["hallazgos"] == []


def test_version_moderna_es_low():
    assert escaner._por_version("Puerto 1", "SSH-2.0-OpenSSH_9.6")["severidad"] == "LOW"


def test_recon_de_localhost():
    assert "127.0.0.1" in escaner.reconocer("localhost")["detalle"]


def test_web_reporta_cabeceras_faltantes_y_version():
    class Web(http.server.BaseHTTPRequestHandler):
        def version_string(self):
            return "Apache/2.2.8"

        def do_GET(self):
            self.send_response(200)
            self.send_header("X-Frame-Options", "DENY")
            self.end_headers()

        def log_message(self, *args):
            pass
    servidor = http.server.HTTPServer(("127.0.0.1", 0), Web)
    puerto = _en_hilo(servidor)
    try:
        r = escaner.revisar_web(f"http://127.0.0.1:{puerto}/", 2.0)
    finally:
        servidor.shutdown()
        servidor.server_close()
    severidades = [h["severidad"] for h in r["hallazgos"]]
    assert severidades == ["HIGH", "MEDIUM", "MEDIUM"]  # Apache 2.2 y dos cabeceras faltantes
