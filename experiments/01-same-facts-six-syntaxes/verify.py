"""Experiment 1 check: parse all six files back into RDF and compare them.

Each file is parsed by a standard parser for its syntax and compared to a
reference graph built directly from the data model in build.py.

Two comparisons are reported:
  identical  - every triple identical, including datatypes and language tags
  same facts - literals compared by lexical value only, and parser
               bookkeeping triples (rdfa:usesVocabulary) dropped

Usage:
    python build.py && python verify.py
"""

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urljoin

import html5lib
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.compare import graph_diff, isomorphic, to_isomorphic
from rdflib.namespace import RDF, XSD

from build import FORMATS, JSONL_FILE, OUT, build_model, load_rows, to_graph

HTML_NS = "{http://www.w3.org/1999/xhtml}"


# ---------------------------------------------------------------------------
# Microdata -> RDF
# rdflib has no Microdata parser, so this follows the W3C "Microdata to RDF"
# note (https://www.w3.org/TR/microdata-rdf/) for the cases used here:
# itemid subjects, itemtype classes, nested items, URL and plain-text values.
# ---------------------------------------------------------------------------

URL_ELEMENTS = {"a", "area", "link", "audio", "video", "embed", "iframe",
                "img", "source", "track", "object"}


def _tag(el):
    return el.tag.replace(HTML_NS, "")


def _text(el):
    return "".join(el.itertext())


INT_RE = re.compile(r"^-?[0-9]+$")
FLOAT_RE = re.compile(r"^-?[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?$")


def _number(text):
    """data/meter values: valid integers -> xsd:integer, valid floats -> xsd:double."""
    if INT_RE.match(text):
        return Literal(text, datatype=XSD.integer)
    if FLOAT_RE.match(text):
        return Literal(text, datatype=XSD.double)
    return Literal(text)


def _item_value(el, base, lang):
    tag = _tag(el)
    if tag == "meta":
        return Literal(el.get("content", ""), lang=lang)
    if tag in URL_ELEMENTS:
        attr = "data" if tag == "object" else ("src" if el.get("src") else "href")
        return URIRef(urljoin(base, el.get(attr, "")))
    if tag in ("data", "meter"):
        return _number(el.get("value", ""))
    if tag == "time" and el.get("datetime"):
        return Literal(el.get("datetime"))
    # Text content becomes a language-tagged string when the element has a
    # language, which it inherits from the nearest ancestor with lang="...".
    return Literal(_text(el), lang=lang)


def _item(el, g, base, parents):
    subj = URIRef(urljoin(base, el.get("itemid"))) if el.get("itemid") else BNode()
    itemtype = (el.get("itemtype") or "").split()
    for t in itemtype:
        g.add((subj, RDF.type, URIRef(t)))
    vocab = itemtype[0].rsplit("/", 1)[0] + "/" if itemtype else ""

    def props(parent):
        for child in parent:
            if not isinstance(child.tag, str):
                continue
            names = (child.get("itemprop") or "").split()
            if names:
                value = _item(child, g, base, parents) if child.get("itemscope") is not None \
                    else _item_value(child, base, _language(child, parents))
                for n in names:
                    pred = URIRef(n if ":" in n else vocab + n)
                    g.add((subj, pred, value))
            if child.get("itemscope") is None:
                props(child)  # properties can sit deeper in the tree

    props(el)
    return subj


def _language(el, parents):
    while el is not None:
        if el.get("lang"):
            return el.get("lang")
        el = parents.get(el)
    return None


def parse_microdata(path):
    doc = html5lib.parse(path.read_text(encoding="utf-8"))
    parents = {c: p for p in doc.iter() for c in p}
    g = Graph()
    base = path.resolve().as_uri()
    nested = set()
    for el in doc.iter():
        if isinstance(el.tag, str) and el.get("itemscope") is not None:
            if el.get("itemprop"):
                nested.add(el)
    for el in doc.iter():
        if isinstance(el.tag, str) and el.get("itemscope") is not None \
                and el not in nested:
            _item(el, g, base, parents)
    return g


# ---------------------------------------------------------------------------
# The other parsers
# ---------------------------------------------------------------------------

def parse_rdfa(path):
    from pyRdfa import pyRdfa
    return pyRdfa().graph_from_source(str(path))


def parse_jsonl_line(path, subject):
    for line in path.read_text(encoding="utf-8").splitlines():
        if json.loads(line).get("@id") == subject:
            return Graph().parse(data=line, format="json-ld")
    raise ValueError(f"{subject} not found in {path.name}")


