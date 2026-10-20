"""Pruebas del reporte (Paso 5). Ya vienen listas."""
from toolkit.modules.audit_logger import guardar_resultado
from toolkit.modules.escaner import hallazgo
from toolkit.modules.report_generator import generar_reporte, ofuscar

AUTH = {"cliente": "Cliente de prueba", "identificador": "P-1", "tipo_prueba": "caja_gris",
        "fecha_inicio": "2026-01-01", "fecha_fin": "2026-12-31"}


def _guardar(*hallazgos):
    guardar_resultado({"modulo": "scan", "objetivo": "127.0.0.1", "hallazgos": list(hallazgos)})


def test_oculta_ultimo_octeto_y_contrasenas():
    assert ofuscar("192.168.56.101 password=secreto") == "192.168.56.*** password=*****"


def test_sin_modulos_no_hay_hallazgos_inventados(tmp_path):
    salida = tmp_path / "r.html"
    assert generar_reporte(AUTH, "html", salida) == 0
    texto = salida.read_text(encoding="utf-8")
    assert "Sin hallazgos" in texto and "HALL-001" not in texto


def test_hallazgos_reales_ordenados_por_gravedad(tmp_path):
    _guardar(hallazgo("LOW", "banner visible", "ocultar", "x"), hallazgo("HIGH", "versión antigua", "actualizar", "y"))
    salida = tmp_path / "r.md"
    assert generar_reporte(AUTH, "markdown", salida) == 2
    texto = salida.read_text(encoding="utf-8")
    assert texto.index("HALL-001 | HIGH") < texto.index("HALL-002 | LOW")


def test_repetir_un_escaneo_no_duplica_hallazgos(tmp_path):
    _guardar(hallazgo("HIGH", "versión antigua", "actualizar", "y"))
    _guardar(hallazgo("HIGH", "versión antigua", "actualizar", "y"))
    assert generar_reporte(AUTH, "markdown", tmp_path / "r.md") == 1


def test_banner_con_html_se_escapa(tmp_path):
    _guardar(hallazgo("LOW", "banner", "ocultar", "220 <b>texto</b>"))
    salida = tmp_path / "r.html"
    generar_reporte(AUTH, "html", salida)
    texto = salida.read_text(encoding="utf-8")
    assert "<b>texto</b>" not in texto and "&lt;b&gt;texto&lt;/b&gt;" in texto
