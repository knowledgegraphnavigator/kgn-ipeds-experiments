"""Load every model, ask the same two questions of each, and compare.

  Q1  How many bachelor's degrees did Arizona State University Campus
      Immersion confer in CIP 11.0701 (Computer Science) in 2023-24?
  Q2  Total completions at each award level, across all 45 institutions.

The CSV is the ground truth for both. Engines: Kuzu (Cypher) for the property
graph and Oxigraph 0.5 (RDF 1.2, SPARQL 1.2) for the RDF models. The same
star.ttl file is also run in a 2021 RDF-star engine by run_rdfstar_2021.py;
run that afterwards to add its results.

Usage:
    python run.py
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

from build import EXAMPLE, EXAMPLES, MODELS, OUT, WORK, kuzu_db, load, pairs_with_several_levels, write_graphs

HERE = Path(__file__).resolve().parent
Q = HERE / "queries"

LABELS = {
    "pg": "Property graph: count on the edge",
    "nary": "RDF: intermediate offering node",
    "reification": "RDF 1.1: standard reification",
    "star": "RDF 1.2: << >> annotation syntax",
    "reifier": "RDF 1.2: named reifier per row",
    "reifier-pair": "RDF 1.2: reifier named for the pair (slip)",
}
QUERY_FILE = {"pg": "pg.cypher", "nary": "nary.rq", "reification": "reification.rq",
              "star": "star.rq", "reifier": "reifier.rq", "reifier-pair": "reifier.rq"}


def truth(rows):
    q1 = sorted(r["completions"] for r in rows
                if (r["unitid"], r["cipcode"]) == EXAMPLE and r["level"] == 5)
    q2 = defaultdict(int)
    for r in rows:
        q2[r["level"]] += r["completions"]
    return q1, dict(sorted(q2.items()))


def cypher(con, q):
    res, out = con.execute(q), []
    while res.has_next():
        out.append(res.get_next())
    return out


def sparql(store, q):
    return [[None if v is None else int(v.value) for v in sol] for sol in store.query(q)]


def q1_for(text, unitid, cipcode, level):
    """Q1 rewritten for another school, CIP code and award level."""
    for old, new in [("104151", unitid), ("11.0701", cipcode),
                     ("kgn:awardLevelCode 5", f"kgn:awardLevelCode {level}"),
                     ("awardLevelCode = 5", f"awardLevelCode = {level}")]:
        text = text.replace(old, new)
    return text


def examples(model, store, run):
    text = (Q / "q1" / QUERY_FILE[model]).read_text()
    return {f"{u}|{c}": sorted(r[0] for r in run(store, q1_for(text, u, c, lvl))) for u, c, _, lvl in EXAMPLES}


def ask(model, store):
    qs = [(Q / n / QUERY_FILE[model]).read_text() for n in ("q1", "q2")]
    run = cypher if model == "pg" else sparql
    q1 = sorted(r[0] for r in run(store, qs[0]))
    q2 = {int(l): int(t) for l, t in run(store, qs[1])}
    return q1, dict(sorted(q2.items()))


def main():
    import pyoxigraph as ox
    rows = load()
    paths = write_graphs(rows)
    t1, t2 = truth(rows)
    pairs, multi, multi_rows = pairs_with_several_levels(rows)
    ex_rows = {f"{u}|{c}": [{"level": r["level"], "award_level": r["award_level"], "completions": r["completions"]}
                            for r in rows if (r["unitid"], r["cipcode"]) == (u, c)]
               for u, c, _, _ in EXAMPLES}
    results = {"examples": [{"key": f"{u}|{c}", "unitid": u, "cip": c, "title": t, "level": lvl,
                             "school": next(r["name"] for r in rows if r["unitid"] == u), "rows": ex_rows[f"{u}|{c}"]}
                            for u, c, t, lvl in EXAMPLES],
               "engine": {"rdf": f"pyoxigraph {ox.__version__}"}, "truth": {"q1": t1, "q2": t2},
               "pairs": {"total": pairs, "several_levels": multi, "rows_affected": multi_rows,
                         "rows": len(rows)},
               "models": {}}
    for m in MODELS:
        if m == "pg":
            store = kuzu_db(rows)
            size = {"nodes": cypher(store, "MATCH (n) RETURN count(n)")[0][0],
                    "edges": cypher(store, "MATCH ()-[r]->() RETURN count(r)")[0][0]}
        else:
            store = ox.Store()
            store.bulk_load(path=str(paths[m]), format=ox.RdfFormat.TURTLE)
            size = {"triples": len(store), "turtle_bytes": paths[m].stat().st_size}
        q1, q2 = ask(m, store)
        results["models"][m] = {"label": LABELS[m], "size": size, "q1": q1, "q2": q2,
                                "q1_ok": q1 == t1, "q2_ok": q2 == t2,
                                "examples": examples(m, store, cypher if m == "pg" else sparql)}
    (OUT / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    report = write_report(results)
    print(report)
    return all(v["q1_ok"] and v["q2_ok"] for k, v in results["models"].items() if k != "reifier-pair")


def write_report(res):
    """results.md, including the 2021 RDF-star run if it has been made."""
    t1, t2 = res["truth"]["q1"], res["truth"]["q2"]
    rows = dict(res["models"])
    extra = OUT / "rdfstar-2021.json"
    if extra.exists():
        e = json.loads(extra.read_text())
        rows = {**{k: v for k, v in rows.items() if k != "reifier-pair"},
                "star-2021": {"label": f"RDF-star 2021: << >> annotation syntax ({e['engine']})", **e},
                "reifier-pair": rows["reifier-pair"]}
    t2_total = sum(t2.values())
    lines = ["# Results: where does the number go?", "",
             f"{res['pairs']['rows']} rows, one per school x CIP code x award level. "
             f"{res['pairs']['several_levels']} of {res['pairs']['total']} school x CIP pairs have more than one "
             f"award level ({res['pairs']['rows_affected']} rows).", "",
             f"Q1: bachelor's degrees at ASU Campus Immersion in CIP 11.0701. Truth: {t1}.",
             f"Q2: completions by award level, all schools. Truth: {t2_total:,} in total.", "",
             "| Model | Size | Q1 answer | Q1 | Q2 total | Q2 |", "|---|---|---|---|---|---|"]
    for k, v in rows.items():
        s = v["size"]
        size = f"{s['nodes']:,} nodes, {s['edges']:,} edges" if "nodes" in s else f"{s['triples']:,} triples"
        lines.append(f"| {v['label']} | {size} | {', '.join(map(str, v['q1']))} | "
                     f"{'✓' if v['q1_ok'] else '✗'} | {sum(v['q2'].values()):,} | {'✓' if v['q2_ok'] else '✗'} |")
    lines.append("")
    report = "\n".join(lines)
    (OUT / "results.md").write_text(report, encoding="utf-8")
    return report


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
