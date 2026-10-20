"""
Utilidades de trazabilidad para la suite de pruebas Family Health MF.

Cada prueba declara su metadato en el docstring con el formato:

    "ID | REQUISITO | COMPONENTE | ENTRADA | RESULTADO ESPERADO"

y registra su resultado real observado con ``registrar(ID, "...")``.
El runner (tests/runner.py) combina ambos para producir las evidencias
(txt/json/csv) sin inventar valores.
"""
from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
DIR_EVIDENCIAS = RAIZ_PROYECTO / "evidencias"

# Resultados reales observados durante la ejecución (en memoria).
_RESULTADOS_REALES: dict = {}


def registrar(test_id: str, resultado_real: str) -> None:
    """Registra el resultado real observado por una prueba (texto corto)."""
    _RESULTADOS_REALES[str(test_id)] = str(resultado_real)


def obtener_resultado_real(test_id: str) -> str:
    return _RESULTADOS_REALES.get(str(test_id), "")


def limpiar_resultados() -> None:
    _RESULTADOS_REALES.clear()


def parsear_metadato(docstring: str) -> dict:
    """
    Extrae los metadatos de trazabilidad del docstring de una prueba.
    Devuelve un dict con id/requisito/componente/entrada/esperado.
    """
    vacio = {"id": "", "requisito": "", "componente": "",
             "entrada": "", "esperado": ""}
    if not docstring:
        return vacio
    primera = ""
    for linea in docstring.strip().splitlines():
        if linea.strip():
            primera = linea.strip()
            break
    if "|" not in primera:
        return vacio
    partes = [p.strip() for p in primera.split("|")]
    if len(partes) < 5:
        return vacio
    return {
        "id": partes[0],
        "requisito": partes[1],
        "componente": partes[2],
        "entrada": partes[3],
        "esperado": " | ".join(partes[4:]),
    }
