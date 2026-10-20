"""
conftest.py - Preparación común de las pruebas. Ya viene listo.

pytest lee este archivo solo. La "fixture" de abajo se aplica a TODAS las pruebas
(autouse=True): cambia la carpeta de datos del toolkit por una carpeta temporal,
así las pruebas nunca escriben en su registro de auditoría real.
"""
import pytest


@pytest.fixture(autouse=True)
def datos_temporales(tmp_path, monkeypatch):
    monkeypatch.setenv("TOOLKIT_DATOS", str(tmp_path / "datos"))  # se deshace sola al terminar cada prueba
    return tmp_path / "datos"
