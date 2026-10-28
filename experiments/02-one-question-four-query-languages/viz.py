"""Build viz/index.html: four query tabs beside the graph of candidate schools.

Pick a modeling variant to see which lines of each query change and which
schools the answer gains or loses. Run after run.py.
"""

import json
from pathlib import Path

from run import QUERIES, TRAPS, VARIANTS, apply

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
VIZ = HERE / "viz"
GQL = (HERE / "queries" / "question.gql").read_text()

# Display labels for the graph; full names appear in tooltips and the table.
SHORT = {
    "California State University-Northridge": "CSUN", "San Jose State University": "San Jose State",
    "University of Southern California": "USC", "University of Central Florida": "UCF",
    "Keiser University-Ft Lauderdale": "Keiser", "DePaul University": "DePaul",
    "Southern New Hampshire University": "SNHU", "New York University": "NYU",
    "St. John's University-New York": "St. John's", "North Carolina A & T State University": "NC A&T",
    "Ohio State University-Main Campus": "Ohio State", "Baylor University": "Baylor",
    "Utah Valley University": "Utah Valley", "University of Washington-Seattle Campus": "UW Seattle",
    "NUC University": "NUC", "Western Governors University": "WGU",
    "American Public University System": "APUS", "Chamberlain University-Illinois": "Chamberlain",
    "Touro University California": "Touro California", "University of Phoenix-Arizona": "Phoenix",
}


def main():
    res = json.loads((OUT / "results.json").read_text())
    texts = {}
    for v in VARIANTS:
        texts[v] = {lang: apply(lang, q, v) for lang, q in QUERIES.items()}
        g = GQL
        for old, new in VARIANTS[v]["edits"].get("Cypher", []):  # same property names
            g = g.replace(old, new)
        texts[v]["GQL"] = g
    data = {
        "variants": {v: {"label": s["label"],
                         "answer": [r[0] for r in res["variants"][v]["answers"]["SQL"]],
                         "agree": len({json.dumps(a) for a in res["variants"][v]["answers"].values()}) == 1,
                         "texts": texts[v]}
                     for v, s in VARIANTS.items()},
        "candidates": [{**c, "short": SHORT.get(c["name"], c["name"])} for c in res["candidates"]],
        "gql": None,
    }
    gql_path = OUT / "gql-results.json"
    if gql_path.exists():  # written by run_gql.py
        g = json.loads(gql_path.read_text())
        data["gql"] = {"engine": g["engine"], "full": g["full_graph"],
                       "match": {v: g["answers"][v] == res["variants"][v]["answers"]["SQL"] for v in VARIANTS}}
    # Small edits that break the question: per-language text and answers
    gql_traps = data["gql"] and json.loads(gql_path.read_text()).get("traps", {})
    data["traps"] = {}
    for t, spec in TRAPS.items():
        texts_t = {lang: apply(lang, q, t, TRAPS) for lang, q in QUERIES.items()}
        g = GQL
        for old, new in spec["edits"].get("Cypher", []):
            g = g.replace(old, new)
        texts_t["GQL"] = g
        out = {}
        for lang, r in res["traps"][t]["results"].items():
            out[lang] = r
        out["GQL"] = (gql_traps or {}).get(t) or {"na": "Run run_gql.py with GraphLite installed to execute it."}
        data["traps"][t] = {
            "label": spec["label"], "why": spec["why"], "texts": texts_t,
            "results": {lang: ({"answer": [row[0] for row in r["rows"]], "n": len(r["rows"])} if "rows" in r else r)
                        for lang, r in out.items()},
        }
    VIZ.mkdir(exist_ok=True)
    page = (HERE / "viz_template.html").read_text(encoding="utf-8")
    page = page.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    (VIZ / "index.html").write_text(page, encoding="utf-8")
    print(f"Wrote {VIZ / 'index.html'} ({len(data['candidates'])} candidate schools)")


if __name__ == "__main__":
    main()
