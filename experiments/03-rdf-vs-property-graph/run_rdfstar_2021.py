"""Run star.ttl and the star queries in a 2021 RDF-star engine.

The RDF-star Community Group report (2021) treats << s p o >> as a quoted
triple: one term, identified only by its subject, predicate and object.
Every annotation on that triple attaches to the same term. RDF 1.2 reads the
same Turtle as "a fresh reifier for each << >>", so each annotation stays
separate. Oxigraph implemented the 2021 semantics up to 0.4 and RDF 1.2 from
0.5, which makes it a clean way to run one file under both readings.

This script needs its own environment with the older Oxigraph:

    python -m venv .venv-rdfstar
    source .venv-rdfstar/bin/activate
    pip install -r requirements-rdfstar-2021.txt
    python run_rdfstar_2021.py

Run it after run.py (which writes .work/star.ttl); run.py's report picks up
the result the next time it runs, and viz.py includes it.
"""

import json
import sys
from importlib.metadata import version
from pathlib import Path

from build import EXAMPLE, EXAMPLES, OUT, WORK, load, write_graphs
from run import q1_for

HERE = Path(__file__).resolve().parent
Q = HERE / "queries"


def main():
    import pyoxigraph as ox
    v = version("pyoxigraph")
    if not v.startswith(("0.3.", "0.4.")):
        sys.exit(f"pyoxigraph {v} implements RDF 1.2. Install requirements-rdfstar-2021.txt "
                 "in a separate environment to run the 2021 RDF-star semantics.")
    rows = load()
    path = WORK / "star.ttl"
    if not path.exists():
        write_graphs(rows)
    store = ox.Store()
    store.bulk_load(str(path), "text/turtle")

    def run(q):
        return [[None if x is None else int(x.value) for x in sol] for sol in store.query(q)]

    q1 = sorted(r[0] for r in run((Q / "q1" / "star.rq").read_text()))
    q2 = dict(sorted({int(l): int(t) for l, t in run((Q / "q2" / "star.rq").read_text())}.items()))
    truth = json.loads((OUT / "results.json").read_text())["truth"]
    t2 = {int(k): v for k, v in truth["q2"].items()}
    # What the example quoted triple carries: every level and every count
    ex = run(f"""PREFIX kgn: <https://knowledgegraphnavigator.com/vocab/ipeds#>
        PREFIX ipeds: <https://knowledgegraphnavigator.com/id/ipeds/>
        PREFIX cip: <https://knowledgegraphnavigator.com/id/ipeds/cip/>
        SELECT ?level ?n WHERE {{ << ipeds:{EXAMPLE[0]} kgn:conferredIn cip:{EXAMPLE[1]} >>
            kgn:awardLevelCode ?level ; kgn:completions ?n }} ORDER BY ?level ?n""")
    text = (Q / "q1" / "star.rq").read_text()
    examples = {f"{u}|{c}": sorted(r[0] for r in run(q1_for(text, u, c, lvl))) for u, c, _, lvl in EXAMPLES}
    out = {"engine": f"pyoxigraph {v}", "size": {"triples": len(store), "turtle_bytes": path.stat().st_size},
           "q1": q1, "q2": q2, "q1_ok": q1 == truth["q1"], "q2_ok": q2 == t2, "example_pairs": ex, "examples": examples}
    (OUT / "rdfstar-2021.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"{out['engine']}: {len(store):,} triples")
    print(f"Q1 (truth {truth['q1']}): {q1}")
    print(f"Q2 total (truth {sum(t2.values()):,}): {sum(q2.values()):,}")
    print(f"Example quoted triple returns {len(ex)} level x count combinations: {ex}")


if __name__ == "__main__":
    main()
