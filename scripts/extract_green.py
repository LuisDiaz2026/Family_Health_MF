import sys
import json
import re
from pathlib import Path

# Asegurar site-packages del venv (por si PowerShell ConstrainedLanguage borra PYTHONPATH)
_VENV_SITE = r"C:\Family_Health_MF\.venv\Lib\site-packages"
if Path(_VENV_SITE).exists() and _VENV_SITE not in sys.path:
    sys.path.insert(0, _VENV_SITE)

try:
    from docx import Document
    from docx.shared import RGBColor
except ImportError:
    print("ERROR: python-docx no instalado. Ejecuta: python -m pip install python-docx", file=sys.stderr)
    sys.exit(1)

DOCX_PATH = r"c:\Users\gusta\OneDrive - UNIR\TRABAJOS DE GRADO\TRABAJOS DE GRADO\UAN\LUIS\02. TESIS\Reuniones\Monografia_UAN_LUIS_DIAZ_revision_documentos_adicionales.docx"
OUT_PATH = r"c:\Family_Health_MF\green_text_extractions.json"

# Colores verdes comunes en Word (RGB hex) — incluimos variantes (oscuro, claro, standard)
GREEN_RGBS = {
    "008000",  # Green standard
    "00B050",  # Verde oscuro Office
    "548235",  # Verde oliva profundo
    "375623",  # Verde bosque
    "92D050",  # Verde claro
    "70AD47",  # Verde 2 Office
    "66FF66",  # Verde neón suave
    "00FF00",  # Verde puro
    "006400",  # DarkGreen
    "228B22",  # ForestGreen
    "2E8B57",  # SeaGreen
    "3CB371",  # MediumSeaGreen
    "32CD32",  # LimeGreen
    "00A651",  # Corporativo común
    "4F7942",  # Fern green
    "2E7D32",  # Material green 800
    "388E3C",  # Material green 700
    "43A047",  # Material green 600
    "4CAF50",  # Material green 500
    "66BB6A",  # Material green 400
    "81C784",  # Material green 300
}

# Highlight verde (enum WD_COLOR_INDEX = 4 = GREEN, 11 = BRIGHT_GREEN)
GREEN_HL_INDICES = {4, 11}


def is_green_color(rgb_hex: str) -> bool:
    if not rgb_hex:
        return False
    h = rgb_hex.upper().replace("#", "")
    if len(h) != 6:
        return False
    # Verificar lista exacta
    if h in GREEN_RGBS:
        return True
    # Rango adicional: R <= 0x7F, G > R + 50, G > B + 30 (verde perceptible)
    try:
        r = int(h[0:2], 16); g = int(h[2:4], 16); b = int(h[4:6], 16)
        if g >= 90 and g > r + 20 and g > b + 20:
            return True
    except ValueError:
        pass
    return False


def get_run_color(run):
    """Retorna (font_color_hex, highlight_index)"""
    font_color = None
    try:
        if run.font.color and run.font.color.rgb:
            font_color = str(run.font.color.rgb).upper()
    except Exception:
        font_color = None
    hl = None
    try:
        if run.font.highlight_color is not None:
            hl = int(run.font.highlight_color)
    except Exception:
        hl = None
    return font_color, hl


def walk_runs_in_paragraph(paragraph):
    runs = []
    for run in paragraph.runs:
        runs.append(run)
    # TODO: in some cases text in hyperlinks/etc. Iterar XML en busca de w:r extra
    return runs


def extract_context_before(doc, idx, n=3):
    ctx = []
    for i in range(max(0, idx-n), idx):
        t = doc.paragraphs[i].text.strip()
        if t:
            ctx.append(t)
    return " / ".join(ctx[-2:])


def extract_context_after(doc, idx, n=3):
    ctx = []
    for i in range(idx+1, min(len(doc.paragraphs), idx+1+n)):
        t = doc.paragraphs[i].text.strip()
        if t:
            ctx.append(t)
    return " / ".join(ctx[:2])


