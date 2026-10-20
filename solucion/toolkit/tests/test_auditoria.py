"""Pruebas del registro de auditoría (Paso 2). Ya vienen listas."""
import logging

from toolkit.modules.audit_logger import (carpeta_datos, configurar_logger, guardar_resultado,
                                          leer_auditoria, leer_resultados, registrar)


def test_los_datos_van_a_la_carpeta_temporal(datos_temporales):
    assert carpeta_datos() == datos_temporales


def test_registra_y_lee_una_accion():
    registrar(configurar_logger(), "scan", "127.0.0.1", "2 hallazgo(s)")
    [entrada] = leer_auditoria()
    assert (entrada["accion"], entrada["objetivo"], entrada["nivel"]) == ("scan", "127.0.0.1", "INFO")


def test_un_salto_de_linea_no_crea_una_linea_falsa():
    registrar(configurar_logger(), "scan", "127.0.0.1", "ok\n2026-01-01 00:00:00 | INFO | USUARIO=x")
    assert len(leer_auditoria()) == 1


def test_lo_denegado_queda_como_warning():
    registrar(configurar_logger(), "scan", "192.0.2.10", "DENEGADO", logging.WARNING)
    assert leer_auditoria()[0]["nivel"] == "WARNING"


def test_guarda_y_lee_resultados_en_orden():
    guardar_resultado({"modulo": "scan", "objetivo": "127.0.0.1", "hallazgos": []})
    guardar_resultado({"modulo": "recon", "objetivo": "localhost", "hallazgos": []})
    assert [r["modulo"] for r in leer_resultados()] == ["scan", "recon"]
