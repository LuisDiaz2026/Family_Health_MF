"""
Runner de pruebas con generación de evidencias.

Extiende DiscoverRunner de Django para:
  - medir la duración real de cada prueba;
  - capturar PASS / FAIL / ERROR / SKIP y el mensaje de error real;
  - combinar metadatos (docstring) + resultado real (harness.registrar);
  - exportar evidencias en .txt, .json y .csv.

Uso:
  python tests/run_suite.py unit
  python tests/run_suite.py integration
"""
import csv
import json
import time
import unittest
from datetime import datetime

from django.test.runner import DiscoverRunner

from tests.harness import (
    DIR_EVIDENCIAS, RAIZ_PROYECTO, limpiar_resultados,
    obtener_resultado_real, parsear_metadato,
)

# Registros recolectados durante la ejecución actual.
REGISTROS = []


class ResultadoEvidencia(unittest.TextTestResult):
    """Resultado que mide duración y captura el error real por prueba."""

    def startTest(self, test):
        self._t0 = time.perf_counter()
        super().startTest(test)

    def _duracion(self):
        t0 = getattr(self, "_t0", None)
        if t0 is None:
            return 0.0
        return round(time.perf_counter() - t0, 4)

    def _identificador(self, test):
        return test.id()

    def _nombre_metodo(self, test):
        return getattr(test, "_testMethodName", str(test))

    def _doc(self, test):
        metodo = getattr(test, getattr(test, "_testMethodName", ""), None)
        return getattr(metodo, "__doc__", "") or ""

    def _base(self, test):
        return {
            "test_id_unittest": self._identificador(test),
            "metodo": self._nombre_metodo(test),
            "entrada": "",
            "esperado": "",
            "duracion_s": self._duracion(),
            "error": "",
        }

    def _completar_meta(self, registro, test):
        meta = parsear_metadato(self._doc(test))
        registro.update({
            "id": meta["id"] or self._nombre_metodo(test),
            "requisito": meta["requisito"],
            "componente": meta["componente"],
            "entrada": meta["entrada"],
            "esperado": meta["esperado"],
        })
        registro["resultado_real"] = (
            obtener_resultado_real(registro["id"]) or registro.get("resultado_real", "")
        )
        return registro

    def addSuccess(self, test):
        super().addSuccess(test)
        reg = self._base(test)
        reg["estado"] = "PASS"
        reg["resultado_real"] = "Comportamiento observado coincide con lo esperado."
        REGISTROS.append(self._completar_meta(reg, test))

    def addFailure(self, test, err):
        super().addFailure(test, err)
        reg = self._base(test)
        reg["estado"] = "FAIL"
        reg["error"] = self._exc_info_to_string(err, test).strip()
        REGISTROS.append(self._completar_meta(reg, test))

    def addError(self, test, err):
        super().addError(test, err)
        reg = self._base(test)
        reg["estado"] = "ERROR"
        reg["error"] = self._exc_info_to_string(err, test).strip()
        REGISTROS.append(self._completar_meta(reg, test))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        reg = self._base(test)
        reg["estado"] = "SKIP"
        reg["error"] = f"Omitida: {reason}"
        REGISTROS.append(self._completar_meta(reg, test))


