"""Run the question in SQL, SPARQL and Cypher, then compare the answers.

The same three queries are also run under two alternative modeling choices,
to show that the answer moves with the definitions, not with the language:

  baseline     "fully online" = at least one program offered fully via
               distance education; "six-year graduation rate" = all
               degree/certificate-seeking students, 150% of normal time
  bachelors    same, but using the bachelor's-seeking cohort's rate
  any-online   same as baseline, but "online" also counts programs with
               only some distance-education component

Usage:
    python run.py
"""

import json
from pathlib import Path

from build import OUT, cypher_db, load, rdf_graph, sql_db

HERE = Path(__file__).resolve().parent
Q = HERE / "queries"

QUERIES = {
    "SQL": (Q / "question.sql").read_text(),
    "SPARQL": (Q / "question.rq").read_text(),
    "Cypher": (Q / "question.cypher").read_text(),
}

# Each variant is a set of text substitutions applied to every query.
VARIANTS = {
    "baseline": {
        "label": "Fully online programs; all-student six-year rate",
        "edits": {},
    },
    "bachelors": {
        "label": "Fully online programs; bachelor's-seeking six-year rate",
        "edits": {
            "SQL": [("gr4_rate_150_all_pct", "gr4_rate_150_bach_pct")],
            "SPARQL": [("kgn:gradRate150All", "kgn:gradRate150Bach")],
            "Cypher": [("gradRate150All", "gradRate150Bach")],
        },
    },
    "any-online": {
        "label": "Fully or partly online programs; all-student six-year rate",
        "edits": {
            "SQL": [("p.programs_offered_fully_distance > 0     -- offered fully online",
                     "(p.programs_offered_fully_distance > 0 OR p.programs_offered_some_distance > 0)")],
            "SPARQL": [("kgn:fullyDistancePrograms ?online .",
                        "kgn:fullyDistancePrograms ?full ;\n           kgn:someDistancePrograms ?some ."),
                       ("FILTER (?online > 0 &&", "FILTER ((?full + ?some) > 0 &&")],
            "Cypher": [("o.fullyDistance > 0", "(o.fullyDistance > 0 OR o.someDistance > 0)")],
        },
    },
}


