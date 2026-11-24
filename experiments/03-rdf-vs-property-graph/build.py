"""Experiment 3: Where Does the Number Go? RDF vs. Property Graphs.

Each row of programs-v1.0.csv is one fact about a relationship: institution X
conferred N awards at award level L in CIP code C during 2023-24. The count
belongs to neither the school nor the program. This script writes that fact
in five models:

  pg            labeled property graph (Kuzu): the count is a property on the
                edge  (:Institution)-[:CONFERRED {...}]->(:Cip)
  nary          RDF with an intermediate node: one "offering" node per row
  reification   RDF 1.1 standard reification: one rdf:Statement per row
  star          RDF-star annotation syntax:  << school conferredIn cip >> ...
                The same file means different things in a 2021 RDF-star
                engine and an RDF 1.2 engine (see run.py and run_rdfstar_2021.py)
  reifier       RDF 1.2 with a named reifier per row:
                school conferredIn cip ~ <offering> {| ... |}
  reifier-pair  the same, with the reifier named for the school x CIP pair
                instead of the row: a slip that recreates the 2021 problem

Full graphs go to .work/ (not committed). One example relationship from each
model goes to output/sample/ for reading.
"""

import csv
import shutil
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent.parent / "data"
OUT = HERE / "output"
WORK = HERE / ".work"  # generated graphs and databases; not committed

SCHEMA = "https://schema.org/"
KGN = "https://knowledgegraphnavigator.com/vocab/ipeds#"
ID = "https://knowledgegraphnavigator.com/id/ipeds/"

PREFIXES = (f"@prefix schema: <{SCHEMA}> .\n@prefix kgn: <{KGN}> .\n"
            f"@prefix ipeds: <{ID}> .\n@prefix cip: <{ID}cip/> .\n"
            f"@prefix offering: <{ID}offering/> .\n"
            "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n\n")

MODELS = ["pg", "nary", "reification", "star", "reifier", "reifier-pair"]

# Example relationship used in samples, queries and the visualization:
# Arizona State University Campus Immersion x CIP 11.0701 (Computer Science)
EXAMPLE = ("104151", "11.0701")

# Relationships shown in the visualization: (unitid, CIP code, CIP 2020 title,
# award level asked about). The first has three award levels, the second two,
# the third one, which is the only case where every model agrees.
EXAMPLES = [
    ("104151", "11.0701", "Computer Science", 5),
    ("104151", "42.0101", "Psychology, General", 5),
    ("104151", "52.0801", "Finance, General", 5),
]


def load():
    """One dict per programs row (UNITID x CIP code x award level)."""
    names = {}
    with open(DATA / "institutions-v1.0.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            names[r["UNITID"]] = r["name"]
    rows = []
    with open(DATA / "programs-v1.0.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "unitid": r["UNITID"],
                "name": names[r["UNITID"]],
                "cipcode": r["cipcode"],
                "cip2": r["cip_2digit"],
                "family": r["cip_family"],
                "level": int(r["awlevel_code"]),
                "award_level": r["award_level"],
                "completions": int(float(r["completions_total"] or 0)),
            })
    return rows


