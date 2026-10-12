import sys
from pathlib import Path

_VENV_SITE = r"C:\Family_Health_MF\.venv\Lib\site-packages"
print(f"VENV_SITE existe: {Path(_VENV_SITE).exists()}")
if Path(_VENV_SITE).exists():
    sys.path.insert(0, _VENV_SITE)
    print(f"Insertado en sys.path[0] = {sys.path[0]}")

print(f"\nsys.path primeros 6:")
for i, p in enumerate(sys.path[:6]):
    print(f"  [{i}] {p}")

print("\n>>> Intentando import docx...")
try:
    import docx
    print(f"OK. docx.__file__ = {getattr(docx, '__file__', 'N/A')}")
    from docx import Document
    print("OK Document importado.")
except Exception as e:
    import traceback
    print(f"ERROR: type={type(e).__name__} msg={e}")
    traceback.print_exc()
    sys.exit(1)

print("\n>>> Abriendo documento...")
DOCX_PATH = r"c:\Users\gusta\OneDrive - UNIR\TRABAJOS DE GRADO\TRABAJOS DE GRADO\UAN\LUIS\02. TESIS\Reuniones\Monografia_UAN_LUIS_DIAZ_revision_documentos_adicionales.docx"
print(f"Path docx existe: {Path(DOCX_PATH).exists()}")
if Path(DOCX_PATH).exists():
    doc = Document(DOCX_PATH)
    print(f"OK. Párrafos totales: {len(doc.paragraphs)}")
    # Dump los primeros 20 párrafos con style name (primera letra del texto)
    for idx, p in enumerate(doc.paragraphs[:30]):
        txt = p.text.strip().replace("\n", " ")[:80]
        colors = set()
        for run in p.runs:
            try:
                if run.font.color and run.font.color.rgb:
                    col = str(run.font.color.rgb).upper()
                    colors.add(col)
            except Exception:
                pass
        if colors:
            print(f" [{idx:03d}] {p.style.name:<25} colors={colors!r:<30} txt={txt!r}")
        elif txt:
            print(f" [{idx:03d}] {p.style.name:<25} colors=---                   txt={txt!r}")
        else:
            print(f" [{idx:03d}] {p.style.name:<25} (vacio)")