def parse_file(key, path, subject):
    if key == "microdata":
        return parse_microdata(path)
    if key == "rdfa":
        return parse_rdfa(path)
    if key == "jsonl":
        return parse_jsonl_line(path, subject)
    fmt = {"jsonld": "json-ld", "turtle": "turtle", "ntriples": "nt"}[key]
    return Graph().parse(str(path), format=fmt)


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

RDFA_VOCAB_NS = "http://www.w3.org/ns/rdfa#"


def same_facts_view(g):
    """Copy of g reduced to its facts: literals become plain lexical strings
    (no datatype, no language tag) and parser bookkeeping triples, such as
    rdfa:usesVocabulary, are dropped."""
    out = Graph()
    for s, p, o in g:
        if str(p).startswith(RDFA_VOCAB_NS):
            continue
        out.add((s, p, Literal(str(o)) if isinstance(o, Literal) else o))
    return out


def _kind(o):
    if not isinstance(o, Literal):
        return "IRI"
    if o.datatype:
        return "xsd:" + o.datatype.split("#")[-1]
    return f"string@{o.language}" if o.language else "string"


def describe_diff(ref, got):
    """Group differences into categories, e.g. 'string -> string@en: 36 triples'."""
    _, only_ref, only_got = graph_diff(to_isomorphic(ref), to_isomorphic(got))
    pending = {}
    for s_, p, o in only_ref:
        pending.setdefault((str(p), str(o)), []).append(o)
    changes, extra = {}, []
    for s_, p, o in sorted(only_got):
        key = (str(p), str(o))
        if pending.get(key):
            before = pending[key].pop()
            label = f"{_kind(before)} -> {_kind(o)}"
            changes.setdefault(label, []).append(f"{p.split('/')[-1]}: {o}")
        else:
            extra.append(f"{p.split('/')[-1].split('#')[-1]}: {o}")
    missing = [f"{k[0].split('/')[-1]}: {k[1]}" for k, v in pending.items() for _ in v]
    return {"changed": changes, "extra": extra, "missing": missing}


LABELS = {"jsonld": "JSON-LD", "microdata": "Microdata", "rdfa": "RDFa",
          "turtle": "Turtle", "ntriples": "N-Triples", "jsonl": "JSONL"}


def main(unitid="152318"):
    model = build_model(load_rows(unitid))
    ref = to_graph(model)
    files = {k: OUT / f for k, (f, _) in FORMATS.items()}
    files["jsonl"] = OUT / JSONL_FILE

    results = []
    for key in ["jsonld", "microdata", "rdfa", "turtle", "ntriples", "jsonl"]:
        g = parse_file(key, files[key], model["id"])
        strict = isomorphic(ref, g)
        lex = isomorphic(same_facts_view(ref), same_facts_view(g))
        diff = {"changed": {}, "extra": [], "missing": []} if strict else describe_diff(ref, g)
        results.append({"format": LABELS[key], "file": files[key].name,
                        "triples": len(g), "strict": strict, "lexical": lex, **diff})

    name = next(v[1] for p, v in model["props"] if p == "name")
    lines = [f"# Verification: {name} (UNITID {unitid})", "",
             f"Reference graph: {len(ref)} triples built directly from the data model.", "",
             "| Format | File | Triples | Identical graph | Same facts* |",
             "|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['format']} | `{r['file']}` | {r['triples']} | "
                     f"{'yes' if r['strict'] else 'no'} | {'yes' if r['lexical'] else 'no'} |")
    lines += ["", "*Same facts: literals compared by lexical value only (datatypes and "
              "language tags ignored), and parser bookkeeping triples such as "
              "`rdfa:usesVocabulary` dropped."]
    for r in results:
        if r["strict"]:
            continue
        lines += ["", f"## {r['format']}: what changed", ""]
        for label, items in r["changed"].items():
            ex = "; ".join(items[:3]) + ("; ..." if len(items) > 3 else "")
            lines.append(f"- **{label}** on {len(items)} triples (e.g. {ex})")
        for e in r["extra"]:
            lines.append(f"- **extra triple** added by the parser: {e}")
        for m in r["missing"]:
            lines.append(f"- **missing**: {m}")
    report = "\n".join(lines) + "\n"
    (OUT / "verify-report.md").write_text(report, encoding="utf-8")
    (OUT / "verify-results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(report)
    return all(r["lexical"] for r in results)


if __name__ == "__main__":
    ok = main(sys.argv[1] if len(sys.argv) > 1 else "152318")
    sys.exit(0 if ok else 1)
