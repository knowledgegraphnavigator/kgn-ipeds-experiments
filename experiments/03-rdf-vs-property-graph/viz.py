"""Build viz/index.html: the same relationship drawn in each model.

Run after run.py (and run_rdfstar_2021.py, if you ran it).
"""

import json
from pathlib import Path

from build import EXAMPLES, OUT, cypher_sample, load, turtle
from run import QUERY_FILE, q1_for

HERE = Path(__file__).resolve().parent
VIZ = HERE / "viz"
Q = HERE / "queries"

# Cards, in display order: (key in results, model used to write the data, engine)
CARDS = [
    ("pg", "pg", "Kùzu 0.11.3 · Cypher"),
    ("nary", "nary", "Oxigraph 0.5 · SPARQL"),
    ("reification", "reification", "Oxigraph 0.5 · SPARQL"),
    ("reifier", "reifier", "Oxigraph 0.5 · SPARQL 1.2"),
    ("star", "star", "Oxigraph 0.5 · SPARQL 1.2"),
    ("star-2021", "star", "Oxigraph 0.3.22 · SPARQL-star"),
]


def short(level):
    return (level.replace(" degree - research/scholarship", " (research)")
                 .replace(" degree - professional practice", " (professional)")
                 .replace(" degree - other", " (other)").replace(" degree", "")
                 .replace("Certificate of ", "Cert. ").replace("Postbaccalaureate certificate", "Postbacc. cert.")
                 .replace("Post-master's certificate", "Post-master's cert."))


def strip_prefixes(text):
    return "\n".join(l for l in text.splitlines() if not l.startswith("@prefix")).strip() + "\n"


def strip_query_header(text):
    return "\n".join(l for l in text.splitlines() if not l.startswith(("#", "//", "PREFIX"))).strip() + "\n"


def main():
    rows = load()
    res = json.loads((OUT / "results.json").read_text())
    models = dict(res["models"])
    star21 = OUT / "rdfstar-2021.json"
    if star21.exists():
        e = json.loads(star21.read_text())
        models["star-2021"] = {"label": "RDF-star 2021: << >> annotation syntax", **e}
    cards = []
    for key, model, engine in CARDS + [("reifier-pair", "reifier-pair", "Oxigraph 0.5 · SPARQL 1.2")]:
        m = models.get(key)
        code, query = {}, {}
        for u, c, _, lvl in EXAMPLES:
            ex = [r for r in rows if (r["unitid"], r["cipcode"]) == (u, c)]
            code[f"{u}|{c}"] = cypher_sample(ex) if model == "pg" else strip_prefixes(turtle(ex, model))
            query[f"{u}|{c}"] = strip_query_header(q1_for((Q / "q1" / QUERY_FILE[model]).read_text(), u, c, lvl))
        cards.append({"key": key, "engine": engine, "ran": m is not None,
                      "size": m["size"] if m else None, "answers": m["examples"] if m else None,
                      "q1": m["q1"] if m else None, "q2total": sum(m["q2"].values()) if m else None,
                      "code": code, "query": query})
    data = {"examples": [{**e, "rows": [{**r, "short": short(r["award_level"])} for r in e["rows"]]}
                         for e in res["examples"]],
            "truth": {"q1": res["truth"]["q1"], "q2total": sum(res["truth"]["q2"].values())},
            "pairs": res["pairs"], "cards": cards,
            "example_pairs_2021": models.get("star-2021", {}).get("example_pairs")}
    VIZ.mkdir(exist_ok=True)
    page = (HERE / "viz_template.html").read_text(encoding="utf-8")
    page = page.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    (VIZ / "index.html").write_text(page, encoding="utf-8")
    print(f"Wrote {VIZ / 'index.html'}" + ("" if star21.exists() else " (no 2021 RDF-star results yet)"))


if __name__ == "__main__":
    main()