class RunnerEvidencia(DiscoverRunner):
    """DiscoverRunner que descubre tests en un directorio y exporta evidencias."""

    def __init__(self, *args, ruta_descubrimiento=None, prefijo_evidencia=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.ruta_descubrimiento = ruta_descubrimiento
        self.prefijo_evidencia = prefijo_evidencia or "pruebas"

    def get_resultclass(self):
        return ResultadoEvidencia

    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        if self.ruta_descubrimiento:
            suite = self.test_suite()
            loader = unittest.TestLoader()
            suite.addTests(
                loader.discover(
                    start_dir=str(self.ruta_descubrimiento),
                    top_level_dir=str(RAIZ_PROYECTO),
                )
            )
            if extra_tests:
                suite.addTests(extra_tests)
            return suite
        return super().build_suite(test_labels, extra_tests, **kwargs)

    # ---- Exportación de evidencias ----
    def exportar(self, commit, entorno, base_datos):
        DIR_EVIDENCIAS.mkdir(parents=True, exist_ok=True)
        total = len(REGISTROS)
        aprobadas = sum(1 for r in REGISTROS if r["estado"] == "PASS")
        fallidas = sum(1 for r in REGISTROS if r["estado"] == "FAIL")
        errores = sum(1 for r in REGISTROS if r["estado"] == "ERROR")
        omitidas = sum(1 for r in REGISTROS if r["estado"] == "SKIP")
        duracion_total = round(sum(r["duracion_s"] for r in REGISTROS), 4)
        fecha = datetime.now().isoformat(timespec="seconds")

        cabecera = {
            "fecha_ejecucion": fecha,
            "commit": commit,
            "entorno": entorno,
            "base_datos": base_datos,
            "total": total,
            "aprobadas": aprobadas,
            "fallidas": fallidas,
            "errores": errores,
            "omitidas": omitidas,
            "duracion_total_s": duracion_total,
        }

        # ---- JSON ----
        ruta_json = DIR_EVIDENCIAS / f"{self.prefijo_evidencia}.json"
        ruta_json.write_text(
            json.dumps({"resumen": cabecera, "resultados": REGISTROS},
                       ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        # ---- CSV ----
        ruta_csv = DIR_EVIDENCIAS / f"{self.prefijo_evidencia}.csv"
        columnas = ["id", "requisito", "componente", "entrada", "esperado",
                    "resultado_real", "estado", "duracion_s", "error",
                    "metodo", "test_id_unittest"]
        with ruta_csv.open("w", newline="", encoding="utf-8-sig") as fh:
            escritor = csv.DictWriter(fh, fieldnames=columnas, extrasaction="ignore")
            escritor.writeheader()
            for reg in REGISTROS:
                escritor.writerow(reg)

        # ---- TXT ----
        ruta_txt = DIR_EVIDENCIAS / f"{self.prefijo_evidencia}.txt"
        lineas = []
        lineas.append("=" * 78)
        lineas.append("EVIDENCIA DE PRUEBAS - CLUB FAMILY HEALTH MF")
        lineas.append("=" * 78)
        lineas.append(f"Fecha de ejecucion : {fecha}")
        lineas.append(f"Commit             : {commit}")
        lineas.append(f"Entorno            : {entorno}")
        lineas.append(f"Base de datos      : {base_datos}")
        lineas.append(f"Total              : {total}")
        lineas.append(f"Aprobadas (PASS)   : {aprobadas}")
        lineas.append(f"Fallidas  (FAIL)   : {fallidas}")
        lineas.append(f"Errores   (ERROR)  : {errores}")
        lineas.append(f"Omitidas  (SKIP)   : {omitidas}")
        lineas.append(f"Duracion total (s) : {duracion_total}")
        lineas.append("=" * 78)
        for reg in REGISTROS:
            lineas.append("")
            lineas.append(f"[{reg['estado']}] {reg['id']} - {reg['metodo']}")
            lineas.append(f"  Requisito        : {reg['requisito']}")
            lineas.append(f"  Componente       : {reg['componente']}")
            lineas.append(f"  Entrada          : {reg['entrada']}")
            lineas.append(f"  Resultado esperado: {reg['esperado']}")
            lineas.append(f"  Resultado real   : {reg['resultado_real']}")
            lineas.append(f"  Duracion (s)     : {reg['duracion_s']}")
            if reg["error"]:
                lineas.append(f"  Error            : {reg['error'].splitlines()[0]}")
        lineas.append("")
        lineas.append("=" * 78)
        ruta_txt.write_text("\n".join(lineas), encoding="utf-8")

        return cabecera, ruta_txt


def ejecutar(prefijo_evidencia, ruta_descubrimiento, commit, entorno, base_datos):
    """Ejecuta la suite y exporta evidencias. Devuelve (resumen, codigo_salida)."""
    limpiar_resultados()
    REGISTROS.clear()
    runner = RunnerEvidencia(
        verbosity=2,
        ruta_descubrimiento=ruta_descubrimiento,
        prefijo_evidencia=prefijo_evidencia,
    )
    resultado = runner.run_tests(["__suite__"])
    resumen, _ = runner.exportar(commit, entorno, base_datos)
    return resumen, (0 if resultado == 0 else 1)
