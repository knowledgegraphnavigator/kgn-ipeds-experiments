"""Experiment 2: One Question, Four Query Languages.

Loads the same IPEDS CSVs into three stores so one question can be asked
in SQL, SPARQL and Cypher (ISO GQL runs separately; see run_gql.py):

  SQL     -> DuckDB tables, straight from the CSVs
  SPARQL  -> an RDF graph (schema.org where it fits, a small kgn: vocabulary
             for IPEDS-specific fields), queried with rdflib
  Cypher  -> a labeled property graph in Kuzu, an embedded Cypher database

Every store is built from the same three files: institutions, outcomes and
programs (UNITID x CIP code x award level).
"""

import csv
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent.parent / "data"
OUT = HERE / "output"
WORK = HERE / ".work"  # generated databases; not committed

SCHEMA = "https://schema.org/"
KGN = "https://knowledgegraphnavigator.com/vocab/ipeds#"
ID = "https://knowledgegraphnavigator.com/id/ipeds/"


def read(name):
    with open(DATA / f"{name}-v1.0.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(s):
    s = (s or "").strip()
    return float(s) if s else None


def intval(s):
    s = (s or "").strip()
    return int(float(s)) if s else 0


def load():
    """Return (institutions, offerings, cip_families) as plain Python rows."""
    outcomes = {r["UNITID"]: r for r in read("outcomes")}
    institutions = []
    for r in read("institutions"):
        o = outcomes.get(r["UNITID"], {})
        institutions.append({
            "unitid": r["UNITID"],
            "name": r["name"],
            "state": r["state"],
            "sector": r["sector"],
            "grad_rate_150_all": num(o.get("gr4_rate_150_all_pct")),
            "grad_rate_150_bach": num(o.get("gr4_rate_150_bach_pct")),
        })
    offerings, families = [], {}
    for r in read("programs"):
        oid = f'{r["UNITID"]}-{r["cipcode"]}-{r["awlevel_code"]}'
        offerings.append({
            "id": oid,
            "unitid": r["UNITID"],
            "cipcode": r["cipcode"],
            "cip2": r["cip_2digit"],
            "awlevel_code": intval(r["awlevel_code"]),
            "award_level": r["award_level"],
            "fully_distance": intval(r["programs_offered_fully_distance"]),
            "some_distance": intval(r["programs_offered_some_distance"]),
            "completions": intval(r["completions_total"]),
        })
        families[r["cip_2digit"]] = r["cip_family"]
    cip = [{"code": k, "title": v} for k, v in sorted(families.items())]
    return institutions, offerings, cip


# ---------------------------------------------------------------------------
# SQL: DuckDB reads the CSVs directly, as an analyst would
# ---------------------------------------------------------------------------

def sql_db():
    import duckdb
    con = duckdb.connect()
    text_cols = {"institutions": ["UNITID", "opeid", "zip"], "outcomes": ["UNITID"],
                 "programs": ["UNITID", "cipcode", "cip_2digit"]}  # keep codes as text
    for t, cols in text_cols.items():
        types = "{" + ", ".join(f"'{c}': 'VARCHAR'" for c in cols) + "}"
        con.execute(f"CREATE TABLE {t} AS SELECT * FROM read_csv(?, header=true, types={types})",
                    [str(DATA / f"{t}-v1.0.csv")])
    return con


# ---------------------------------------------------------------------------
# SPARQL: an RDF graph
# ---------------------------------------------------------------------------

def rdf_graph(institutions=None, offerings=None, cip=None):
    from rdflib import Graph, Literal, Namespace, URIRef
    from rdflib.namespace import RDF, RDFS, XSD
    if institutions is None:
        institutions, offerings, cip = load()
    s, k = Namespace(SCHEMA), Namespace(KGN)
    g = Graph()
    g.bind("schema", s)
    g.bind("kgn", k)
    g.bind("ipeds", Namespace(ID))
    for f in cip:
        fam = URIRef(f"{ID}cip/{f['code']}")
        g.add((fam, RDF.type, k.CipFamily))
        g.add((fam, k.cipCode, Literal(f["code"])))
        g.add((fam, RDFS.label, Literal(f["title"])))
    for i in institutions:
        inst = URIRef(ID + i["unitid"])
        g.add((inst, RDF.type, s.CollegeOrUniversity))
        g.add((inst, s.name, Literal(i["name"])))
        g.add((inst, k.unitid, Literal(i["unitid"])))
        for field, prop in [("grad_rate_150_all", k.gradRate150All),
                            ("grad_rate_150_bach", k.gradRate150Bach)]:
            if i[field] is not None:  # no triple at all when IPEDS has no value
                g.add((inst, prop, Literal(str(i[field]), datatype=XSD.decimal)))
    for o in offerings:
        node = URIRef(f"{ID}{o['unitid']}/offering/{o['cipcode']}-{o['awlevel_code']}")
        g.add((node, RDF.type, s.EducationalOccupationalProgram))
        g.add((node, s.provider, URIRef(ID + o["unitid"])))
        g.add((node, s.educationalCredentialAwarded, Literal(o["award_level"])))
        g.add((node, k.awardLevelCode, Literal(o["awlevel_code"])))
        g.add((node, k.cipCode, Literal(o["cipcode"])))
        g.add((node, k.cipFamily, URIRef(f"{ID}cip/{o['cip2']}")))
        g.add((node, k.fullyDistancePrograms, Literal(o["fully_distance"])))
        g.add((node, k.someDistancePrograms, Literal(o["some_distance"])))
    return g


# ---------------------------------------------------------------------------
# Cypher: a labeled property graph in Kuzu
#   (:Institution)-[:OFFERS]->(:Offering)-[:IN_FAMILY]->(:CipFamily)
# ---------------------------------------------------------------------------

def cypher_db(institutions=None, offerings=None, cip=None):
    import kuzu
    if institutions is None:
        institutions, offerings, cip = load()
    path = WORK / "kuzu"
    if path.exists():
        shutil.rmtree(path) if path.is_dir() else path.unlink()
    WORK.mkdir(exist_ok=True)
    stage = WORK / "csv"
    stage.mkdir(exist_ok=True)

    def dump(name, rows, cols):
        with open(stage / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            for r in rows:
                w.writerow(["" if r[c] is None else r[c] for c in cols])
        return (stage / f"{name}.csv").as_posix()

    con = kuzu.Connection(kuzu.Database(str(path)))
    con.execute("CREATE NODE TABLE Institution(unitid STRING, name STRING, "
                "gradRate150All DOUBLE, gradRate150Bach DOUBLE, PRIMARY KEY(unitid))")
    con.execute("CREATE NODE TABLE Offering(id STRING, cipcode STRING, awardLevel STRING, "
                "awardLevelCode INT64, fullyDistance INT64, someDistance INT64, PRIMARY KEY(id))")
    con.execute("CREATE NODE TABLE CipFamily(code STRING, title STRING, PRIMARY KEY(code))")
    con.execute("CREATE REL TABLE OFFERS(FROM Institution TO Offering)")
    con.execute("CREATE REL TABLE IN_FAMILY(FROM Offering TO CipFamily)")
    con.execute(f"COPY Institution FROM '{dump('institution', institutions, ['unitid', 'name', 'grad_rate_150_all', 'grad_rate_150_bach'])}' (HEADER=false)")
    con.execute(f"COPY Offering FROM '{dump('offering', offerings, ['id', 'cipcode', 'award_level', 'awlevel_code', 'fully_distance', 'some_distance'])}' (HEADER=false)")
    con.execute(f"COPY CipFamily FROM '{dump('cip', cip, ['code', 'title'])}' (HEADER=false)")
    con.execute(f"COPY OFFERS FROM '{dump('offers', offerings, ['unitid', 'id'])}' (HEADER=false)")
    con.execute(f"COPY IN_FAMILY FROM '{dump('in_family', offerings, ['id', 'cip2'])}' (HEADER=false)")
    return con


if __name__ == "__main__":
    inst, off, cip = load()
    print(f"{len(inst)} institutions, {len(off)} offerings, {len(cip)} CIP families")
    g = rdf_graph(inst, off, cip)
    print(f"RDF graph: {len(g)} triples")
    con = cypher_db(inst, off, cip)
    n = con.execute("MATCH (n) RETURN count(n)").get_next()[0]
    e = con.execute("MATCH ()-[r]->() RETURN count(r)").get_next()[0]
    print(f"Property graph: {n} nodes, {e} relationships")
