"""Build viz/index.html: six code panels beside one shared graph.

Click a node in the graph to highlight every line, in every syntax, that
states that node. Run after build.py and verify.py.
"""

import html
import json
import re
from pathlib import Path

from rdflib import Literal, URIRef
from rdflib.namespace import RDF

from build import FORMATS, JSONL_FILE, OUT, build_model, load_rows, to_graph

HERE = Path(__file__).resolve().parent
VIZ = HERE / "viz"

PANELS = [  # key, label, file, language hint
    ("jsonld", "JSON-LD", FORMATS["jsonld"][0]),
    ("microdata", "Microdata", FORMATS["microdata"][0]),
    ("rdfa", "RDFa", FORMATS["rdfa"][0]),
    ("turtle", "Turtle", FORMATS["turtle"][0]),
    ("ntriples", "N-Triples", FORMATS["ntriples"][0]),
    ("jsonl", "JSONL", JSONL_FILE),
]


def short(p):
    return str(p).split("/")[-1].split("#")[-1]


def build_graph(model):
    g = to_graph(model)
    nodes, links, idx = [], [], {}

    def node(term, subj=None, pred=None):
        if isinstance(term, URIRef):
            key = str(term)
            if key not in idx:
                types = [short(o) for o in g.objects(term, RDF.type)]
                kind = types[0] if types else "WebPage"
                label = ("#" + key.split("#")[1]) if "#" in key else (
                    model_label if key == model["id"] else key.replace("https://", ""))
                idx[key] = len(nodes)
                nodes.append({"id": key, "label": label, "kind": kind, "iri": key})
            return idx[key]
        # literals: one node per triple keeps the picture readable
        key = f"{subj}|{pred}|{term}"
        idx[key] = len(nodes)
        dt = term.datatype.split("#")[-1] if term.datatype else "string"
        nodes.append({"id": key, "label": str(term), "kind": "literal",
                      "value": str(term), "datatype": dt})
        return idx[key]

    model_label = next(v[1] for p, v in model["props"] if p == "name")
    for s, p, o in sorted(g):
        if p == RDF.type:
            continue
        si = node(s)
        oi = node(o, s, p)
        links.append({"source": si, "target": oi, "label": short(p)})
    return nodes, links


def token_patterns(n, inst_id):
    """Regexes that find this node in each syntax's text."""
    if n["kind"] != "literal":
        iri = n["iri"]
        pats = [re.escape(iri) + r"(?![#\w-])"]
        if iri.startswith(inst_id + "#"):
            pats.append(r"inst:" + re.escape(iri.split("#")[1]) + r"(?![\w-])")
        return pats
    v = n["value"]
    forms = {v, html.escape(v, quote=True), json.dumps(v)[1:-1]}
    return [r"(?<![\w.-])" + re.escape(f) + r"(?![\w.-])" for f in forms]


def _indent(line):
    return len(line) - len(line.lstrip(" "))


def expand_block(lines, i, key):
    """From the line that names a node, extend to the end of that node's block."""
    k = _indent(lines[i])
    out = [i]
    j = i + 1
    if key in ("jsonld",):
        # "@id" sits beside its sibling properties; the block ends when indent drops
        while j < len(lines) and _indent(lines[j]) >= k:
            out.append(j); j += 1
    elif key in ("microdata", "rdfa", "turtle"):
        # children are indented deeper; HTML also has a closing tag at the same indent
        while j < len(lines) and lines[j].strip() and _indent(lines[j]) > k:
            out.append(j); j += 1
        if key != "turtle" and j < len(lines) and lines[j].strip().startswith("</"):
            out.append(j)
    return out


def line_hits(text, pats, key, block):
    lines = text.splitlines()
    hits = set()
    for i, line in enumerate(lines):
        if any(re.search(p, line) for p in pats):
            starts_block = block and (
                (key == "jsonld" and '"@id"' in line) or
                (key in ("microdata", "rdfa") and ("itemid=" in line or "resource=" in line)) or
                (key == "turtle" and _indent(line) == 0))
            hits.update(expand_block(lines, i, key) if starts_block else [i])
    return sorted(hits)


def pretty_jsonl_line(text, inst_id):
    """Show the Rose-Hulman line of the JSONL file, plus a count of the rest."""
    lines = text.splitlines()
    mine = next(l for l in lines if json.loads(l)["@id"] == inst_id)
    note = f"// line {lines.index(mine) + 1} of {len(lines)}: one complete JSON-LD document per line"
    return note + "\n" + mine


def main(unitid="152318"):
    model = build_model(load_rows(unitid))
    nodes, links = build_graph(model)
    texts = {}
    for key, label, fname in PANELS:
        t = (OUT / fname).read_text(encoding="utf-8")
        texts[key] = pretty_jsonl_line(t, model["id"]) if key == "jsonl" else t.rstrip("\n")
    for n in nodes:
        pats = token_patterns(n, model["id"])
        block = n["kind"] not in ("literal", "WebPage")
        n["hits"] = {k: line_hits(texts[k], pats, k, block) for k in texts}

    results = json.loads((OUT / "verify-results.json").read_text())
    by_label = {r["format"]: r for r in results}
    panels = []
    for key, label, fname in PANELS:
        r = by_label[label]
        if r["strict"]:
            verdict, note = "identical", "Identical graph"
        else:
            friendly = {"string -> string@en": "{n} strings gain @en",
                        "xsd:decimal -> xsd:double": "{n} decimals become doubles"}
            parts = [friendly.get(k, "{n} " + k).format(n=len(v)) for k, v in r["changed"].items()]
            if r["extra"]:
                parts.append(f"{len(r['extra'])} extra parser triple" + ("s" if len(r["extra"]) > 1 else ""))
            verdict, note = "same-facts", "Same facts: " + ", ".join(parts)
        panels.append({"key": key, "label": label, "file": fname,
                       "triples": r["triples"], "verdict": verdict, "note": note,
                       "text": texts[key]})

    data = {"name": next(v[1] for p, v in model["props"] if p == "name"),
            "unitid": unitid, "nodes": nodes, "links": links, "panels": panels,
            "refTriples": len(to_graph(model))}
    VIZ.mkdir(exist_ok=True)
    page = (HERE / "viz_template.html").read_text(encoding="utf-8")
    page = page.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    (VIZ / "index.html").write_text(page, encoding="utf-8")
    print(f"Wrote {VIZ / 'index.html'} ({len(nodes)} nodes, {len(links)} edges)")


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else "152318")