# Small edits to how the question is *written* (not what it means) that move
# the answer a lot, or make the languages disagree. Each one is a typo-sized
# change a careful analyst could still make. "na" marks a language where the
# mistake can't be expressed against this data model.
TRAPS = {
    "quoted-code": {
        "label": "Write the CIP code as a number: 51 instead of '51'",
        "edits": {
            "SQL": [("p.cip_2digit = '51'", "p.cip_2digit = 51")],
            "SPARQL": [('kgn:cipCode              "51" .', "kgn:cipCode              51 .")],
            "Cypher": [("{code: '51'}", "{code: 51}")],
        },
        "why": "The code is stored as text. DuckDB and Kuzu quietly convert 51 to '51' and still "
               "return the right schools. SPARQL compares RDF terms, so the integer 51 never matches "
               "the string \"51\": it returns nothing, with no error.",
    },
    "proportion": {
        "label": "Write the threshold as a proportion: > 0.6 instead of > 60",
        "edits": {
            "SQL": [("AND o.gr4_rate_150_all_pct > 60", "AND o.gr4_rate_150_all_pct > 0.6")],
            "SPARQL": [("?gradRate6yr > 60)", "?gradRate6yr > 0.6)")],
            "Cypher": [("i.gradRate150All > 60", "i.gradRate150All > 0.6")],
        },
        "why": "IPEDS rates are stored as percents (0-100). Every school with a rate clears 0.6.",
    },
    "optional-filter": {
        "label": "Put the rate condition inside an outer join or OPTIONAL block",
        "edits": {
            "SQL": [("JOIN outcomes      AS o ON o.UNITID = p.UNITID",
                     "LEFT JOIN outcomes AS o ON o.UNITID = p.UNITID AND o.gr4_rate_150_all_pct > 60"),
                    ("  AND o.gr4_rate_150_all_pct > 60               -- 150% of normal time = 6 years\n", "")],
            "SPARQL": [("kgn:unitid               ?unitid ;\n           kgn:gradRate150All       ?gradRate6yr .",
                        "kgn:unitid               ?unitid .\n  OPTIONAL { ?school kgn:gradRate150All ?gradRate6yr . FILTER (?gradRate6yr > 60) }"),
                       ("FILTER (?online > 0 && ?gradRate6yr > 60)", "FILTER (?online > 0)")],
        },
        "na": {"Cypher": "The rate is a property on the Institution node, so there is no optional match to misplace it in.",
               "GQL": "The rate is a property on the Institution node, so there is no optional match to misplace it in."},
        "why": "A condition inside an outer join or OPTIONAL only decides whether the optional part "
               "attaches. Schools below 60% stay in the answer with a blank rate.",
    },
    "negation": {
        "label": "Ask the opposite: which schools do NOT clear 60%?",
        "edits": {
            "SQL": [("AND o.gr4_rate_150_all_pct > 60", "AND NOT (o.gr4_rate_150_all_pct > 60)")],
            "SPARQL": [("kgn:unitid               ?unitid ;\n           kgn:gradRate150All       ?gradRate6yr .",
                        "kgn:unitid               ?unitid .\n  OPTIONAL { ?school kgn:gradRate150All ?gradRate6yr }\n"
                        "  FILTER NOT EXISTS { ?school kgn:gradRate150All ?r . FILTER (?r > 60) }"),
                       ("FILTER (?online > 0 && ?gradRate6yr > 60)", "FILTER (?online > 0)")],
            "Cypher": [("AND i.gradRate150All > 60", "AND NOT (i.gradRate150All > 60)")],
        },
        "why": "Each query uses its language's usual negation. SQL and Cypher evaluate NOT (NULL > 60) "
               "as unknown and drop the school with no rate. SPARQL's NOT EXISTS asks whether a "
               "matching rate exists, finds none, and keeps it.",
    },
}


def apply(lang, text, variant, table=None):
    spec = (table or VARIANTS)[variant]
    for old, new in spec["edits"].get(lang, []):
        assert old in text, f"{lang}/{variant}: '{old}' not found"
        text = text.replace(old, new)
    return text


def normalize(rows):
    """(unitid, institution, rate, count) with consistent types, sorted."""
    out = [(str(u), str(n), None if r in (None, "") else round(float(r), 1), int(c)) for u, n, r, c in rows]
    return sorted(out, key=lambda x: (-(x[2] if x[2] is not None else -1), x[0]))


def run_sql(con, q):
    return con.execute(q).fetchall()


def run_sparql(g, q):
    return [(r[0], r[1], None if r[2] is None else r[2].toPython(), r[3].toPython()) for r in g.query(q)]


def run_cypher(con, q):
    res, rows = con.execute(q), []
    while res.has_next():
        rows.append(res.get_next())
    return rows


def candidates(institutions, offerings):
    """Every school with at least one partly or fully online health master's,
    with what each variant decides about it. Feeds the visualization."""
    by = {}
    for o in offerings:
        if o["cip2"] == "51" and o["awlevel_code"] == 7 and (o["fully_distance"] or o["some_distance"]):
            b = by.setdefault(o["unitid"], {"fully": 0, "some": 0, "cips": []})
            b["fully"] += 1 if o["fully_distance"] else 0
            b["some"] += 1 if (o["some_distance"] and not o["fully_distance"]) else 0
            b["cips"].append({"cip": o["cipcode"], "mode": "fully" if o["fully_distance"] else "some"})
    inst = {i["unitid"]: i for i in institutions}
    return [{"unitid": u, "name": inst[u]["name"], "sector": inst[u]["sector"],
             "rateAll": inst[u]["grad_rate_150_all"], "rateBach": inst[u]["grad_rate_150_bach"], **b}
            for u, b in sorted(by.items())]