def heading_of(doc, idx):
    """Retorna la ruta de títulos anterior al párrafo idx."""
    path = []
    for i in range(idx, -1, -1):
        p = doc.paragraphs[i]
        style = (p.style.name or "").lower()
        if style.startswith("título ") or style.startswith("titulo ") or style.startswith("heading "):
            label = p.text.strip()
            if label:
                m = re.search(r"(\d+(?:\.\d+)*)", style)
                if m:
                    level = m.group(1)
                    path.append(f"[{style.upper()}] {label}")
                else:
                    path.append(f"[{style.upper()}] {label}")
                if (style.startswith("título 1") or style.startswith("titulo 1") or style.startswith("heading 1")):
                    break
    path.reverse()
    return " > ".join(path)


def page_estimate(total_paragraphs, idx):
    """Estimado de página: Word suele ~35 párrafos por página en documentos normales (títulos + contenido)."""
    if total_paragraphs <= 0:
        return 1
    # Ajuste: las primeras páginas son portada, abstract, TOC: saltar ~6 páginas
    base_pages_for_front = 6
    content_ratio = idx / max(total_paragraphs, 1)
    estimated_total_pages = 80  # aprox TFG
    page = base_pages_for_front + int(content_ratio * (estimated_total_pages - base_pages_for_front))
    return max(1, page)


def main():
    if not Path(DOCX_PATH).exists():
        print(f"ERROR archivo no existe: {DOCX_PATH}", file=sys.stderr)
        sys.exit(2)

    doc = Document(DOCX_PATH)
    total = len(doc.paragraphs)
    results = []

    current_heading_path = ""

    for idx, para in enumerate(doc.paragraphs):
        style_name = para.style.name or ""
        style_lc = style_name.lower()
        if style_lc.startswith("título") or style_lc.startswith("titulo") or style_lc.startswith("heading"):
            current_heading_path = heading_of(doc, idx)

        for run in para.runs:
            text = run.text
            if not text or not text.strip():
                continue
            font_color_hex, hl_idx = get_run_color(run)
            green_reasons = []
            if font_color_hex and is_green_color(font_color_hex):
                green_reasons.append(f"font_color=#{font_color_hex}")
            if hl_idx is not None and hl_idx in GREEN_HL_INDICES:
                green_reasons.append(f"highlight_idx={hl_idx}")

            if not green_reasons:
                continue

            ctx_before = extract_context_before(doc, idx)
            ctx_after = extract_context_after(doc, idx)
            entry = {
                "paragraph_index": idx,
                "paragraph_style": style_name,
                "heading_path": current_heading_path,
                "page_estimate": page_estimate(total, idx),
                "reason_detected_green": " + ".join(green_reasons),
                "text_green": text,
                "full_paragraph_text": para.text.strip(),
                "context_before": ctx_before,
                "context_after": ctx_after,
            }
            results.append(entry)

    # Merge adjacentes del mismo párrafo (mismo heading/página) para reducir ruido
    merged = []
    buf_text = []
    buf_ref = None
    for r in results:
        key = (r["paragraph_index"], r["heading_path"], r["page_estimate"])
        if buf_ref and key == (buf_ref["paragraph_index"], buf_ref["heading_path"], buf_ref["page_estimate"]):
            buf_text.append(r["text_green"])
        else:
            if buf_ref and buf_text:
                br = dict(buf_ref); br["text_green"] = "".join(buf_text)
                merged.append(br)
            buf_ref = r
            buf_text = [r["text_green"]]
    if buf_ref and buf_text:
        br = dict(buf_ref); br["text_green"] = "".join(buf_text)
        merged.append(br)

    out = {
        "document": DOCX_PATH,
        "total_paragraphs": total,
        "green_entries_count": len(merged),
        "entries": merged,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"OK. Total entradas VERDES detectadas: {len(merged)}")
    print(f"Salida JSON guardada en: {OUT_PATH}")
    print()
    for i, e in enumerate(merged[:50], 1):
        tg = e["text_green"].replace("\n", " ")[:280]
        print(f"[{i:02d}] Pág ~{e['page_estimate']} | {e['heading_path']}")
        print(f"       VERDE: {tg}")
        if e["context_before"]:
            print(f"       ANTES: {str(e['context_before'])[:140]}")
        print()


if __name__ == "__main__":
    main()
