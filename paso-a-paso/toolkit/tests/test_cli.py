"""Pruebas de la CLI completa (Paso 4). No abren conexiones a otros equipos. Ya vienen listas."""
import datetime
import json

import pytest

from toolkit.cli import main
from toolkit.modules.audit_logger import leer_auditoria


@pytest.fixture
def permiso(tmp_path):
    hoy = datetime.date.today()
    datos = {"cliente": "Cliente de prueba", "contacto_autorizado": "Instructor", "identificador": "P-1",
             "activos_autorizados": ["127.0.0.1", "localhost"], "tipo_prueba": "caja_gris",
             "fecha_inicio": hoy.isoformat(), "fecha_fin": (hoy + datetime.timedelta(days=1)).isoformat()}
    ruta = tmp_path / "authorization.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    return str(ruta)


@pytest.mark.parametrize("objetivo", ["192.0.2.10", "127.0.0.10", "ejemplo.com"])
def test_objetivo_no_autorizado_sale_con_1_y_queda_registrado(permiso, objetivo):
    assert main(["--auth", permiso, "scan", objetivo]) == 1
    assert leer_auditoria()[-1]["resultado"].startswith("DENEGADO")


def test_url_de_equipo_no_autorizado_se_niega(permiso):
    assert main(["--auth", permiso, "web", "http://192.0.2.10/"]) == 1


def test_sin_permiso_no_hay_reporte(tmp_path):
    salida = tmp_path / "r.html"
    assert main(["--auth", str(tmp_path / "no_existe.json"), "report", "--salida", str(salida)]) == 1
    assert not salida.exists()


def test_recon_autorizado_guarda_resultado(permiso):
    assert main(["--auth", permiso, "recon", "localhost"]) == 0
    assert "1 hallazgo(s)" in leer_auditoria()[-1]["resultado"]
