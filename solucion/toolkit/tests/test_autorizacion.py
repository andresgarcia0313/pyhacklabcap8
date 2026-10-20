"""
test_autorizacion.py - Pruebas del control de autorización (Paso 6).

pytest busca solo los archivos test_*.py y, dentro de ellos, las funciones test_*.
Cada prueba prepara un caso, llama al código y comprueba el resultado con assert:
si lo que va después de assert es falso, la prueba falla y pytest muestra por qué.
"""
import datetime  # para calcular fechas relativas a hoy
import json

import pytest  # el programa de pruebas; aquí se usan pytest.raises y pytest.mark

from toolkit.modules.auth_manager import (AutorizacionError, cargar_autorizacion,
                                          huella_autorizacion, verificar_activo_autorizado)

HOY = datetime.date.today()
UN_DIA = datetime.timedelta(days=1)  # timedelta = una duración de tiempo
PERMISO = {"cliente": "Cliente de prueba", "contacto_autorizado": "Instructor", "identificador": "P-1",
           "activos_autorizados": ["127.0.0.1", "localhost", "192.0.2.0/24"],  # 192.0.2.x: red de documentación
           "fecha_inicio": (HOY - UN_DIA).isoformat(), "fecha_fin": (HOY + UN_DIA).isoformat(),
           "tipo_prueba": "caja_gris"}


def _archivo(tmp_path, **cambios) -> str:  # **cambios recibe pares nombre=valor
    """Escribe un permiso de prueba en una carpeta temporal y devuelve su ruta."""
    ruta = tmp_path / "authorization.json"  # tmp_path: carpeta temporal que pytest crea por prueba
    ruta.write_text(json.dumps({**PERMISO, **cambios}), encoding="utf-8")  # el permiso con los cambios
    return str(ruta)


def test_permiso_vigente_se_carga(tmp_path):
    assert cargar_autorizacion(_archivo(tmp_path))["cliente"] == "Cliente de prueba"


def test_archivo_inexistente_se_rechaza(tmp_path):
    with pytest.raises(AutorizacionError, match="no encontrado"):  # la prueba pasa SI ocurre ese error
        cargar_autorizacion(tmp_path / "no_existe.json")


def test_campo_vacio_se_rechaza(tmp_path):
    with pytest.raises(AutorizacionError, match="identificador"):
        cargar_autorizacion(_archivo(tmp_path, identificador=""))


def test_permiso_vencido_se_rechaza(tmp_path):
    with pytest.raises(AutorizacionError, match="vigencia"):
        cargar_autorizacion(_archivo(tmp_path, fecha_inicio="2020-01-01", fecha_fin="2020-12-31"))


def test_fecha_mal_escrita_se_rechaza(tmp_path):
    with pytest.raises(AutorizacionError, match="AAAA-MM-DD"):
        cargar_autorizacion(_archivo(tmp_path, fecha_fin="31/12/2030"))


@pytest.mark.parametrize("objetivo, esperado", [  # corre la prueba una vez por cada pareja de abajo
    ("127.0.0.1", True),     # IP listada
    ("127.0.0.10", False),   # empieza igual que 127.0.0.1, pero es otro equipo
    ("192.0.2.50", True),    # dentro de la red 192.0.2.0/24
    ("192.0.3.1", False),    # fuera de la red
    ("LOCALHOST", True),     # nombre listado, sin importar mayúsculas
    ("localhost.ejemplo.com", False),  # contiene "localhost", pero es otro nombre
])
def test_activos_autorizados(objetivo, esperado):
    assert verificar_activo_autorizado(objetivo, PERMISO) is esperado


def test_lista_vacia_no_autoriza_nada():
    assert verificar_activo_autorizado("127.0.0.1", {"activos_autorizados": []}) is False


def test_huella_cambia_si_cambia_el_permiso():
    assert huella_autorizacion(PERMISO) != huella_autorizacion({**PERMISO, "cliente": "Otro"})
