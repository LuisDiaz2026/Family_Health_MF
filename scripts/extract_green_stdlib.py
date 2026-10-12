import sys
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

DOCX_PATH = r"c:\Users\gusta\OneDrive - UNIR\TRABAJOS DE GRADO\TRABAJOS DE GRADO\UAN\LUIS\02. TESIS\Reuniones\Monografia_UAN_LUIS_DIAZ_revision_documentos_adicionales.docx"
OUT_PATH = r"c:\Family_Health_MF\green_text_extractions.json"

# ================ NAMESPACES WordprocessingML (OOXML) ================
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}
ET.register_namespace("w", W_NS)

GREEN_RGBS = {
    "008000", "00B050", "548235", "375623", "92D050", "70AD47",
    "66FF66", "00FF00", "006400", "228B22", "2E8B57", "3CB371",
    "32CD32", "00A651", "4F7942", "2E7D32", "388E3C", "43A047",
    "4CAF50", "66BB6A", "81C784",
}
GREEN_HL = {"green", "brightGreen"}


def w(tag):
    return f"{{{W_NS}}}{tag}"


def is_green_rgb(h: str) -> bool:
    if not h: return False
    h = h.upper().replace("#", "").strip()
    if len(h) < 6: return False
    h = h[-6:]
    if h in GREEN_RGBS:
        return True
    try:
        r = int(h[0:2], 16); g = int(h[2:4], 16); b = int(h[4:6], 16)
        if g >= 80 and g > r + 25 and g > b + 25:
            return True
    except Exception:
        pass
    return False


def get_paragraph_style_id(p_el) -> str:
    try:
        pPr = p_el.find(f"w:pPr", NS)
        if pPr is None: return ""
        pStyle = pPr.find(f"w:pStyle", NS)
        if pStyle is None: return ""
        return (pStyle.get(w("val")) or "").strip()
    except Exception:
        return ""


def iter_paragraph_runs(p_el):
    """Itera sobre runs (incluyendo dentro de hyperlinks, smarttag, etc) de un párrafo."""
    # Direct runs
    for r in p_el.findall(f"w:r", NS):
        yield r
    # Runs dentro de hyperlink (w:hyperlink/w:r)
    for hyper in p_el.findall(f"w:hyperlink", NS):
        for r in hyper.findall(f"w:r", NS):
            yield r


def get_run_props(r_el):
    """Retorna dict con color_hex, highlight."""
    d = {"color_hex": None, "highlight": None}
    try:
        rPr = r_el.find(f"w:rPr", NS)
        if rPr is None: return d
        color_el = rPr.find(f"w:color", NS)
        if color_el is not None:
            d["color_hex"] = (color_el.get(w("val")) or "").upper()
        hl_el = rPr.find(f"w:highlight", NS)
        if hl_el is not None:
            d["highlight"] = (hl_el.get(w("val")) or "").strip()
    except Exception:
        pass
    return d


def paragraph_text_from_runs(p_el) -> str:
    parts = []
    for r in iter_paragraph_runs(p_el):
        t_el = r.find(f"w:t", NS)
        if t_el is not None:
            parts.append(t_el.text or "")
    return "".join(parts)


def heading_rank_of_style(style_id: str) -> int:
    """Retorna 0 si no es heading, 1..9 si es Título/Heading."""
    s = (style_id or "").lower()
    # Ttulo1, Ttulo2, Ttulo3 (es-CO Word)
    m = re.search(r"(?:ttulo|titulo|heading)\s*(\d+)", s)
    if m:
        try: return max(1, int(m.group(1)))
        except Exception: return 0
    return 0


def page_estimate(total_p: int, idx: int) -> int:
    base_pages_front = 6
    estimated_total_pages = 85
    if total_p <= 0: return 1
    ratio = idx / total_p
    return max(1, base_pages_front + int(ratio * (estimated_total_pages - base_pages_front)))


def extract_body_paragraphs(xml_bytes):
    root = ET.fromstring(xml_bytes)
    body = root.find("w:body", NS)
    if body is None:
        return []
    paragraphs = []
    for child in list(body):
        if child.tag == w("p"):
            paragraphs.append(child)
    return paragraphs