def lit(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def inst(u):
    return f"ipeds:{u}"


def cip(c):
    return f"cip:{c}"


def offering(r):
    return f"offering:{r['unitid']}-{r['cipcode']}-{r['level']}"


def base(rows):
    """Triples every RDF model shares: names for schools and CIP codes."""
    out, seen = [], set()
    for r in rows:
        if r["unitid"] not in seen:
            seen.add(r["unitid"])
            out.append(f"{inst(r['unitid'])} a schema:CollegeOrUniversity ; schema:name {lit(r['name'])} .")
        if r["cipcode"] not in seen:
            seen.add(r["cipcode"])
            out.append(f"{cip(r['cipcode'])} a kgn:Cip ; kgn:cipCode {lit(r['cipcode'])} ; kgn:cipFamily {lit(r['family'])} .")
    return out


def facts(rows, model):
    """The model-specific statements, as Turtle lines."""
    out, asserted = [], set()

    def assert_once(r):  # the plain edge, stated once per school x CIP pair
        key = (r["unitid"], r["cipcode"])
        if key not in asserted:
            asserted.add(key)
            out.append(f"{inst(r['unitid'])} kgn:conferredIn {cip(r['cipcode'])} .")

    for r in rows:
        ann = f"kgn:awardLevelCode {r['level']} ; kgn:completions {r['completions']}"
        if model == "nary":
            out.append(f"{offering(r)} a schema:EducationalOccupationalProgram ;\n"
                       f"    schema:provider {inst(r['unitid'])} ;\n    kgn:cip {cip(r['cipcode'])} ;\n    {ann} .")
        elif model == "reification":
            assert_once(r)
            out.append(f"{offering(r)} a rdf:Statement ;\n    rdf:subject {inst(r['unitid'])} ;\n"
                       f"    rdf:predicate kgn:conferredIn ;\n    rdf:object {cip(r['cipcode'])} ;\n    {ann} .")
        elif model == "star":
            assert_once(r)
            out.append(f"<< {inst(r['unitid'])} kgn:conferredIn {cip(r['cipcode'])} >> {ann} .")
        elif model in ("reifier", "reifier-pair"):
            # reifier-pair is a deliberate slip: the reifier is named for the
            # school x CIP pair, so rows at different award levels share it
            rid = offering(r) if model == "reifier" else f"offering:{r['unitid']}-{r['cipcode']}"
            out.append(f"{inst(r['unitid'])} kgn:conferredIn {cip(r['cipcode'])} ~ {rid}\n"
                       f"    {{| {ann} |}} .")
    return out


def turtle(rows, model):
    return PREFIXES + "\n".join(base(rows) + [""] + facts(rows, model)) + "\n"


def write_graphs(rows):
    """Full Turtle files in .work/, one example relationship in output/sample/."""
    WORK.mkdir(exist_ok=True)
    (OUT / "sample").mkdir(parents=True, exist_ok=True)
    example = [r for r in rows if (r["unitid"], r["cipcode"]) == EXAMPLE]
    paths = {}
    for m in MODELS[1:]:
        paths[m] = WORK / f"{m}.ttl"
        paths[m].write_text(turtle(rows, m), encoding="utf-8")
        (OUT / "sample" / f"{m}.ttl").write_text(turtle(example, m), encoding="utf-8")
    (OUT / "sample" / "pg.cypher").write_text(cypher_sample(example), encoding="utf-8")
    return paths


def cypher_sample(rows):
    r0 = rows[0]
    lines = [f"MERGE (i:Institution {{unitid: '{r0['unitid']}', name: {lit(r0['name'])}}})",
             f"MERGE (c:Cip {{code: '{r0['cipcode']}', family: {lit(r0['family'])}}})"]
    for r in rows:
        lines.append(f"CREATE (i)-[:CONFERRED {{awardLevelCode: {r['level']}, completions: {r['completions']}}}]->(c)")
    return "\n".join(lines) + ";\n"


def kuzu_db(rows):
    """The property graph: two node tables and one relationship table."""
    import kuzu
    path = WORK / "kuzu"
    if path.exists():
        shutil.rmtree(path) if path.is_dir() else path.unlink()
    WORK.mkdir(exist_ok=True)
    stage = WORK / "csv"
    stage.mkdir(exist_ok=True)

    def dump(name, items):
        p = stage / f"{name}.csv"
        with open(p, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(items)
        return p.as_posix()

    schools = {r["unitid"]: r["name"] for r in rows}
    cips = {r["cipcode"]: r["family"] for r in rows}
    con = kuzu.Connection(kuzu.Database(str(path)))
    con.execute("CREATE NODE TABLE Institution(unitid STRING, name STRING, PRIMARY KEY(unitid))")
    con.execute("CREATE NODE TABLE Cip(code STRING, family STRING, PRIMARY KEY(code))")
    con.execute("CREATE REL TABLE CONFERRED(FROM Institution TO Cip, awardLevelCode INT64, completions INT64)")
    con.execute(f"COPY Institution FROM '{dump('inst', schools.items())}' (HEADER=false)")
    con.execute(f"COPY Cip FROM '{dump('cip', cips.items())}' (HEADER=false)")
    con.execute(f"COPY CONFERRED FROM '{dump('conf', [(r['unitid'], r['cipcode'], r['level'], r['completions']) for r in rows])}' (HEADER=false)")
    return con


def pairs_with_several_levels(rows):
    by = defaultdict(set)
    for r in rows:
        by[(r["unitid"], r["cipcode"])].add(r["level"])
    multi = [k for k, v in by.items() if len(v) > 1]
    return len(by), len(multi), sum(len(by[k]) for k in multi)


if __name__ == "__main__":
    rows = load()
    pairs, multi, multi_rows = pairs_with_several_levels(rows)
    print(f"{len(rows)} rows; {pairs} school x CIP pairs, {multi} with more than one award level "
          f"({multi_rows} rows)")
    for m, p in write_graphs(rows).items():
        print(f"{m:12} {p.stat().st_size / 1e6:5.1f} MB  {p}")
    con = kuzu_db(rows)
    n = con.execute("MATCH (n) RETURN count(n)").get_next()[0]
    e = con.execute("MATCH ()-[r]->() RETURN count(r)").get_next()[0]
    print(f"pg           {n} nodes, {e} edges")