def main():
    institutions, offerings, cip = load()
    engines = {
        "SQL": (run_sql, sql_db()),
        "SPARQL": (run_sparql, rdf_graph(institutions, offerings, cip)),
        "Cypher": (run_cypher, cypher_db(institutions, offerings, cip)),
    }
    results = {}
    for v in VARIANTS:
        results[v] = {}
        for lang, (fn, store) in engines.items():
            results[v][lang] = normalize(fn(store, apply(lang, QUERIES[lang], v)))

    traps = {}
    for t, spec in TRAPS.items():
        traps[t] = {}
        for lang, (fn, store) in engines.items():
            if lang in spec.get("na", {}):
                traps[t][lang] = {"na": spec["na"][lang]}
                continue
            try:
                traps[t][lang] = {"rows": normalize(fn(store, apply(lang, QUERIES[lang], t, TRAPS)))}
            except Exception as e:  # an error is a result too
                traps[t][lang] = {"error": f"{type(e).__name__}: {str(e).splitlines()[0][:160]}"}

    lines = ["# Results: one question, four query languages", "",
             "Question: *Which schools offer a fully online master's in the health professions "
             "and graduate more than 60% of their students within six years?*", ""]
    all_agree = True
    for v, spec in VARIANTS.items():
        answers = results[v]
        agree = len({json.dumps(a) for a in answers.values()}) == 1
        all_agree &= agree
        base = answers["SQL"]
        lines += [f"## {v}: {spec['label']}", "",
                  f"SQL, SPARQL and Cypher return {'the same' if agree else 'DIFFERENT'} "
                  f"{len(base)} schools.", "",
                  "| Institution | Six-year rate (%) | Online health master's fields |", "|---|---|---|"]
        lines += [f"| {n} | {r} | {c} |" for _, n, r, c in base]
        if not agree:
            for lang, a in answers.items():
                lines.append(f"\n{lang}: {[x[0] for x in a]}")
        lines.append("")

    b = {x[0] for x in results["baseline"]["SQL"]}
    for v in ["bachelors", "any-online"]:
        s = {x[0] for x in results[v]["SQL"]}
        inst = {i["unitid"]: i["name"] for i in institutions}
        lines.append(f"- **{v} vs baseline:** "
                     + (f"drops {', '.join(inst[u] for u in sorted(b - s))}" if b - s else "drops none")
                     + "; "
                     + (f"adds {', '.join(inst[u] for u in sorted(s - b))}" if s - b else "adds none") + ".")
    lines.append("")
    base_n = len(results["baseline"]["SQL"])
    lines += ["## Small edits, big discrepancies", "",
              f"Each row is one typo-sized change to how the strict question is written. Baseline: {base_n} schools.", "",
              "| Edit | SQL | SPARQL | Cypher |", "|---|---|---|---|"]
    def cell(r):
        if "rows" in r: return str(len(r["rows"]))
        if "error" in r: return "error"
        return "n/a"
    for t, spec in TRAPS.items():
        lines.append(f"| {spec['label']} | " + " | ".join(cell(traps[t][l]) for l in engines) + " |")
    lines.append("")
    for t, spec in TRAPS.items():
        lines.append(f"- **{spec['label'].rstrip('?.')}.** {spec['why']}")
        for l in engines:
            if "error" in traps[t][l]:
                lines.append(f"  - {l} error: `{traps[t][l]['error']}`")
    lines.append("")
    report = "\n".join(lines)

    OUT.mkdir(exist_ok=True)
    (OUT / "results.md").write_text(report, encoding="utf-8")
    (OUT / "results.json").write_text(json.dumps({
        "variants": {v: {"label": s["label"], "answers": results[v]} for v, s in VARIANTS.items()},
        "queries": {**{k: v for k, v in QUERIES.items()}, "GQL": (Q / "question.gql").read_text()},
        "candidates": candidates(institutions, offerings),
        "traps": {t: {"label": s_["label"], "why": s_["why"], "results": traps[t]} for t, s_ in TRAPS.items()},
    }, indent=2), encoding="utf-8")
    print(report)
    return all_agree


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