def main():
    if not Path(DOCX_PATH).exists():
        print(f"ERROR: no existe archivo {DOCX_PATH}", file=sys.stderr)
        sys.exit(2)

    with zipfile.ZipFile(DOCX_PATH, "r") as z:
        xml_bytes = z.read("word/document.xml")

    paragraphs = extract_body_paragraphs(xml_bytes)
    total_p = len(paragraphs)

    # Construir heading stack
    heading_stack = []  # lista de tuplas (level, texto)
    results = []

    for idx, p_el in enumerate(paragraphs):
        style_id = get_paragraph_style_id(p_el)
        rank = heading_rank_of_style(style_id)

        # Actualizar stack heading
        if rank > 0:
            txt_heading = paragraph_text_from_runs(p_el).strip()
            heading_stack = [(lvl, txt) for (lvl, txt) in heading_stack if lvl < rank]
            heading_stack.append((rank, txt_heading or f"Ttulo {rank}"))
        heading_path = " > ".join([f"Ttulo {lvl}: {txt}" for (lvl, txt) in heading_stack])

        # Contexto anterior/posterior simple
        ctx_before = ""
        for j in range(max(0, idx-4), idx):
            t = paragraph_text_from_runs(paragraphs[j]).strip()
            if t:
                ctx_before = t[-160:]
        ctx_after = ""
        for j in range(idx+1, min(total_p, idx+4)):
            t = paragraph_text_from_runs(paragraphs[j]).strip()
            if t:
                ctx_after = t[:160]
                break

        full_text = paragraph_text_from_runs(p_el).strip()

        # Iterar runs y detectar verde
        green_runs_in_para = []
        for r_el in iter_paragraph_runs(p_el):
            props = get_run_props(r_el)
            t_el = r_el.find(f"w:t", NS)
            txt_run = (t_el.text or "") if t_el is not None else ""
            if not txt_run.strip():
                continue
            reasons = []
            if props["color_hex"] and is_green_rgb(props["color_hex"]):
                reasons.append(f"font=#{props['color_hex']}")
            if props["highlight"] and props["highlight"].lower() in GREEN_HL:
                reasons.append(f"highlight={props['highlight']}")
            if not reasons:
                continue
            green_runs_in_para.append( (txt_run, " + ".join(reasons)) )

        if not green_runs_in_para:
            continue

        # Merge runs del mismo párrafo
        merged_green_text = "".join([t for (t, _) in green_runs_in_para])
        reasons_str = " | ".join(list(dict.fromkeys([r for (_, r) in green_runs_in_para])))

        entry = {
            "paragraph_index": idx,
            "paragraph_style_id": style_id,
            "heading_rank": rank,
            "heading_path": heading_path,
            "page_estimate": page_estimate(total_p, idx),
            "reason_detected_green": reasons_str,
            "text_green": merged_green_text,
            "full_paragraph_text": full_text,
            "context_before": ctx_before,
            "context_after": ctx_after,
        }
        results.append(entry)

    out = {
        "document": DOCX_PATH,
        "total_paragraphs": total_p,
        "green_entries_count": len(results),
        "entries": results,
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("=" * 80)
    print(f"OK. Párrafos totales analizados: {total_p}")
    print(f"OK. Entradas VERDES detectadas: {len(results)}")
    print(f"Salida JSON: {OUT_PATH}")
    print("=" * 80)
    for i, e in enumerate(results, 1):
        tg = e["text_green"].replace("\n", " ")[:300]
        print(f"\n[{i:02d}] === Pg ~{e['page_estimate']} === {e['heading_path']}")
        print(f"  RAZON: {e['reason_detected_green']}")
        print(f"  VERDE: {tg}")
        if e["context_before"]:
            cb = e["context_before"].replace("\n", " ")[:160]
            print(f"  ANTES: {cb}")
        if e["full_paragraph_text"]:
            fp = e["full_paragraph_text"].replace("\n", " ")[:240]
            print(f"  PARA : {fp}")
        if e["context_after"]:
            ca = e["context_after"].replace("\n", " ")[:160]
            print(f"  DESPS: {ca}")


if __name__ == "__main__":
    main()
