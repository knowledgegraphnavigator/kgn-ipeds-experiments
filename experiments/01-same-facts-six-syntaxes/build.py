"""Experiment 1: One University, Six Syntaxes.

Reads the IPEDS CSVs in ../../data, models one institution once, and writes the
same facts as JSON-LD, Microdata, RDFa, Turtle, N-Triples and JSONL.

Usage:
    python build.py            # Rose-Hulman Institute of Technology (UNITID 152318)
    python build.py 132903     # any UNITID in the sample
"""

import csv
import html
import json
import sys
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, XSD

HERE = Path(__file__).resolve().parent
DATA = HERE.parent.parent / "data"
OUT = HERE / "output"

SCHEMA = "https://schema.org/"
ID_BASE = "https://knowledgegraphnavigator.com/id/ipeds/"
DEFAULT_UNITID = "152318"  # Rose-Hulman Institute of Technology


# ---------------------------------------------------------------------------
# 1. Load the facts
# ---------------------------------------------------------------------------

def load_rows(unitid=None):
    """Return {UNITID: merged row} from the four institution-level CSVs."""
    rows = {}
    for name in ["institutions", "admissions-enrollment", "outcomes"]:
        with open(DATA / f"{name}-v1.0.csv", newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                rows.setdefault(r["UNITID"], {}).update(r)
    return rows if unitid is None else rows[unitid]


def number(s):
    """'92.0' -> ('92', integer); '76.9' -> ('76.9', decimal); '' -> None."""
    if s is None or s.strip() == "":
        return None
    v = float(s)
    if v.is_integer():
        return (str(int(v)), "integer")
    return (s.strip(), "decimal")


def split_aliases(s):
    s = (s or "").strip()
    if not s:
        return []
    return [a.strip() for a in s.split("|")] if "|" in s else [s]


# ---------------------------------------------------------------------------
# 2. One data model
#
# A node is {"id": IRI, "type": schema.org class, "props": [(prop, value), ...]}
# A value is one of:
#   ("str", text)                 plain string literal
#   ("num", lexical, "integer"|"decimal")
#   ("iri", IRI)                  link to a web resource
#   ("node", node)                link to another node in the model
# ---------------------------------------------------------------------------

def property_value(base, slug, name, value, unit=None, source=None):
    props = [("name", ("str", name)), ("value", value)]
    if unit:
        props.append(("unitText", ("str", unit)))
    if source:
        props.append(("description", ("str", source)))
    return {"id": f"{base}#{slug}", "type": "PropertyValue", "props": props}


def build_model(r):
    base = ID_BASE + r["UNITID"]
    web = r["web_url"].strip()
    if web and not web.startswith("http"):
        web = "https://" + web

    props = [("name", ("str", r["name"]))]
    props += [("alternateName", ("str", a)) for a in split_aliases(r["alias"])]
    if web:
        props.append(("url", ("iri", web)))

    props.append(("address", ("node", {
        "id": f"{base}#address", "type": "PostalAddress", "props": [
            ("streetAddress", ("str", r["address"])),
            ("addressLocality", ("str", r["city"])),
            ("addressRegion", ("str", r["state"])),
            ("postalCode", ("str", r["zip"])),
            ("addressCountry", ("str", "US")),
        ]})))
    props.append(("geo", ("node", {
        "id": f"{base}#geo", "type": "GeoCoordinates", "props": [
            ("latitude", ("num", r["latitude"], "decimal")),
            ("longitude", ("num", r["longitude"], "decimal")),
        ]})))

    # Identifiers are strings: "00183000" must keep its leading zeros.
    props.append(("identifier", ("node", property_value(
        base, "unitid", "IPEDS UNITID", ("str", r["UNITID"])))))
    if r["opeid"]:
        props.append(("identifier", ("node", property_value(
            base, "opeid", "OPE ID", ("str", r["opeid"])))))

    # Measured facts. schema.org has no numberOfStudents or admissionRate on
    # CollegeOrUniversity, so they go in additionalProperty (allowed because
    # EducationalOrganization is also a CivicStructure, which is a Place).
    measures = [
        ("carnegie", "Carnegie Classification 2021: Basic",
         ("str", r["carnegie_basic_2021"]), None, "IPEDS HD2024 (C21BASIC)"),
        ("enrollment", "Total enrollment, fall 2024",
         number(r["enroll_total"]), None, "IPEDS EF2024A"),
        ("admit-rate", "Admission rate, fall 2024",
         number(r["admit_rate_pct"]), "percent", "IPEDS ADM2024 (admits / applicants)"),
        ("graduation-rate", "Graduation rate within 150% of normal time",
         number(r["gr4_rate_150_all_pct"]), "percent", "IPEDS GR2024, 2018 cohort"),
        ("retention-rate", "Full-time retention rate, fall 2024",
         number(r["retention_rate_ft_pct"]), "percent", "IPEDS EF2024D"),
        ("student-faculty-ratio", "Student-to-faculty ratio (x:1)",
         number(r["student_faculty_ratio"]), None, "IPEDS EF2024D"),
    ]
    for slug, name, val, unit, src in measures:
        if val is None or (val[0] == "str" and not val[1]):
            continue
        if val[0] != "str":
            val = ("num", val[0], val[1])
        props.append(("additionalProperty", ("node", property_value(
            base, slug, name, val, unit, src))))

    return {"id": base, "type": "CollegeOrUniversity", "props": props}


def walk(node):
    """Yield every node in the model, depth first."""
    yield node
    for _, v in node["props"]:
        if v[0] == "node":
            yield from walk(v[1])


# ---------------------------------------------------------------------------
# 3. Reference graph, built straight from the model (no parsing)
# ---------------------------------------------------------------------------

def to_graph(model):
    g = Graph()
    s = Namespace(SCHEMA)
    for n in walk(model):
        subj = URIRef(n["id"])
        g.add((subj, RDF.type, s[n["type"]]))
        for p, v in n["props"]:
            if v[0] == "str":
                o = Literal(v[1])
            elif v[0] == "num":
                o = Literal(v[1], datatype=XSD[v[2]])
            elif v[0] == "iri":
                o = URIRef(v[1])
            else:
                o = URIRef(v[1]["id"])
            g.add((subj, s[p], o))
    return g


# ---------------------------------------------------------------------------
# 4. The six syntaxes
# ---------------------------------------------------------------------------

JSONLD_CONTEXT = {
    "@vocab": SCHEMA,
    "xsd": str(XSD),
    "url": {"@type": "@id"},
}


def jsonld_node(n):
    out = {"@id": n["id"], "@type": n["type"]}
    for p, v in n["props"]:
        if v[0] == "str":
            val = v[1]
        elif v[0] == "num" and v[2] == "integer":
            val = int(v[1])  # JSON integers map to xsd:integer
        elif v[0] == "num":
            # JSON numbers with a fraction become xsd:double, so decimals are
            # written as typed value objects to keep them xsd:decimal.
            val = {"@value": v[1], "@type": "xsd:decimal"}
        elif v[0] == "iri":
            val = v[1]  # coerced to an IRI by "url": {"@type": "@id"}
        else:
            val = jsonld_node(v[1])
        if p in out:
            out[p] = out[p] if isinstance(out[p], list) else [out[p]]
            out[p].append(val)
        else:
            out[p] = val
    return out


def to_jsonld(model, indent=2):
    doc = {"@context": JSONLD_CONTEXT, **jsonld_node(model)}
    return json.dumps(doc, indent=indent, ensure_ascii=False)


def to_jsonl(models):
    """One complete, self-contained JSON-LD document per line."""
    return "\n".join(to_jsonld(m, indent=None) for m in models) + "\n"


def esc(s):
    return html.escape(s, quote=True)


def microdata_node(n, prop=None, depth=0):
    pad = "  " * depth
    attr = f' itemprop="{prop}"' if prop else ""
    lines = [f'{pad}<div{attr} itemscope itemtype="{SCHEMA}{n["type"]}" itemid="{n["id"]}">']
    for p, v in n["props"]:
        ip = pad + "  "
        if v[0] == "str":
            lines.append(f'{ip}<span itemprop="{p}">{esc(v[1])}</span>')
        elif v[0] == "num":
            # Microdata has no datatypes: this value will parse as a plain string.
            lines.append(f'{ip}<data itemprop="{p}" value="{v[1]}">{v[1]}</data>')
        elif v[0] == "iri":
            lines.append(f'{ip}<a itemprop="{p}" href="{esc(v[1])}">{esc(v[1])}</a>')
        else:
            lines += microdata_node(v[1], p, depth + 1)
    lines.append(f"{pad}</div>")
    return lines


def rdfa_node(n, prop=None, depth=0):
    pad = "  " * depth
    attr = f' property="{prop}"' if prop else ""
    lines = [f'{pad}<div{attr} resource="{n["id"]}" typeof="{n["type"]}">']
    for p, v in n["props"]:
        ip = pad + "  "
        if v[0] == "str":
            lines.append(f'{ip}<span property="{p}">{esc(v[1])}</span>')
        elif v[0] == "num":
            lines.append(f'{ip}<span property="{p}" content="{v[1]}" datatype="xsd:{v[2]}">{v[1]}</span>')
        elif v[0] == "iri":
            lines.append(f'{ip}<a property="{p}" href="{esc(v[1])}">{esc(v[1])}</a>')
        else:
            lines += rdfa_node(v[1], p, depth + 1)
    lines.append(f"{pad}</div>")
    return lines


def html_page(title, body_lines, root_attrs=""):
    return "\n".join([
        "<!DOCTYPE html>",
        f'<html lang="en"{root_attrs}>',
        "<head>",
        '  <meta charset="utf-8">',
        f"  <title>{esc(title)}</title>",
        "</head>",
        "<body>",
        *["  " + line for line in body_lines],
        "</body>",
        "</html>",
        "",
    ])


def to_microdata(model):
    return html_page(model_name(model) + " (Microdata)", microdata_node(model))


def to_rdfa(model):
    body = [f'<div vocab="{SCHEMA}" prefix="xsd: {XSD}">'] + \
           ["  " + line for line in rdfa_node(model)] + ["</div>"]
    return html_page(model_name(model) + " (RDFa)", body)


def to_turtle(model):
    g = to_graph(model)
    g.bind("schema", Namespace(SCHEMA))
    g.bind("inst", Namespace(model["id"] + "#"))
    g.bind("xsd", XSD)
    return g.serialize(format="turtle")


def to_ntriples(model):
    lines = to_graph(model).serialize(format="nt").strip().splitlines()
    return "\n".join(sorted(lines)) + "\n"


def model_name(model):
    return next(v[1] for p, v in model["props"] if p == "name")


FORMATS = {
    "jsonld": ("institution.jsonld", to_jsonld),
    "microdata": ("institution.microdata.html", to_microdata),
    "rdfa": ("institution.rdfa.html", to_rdfa),
    "turtle": ("institution.ttl", to_turtle),
    "ntriples": ("institution.nt", to_ntriples),
}
JSONL_FILE = "institutions.jsonl"


def main(unitid=DEFAULT_UNITID):
    OUT.mkdir(exist_ok=True)
    rows = load_rows()
    model = build_model(rows[unitid])
    for key, (fname, fn) in FORMATS.items():
        (OUT / fname).write_text(fn(model), encoding="utf-8")
    # JSONL earns its keep at scale, so it holds every institution in the sample.
    models = [build_model(r) for r in rows.values()]
    (OUT / JSONL_FILE).write_text(to_jsonl(models), encoding="utf-8")
    print(f"Built {model_name(model)} (UNITID {unitid}) in 6 syntaxes -> {OUT}")
    print(f"Reference graph: {len(to_graph(model))} triples; "
          f"{JSONL_FILE}: {len(models)} lines")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_UNITID)
