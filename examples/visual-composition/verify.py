"""Verify the published synthetic pairs and editable native shapes locally."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import zipfile
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main", "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def author_units(node):
    units = []
    if node["type"] == "leaf":
        element = node["element"]
        if element["type"] == "text" and element.get("role") != "caption":
            units.append((element["text"], element.get("role", "body")))
        if element.get("component") == "topology":
            units.extend((item["label"], item.get("role", element.get("role", "body"))) for item in element["nodes"])
    for child in node.get("children", []):
        units.extend(author_units(child))
    return Counter(units)


def native_units(slide):
    values = []
    for shape in slide.findall(".//p:sp", NS):
        value = "".join(item.text or "" for item in shape.findall(".//a:t", NS))
        if value and not value.startswith("计算样例"):
            values.append(re.sub(r"\s+", "", value))
    return Counter(values)


def verify():
    author = json.loads((ROOT / "comparison.author.json").read_text(encoding="utf-8"))
    with zipfile.ZipFile(ROOT / "visual-composition.pptx") as package:
        slides = [ET.fromstring(package.read(f"ppt/slides/slide{i}.xml")) for i in range(1, 8)]
    pairs = []
    for start in (0, 2, 4):
        before, after = author["pages"][start:start + 2]
        original, revised = author_units(before["layout"]), author_units(after["layout"])
        assert original == revised, (before["id"], "author content/role changed")
        assert native_units(slides[start]) == native_units(slides[start + 1]), (before["id"], "native visible content changed")
        pairs.append({"before": before["id"], "after": after["id"], "content_units": sum(original.values()),
                      "author_content_and_font_roles_equal": True, "native_text_units_equal_ignoring_whitespace": True})
    shapes = list(slides[3].find("p:cSld/p:spTree", NS))
    chevrons = [item for item in shapes if item.find('.//a:prstGeom[@prst="chevron"]', NS) is not None]
    links = [item for item in shapes if item.tag.endswith("}cxnSp")]
    ids = [item.find(".//p:cNvPr", NS).get("id") for item in chevrons]
    assert len(ids) == 4 and len(links) == 3
    for index, link in enumerate(links):
        assert link.find(".//a:stCxn", NS).get("id") == ids[index]
        assert link.find(".//a:endCxn", NS).get("id") == ids[index + 1]
        assert shapes.index(link) < shapes.index(chevrons[index])
    for slide in slides:
        all_ids = [item.get("id") for item in slide.findall(".//p:cNvPr", NS)]
        assert len(all_ids) == len(set(all_ids))
    cycle = slides[5].find(".//p:grpSp", NS)
    assert cycle is not None
    assert len(cycle.findall(".//a:custGeom", NS)) == 4
    assert len(cycle.findall(".//p:sp/p:txBody", NS)) == 4
    assert not cycle.findall(".//p:pic", NS) and not cycle.findall(".//p:cxnSp", NS)
    for label in cycle.findall(".//p:sp/p:txBody", NS):
        sizes = [int(run.get("sz")) for run in label.findall(".//a:rPr", NS) if run.get("sz")]
        assert sizes and all(size == 1400 for size in sizes), sizes
    integrated = {item.find(".//p:cNvPr", NS).get("name"): item for item in slides[6].find("p:cSld/p:spTree", NS)
                  if item.find(".//p:cNvPr", NS) is not None}
    row_alignment = []
    for index, (left, right) in enumerate((("objects", "proposal"), ("options", "validation"), ("execution", "ledger"))):
        names = [f"integrated-{left}--surface", f"integrated-step-{index}--surface", f"integrated-{right}--surface"]
        ys = [int(integrated[name].find(".//a:xfrm/a:off", NS).get("y")) for name in names]
        heights = [int(integrated[name].find(".//a:xfrm/a:ext", NS).get("cy")) for name in names]
        assert len(set(ys)) == 1 and len(set(heights)) == 1, (names, ys, heights)
        row_alignment.append({"row": index + 1, "same_top_and_height": True})
    files = [ROOT / "comparison.author.json", ROOT / "visual-composition.pptx", *sorted((ROOT / "previews").glob("slide-*.png"))]
    return {"status": "pass", "scope": "3 controlled pairs and 1 separate integrated synthetic example",
            "controlled_variables": ["body and title content units", "font roles", "design profile", "palette", "canvas"],
            "excluded_from_content_equality": "caption labels identify before/after; page 7 is a separate composition, not a controlled pair",
            "pairs": pairs, "integrated_row_alignment": row_alignment,
            "cycle_native_curved_arrows": 4, "cycle_native_labels_14pt": 4, "cycle_images_and_straight_connectors": 0,
            "native_chevrons": 4, "attached_native_connectors": 3, "duplicate_native_ids": 0,
            "hashes": {str(path.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}}


if __name__ == "__main__":
    result = verify()
    (ROOT / "comparison-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
