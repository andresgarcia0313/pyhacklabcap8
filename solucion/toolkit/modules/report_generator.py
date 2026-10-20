"""
report_generator.py - Reporte final en HTML o Markdown (Paso 5).

Junta tres cosas: los datos del permiso, el registro de auditoría y los
hallazgos que guardaron los módulos. Solo reporta lo que los módulos
observaron: si no se ha ejecutado ningún módulo, la sección de hallazgos
queda vacía y lo dice.

Jinja2 es una librería de PLANTILLAS: un HTML con huecos {{ variable }} que se
llenan con datos. Con autoescape=True, Jinja2 convierte < y > en &lt; y &gt;,
así un banner con etiquetas HTML se MUESTRA como texto y no se ejecuta en el
navegador de quien abra el reporte.

Siglas: HTML (HyperText Markup Language, lenguaje de las páginas web).
"""
import datetime
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader  # se instala con requirements.txt

from toolkit.modules.audit_logger import leer_auditoria, leer_resultados
from toolkit.modules.auth_manager import huella_autorizacion

PLANTILLAS = Path(__file__).resolve().parents[1] / "templates"  # toolkit/templates/
ORDEN = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]  # de más grave a menos grave


def ofuscar(texto: str) -> str:
    """Oculta datos sensibles: el último número de cada IP y el valor de las contraseñas."""
    texto = re.sub(r"\b(\d{1,3}\.\d{1,3}\.\d{1,3})\.\d{1,3}\b", r"\1.***", texto)  # \1 = lo del grupo ( )
    return re.sub(r"(password|passwd|pwd|clave)=\S+", r"\1=*****", texto, flags=re.IGNORECASE)


def recopilar_hallazgos() -> list[dict]:
    """Une los hallazgos de todos los resultados, sin repetidos, del más grave al menos grave."""
    unicos = {}  # diccionario: (módulo, objetivo, descripción) -> hallazgo; el más reciente reemplaza
    for resultado in leer_resultados():
        for h in resultado["hallazgos"]:
            clave = (resultado["modulo"], resultado["objetivo"], h["descripcion"])  # repetido = misma clave
            unicos[clave] = {**h, "modulo": resultado["modulo"],  # ** copia todos los campos de h
                             "descripcion": ofuscar(h["descripcion"]), "evidencia": ofuscar(h["evidencia"])}

    def gravedad(h: dict) -> int:  # posición de la severidad en ORDEN: 0 = la más grave
        return ORDEN.index(h["severidad"])

    hallazgos = sorted(unicos.values(), key=gravedad)  # sorted ordena; key dice con qué criterio
    for numero, h in enumerate(hallazgos, start=1):  # enumerate numera: 1, 2, 3...
        h["id"] = f"HALL-{numero:03d}"  # :03d rellena con ceros: HALL-001
    return hallazgos


def generar_reporte(auth: dict, formato: str, salida: Path) -> int:
    """Escribe el reporte y devuelve cuántos hallazgos incluyó."""
    hallazgos = recopilar_hallazgos()
    auditoria = [{**e, "objetivo": ofuscar(e["objetivo"]), "resultado": ofuscar(e["resultado"])}
                 for e in leer_auditoria()]
    contexto = {
        "proyecto": {"cliente": auth["cliente"], "identificador": auth["identificador"],
                     "tipo_prueba": auth["tipo_prueba"],
                     "vigencia": f"{auth['fecha_inicio']} a {auth['fecha_fin']}",
                     "huella": huella_autorizacion(auth),
                     "generado": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
        "resumen": {sev: sum(h["severidad"] == sev for h in hallazgos) for sev in ORDEN},
        "auditoria": auditoria,
        "hallazgos": hallazgos,
    }
    if formato == "html":
        entorno = Environment(loader=FileSystemLoader(PLANTILLAS), autoescape=True)  # escapa SIEMPRE < y >
        texto = entorno.get_template("reporte.html").render(**contexto)  # ** pasa cada clave como variable
    else:
        texto = _markdown(contexto)
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(texto, encoding="utf-8")
    return len(hallazgos)


def _celda(texto) -> str:
    """Prepara un texto para una tabla Markdown: escapa | y <, y lo deja en una línea."""
    return " ".join(str(texto).split()).replace("|", "\\|").replace("<", "&lt;")


def _markdown(ctx: dict) -> str:
    """Arma el mismo reporte en Markdown, un formato de texto que GitHub muestra con estilo."""
    p = ctx["proyecto"]
    lineas = ["# Reporte de pruebas de seguridad autorizadas", "",
              f"Confidencial. Generado el {p['generado']}.", "", "## 1. Proyecto", "",
              f"- Cliente: {p['cliente']}", f"- Identificador del permiso: {p['identificador']}",
              f"- Tipo de prueba: {p['tipo_prueba']}", f"- Vigencia: {p['vigencia']}",
              f"- Huella de la autorización: `{p['huella']}`", "", "## 2. Resumen", "",
              ", ".join(f"{sev}: {n}" for sev, n in ctx["resumen"].items()), "",
              "## 3. Hallazgos", ""]
    if not ctx["hallazgos"]:
        lineas.append("Sin hallazgos: ejecute recon, scan o web antes de generar el reporte.")
    else:
        lineas += ["| ID | Severidad | Módulo | Descripción | Evidencia | Recomendación |",
                   "|---|---|---|---|---|---|"]
        lineas += [f"| {h['id']} | {h['severidad']} | {h['modulo']} | {_celda(h['descripcion'])} | "
                   f"{_celda(h['evidencia'])} | {_celda(h['recomendacion'])} |" for h in ctx["hallazgos"]]
    lineas += ["", "## 4. Registro de auditoría", "", f"{len(ctx['auditoria'])} acción(es) registradas."]
    return "\n".join(lineas) + "\n"
