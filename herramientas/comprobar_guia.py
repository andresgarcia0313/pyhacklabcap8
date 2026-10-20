#!/usr/bin/env python3
"""
comprobar_guia.py
Herramienta para el instructor: extrae de paso-a-paso/README.md el código que
el estudiante debe pegar, comprueba que es idéntico al de solucion/
y que cada archivo tiene como máximo 100 líneas de código sin contar comentarios.
Con --escribir DIR, además deja esos archivos en DIR (simula al estudiante).

Uso: python3 herramientas/comprobar_guia.py [--escribir DIR]
Sale con código 1 si la guía y la solución no coinciden.
"""
import argparse
import ast
import io
import pathlib
import re
import sys
import tokenize

RAIZ = pathlib.Path(__file__).resolve().parent.parent
GUIA = RAIZ / "paso-a-paso" / "README.md"
SOLUCION = RAIZ / "solucion"
ARCHIVOS = ["toolkit/modules/auth_manager.py", "toolkit/modules/audit_logger.py", "toolkit/modules/escaner.py",
            "toolkit/cli.py", "toolkit/modules/report_generator.py", "toolkit/templates/reporte.html",
            "toolkit/tests/test_autorizacion.py"]
MAX_LINEAS_CODIGO = 100  # sin contar comentarios, docstrings ni líneas en blanco
BLOQUE = re.compile(r"<!-- archivo: (\S+) -->\n```(?:python|html)\n(.*?)```\n", re.DOTALL)


def extraer() -> dict:
    """Devuelve {nombre de archivo: código} con cada bloque marcado de la guía."""
    return {nombre: codigo for nombre, codigo in BLOQUE.findall(GUIA.read_text(encoding="utf-8"))}


def lineas_de_codigo(fuente: str, nombre: str = ".py") -> int:
    """Cuenta las líneas con código real: excluye comentarios, docstrings y líneas en blanco."""
    if not nombre.endswith(".py"):  # plantilla HTML: cuenta las líneas que no están en blanco
        return sum(1 for linea in fuente.splitlines() if linea.strip())
    docstrings = set()
    for nodo in ast.walk(ast.parse(fuente)):
        tipos = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        if isinstance(nodo, tipos) and ast.get_docstring(nodo) is not None:
            docstrings.update(range(nodo.body[0].lineno, nodo.body[0].end_lineno + 1))
    ignorar = {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
               tokenize.DEDENT, tokenize.ENDMARKER}
    tokens = tokenize.generate_tokens(io.StringIO(fuente).readline)
    return len({t.start[0] for t in tokens if t.type not in ignorar} - docstrings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[2])
    parser.add_argument("--escribir", type=pathlib.Path, help="carpeta donde dejar los archivos extraídos")
    args = parser.parse_args()
    bloques, fallos = extraer(), 0
    for nombre in ARCHIVOS:
        if nombre not in bloques:
            print(f"FAIL | {nombre}: no está en la guía")
            fallos += 1
            continue
        solucion = (SOLUCION / nombre).read_text(encoding="utf-8")
        igual, codigo = bloques[nombre] == solucion, lineas_de_codigo(solucion, nombre)
        ok = igual and codigo <= MAX_LINEAS_CODIGO
        print(f"{'PASS' if ok else 'FAIL'} | {nombre}: {'idéntico' if igual else 'distinto'} a solucion/, "
              f"{codigo} líneas de código de {len(solucion.splitlines())} en total")
        fallos += not ok
        if args.escribir:
            (args.escribir / nombre).parent.mkdir(parents=True, exist_ok=True)
            (args.escribir / nombre).write_text(bloques[nombre], encoding="utf-8")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
