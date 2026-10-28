"""Run the GQL query with GraphLite and compare it with the other languages.

GraphLite (https://github.com/GraphLite-AI/GraphLite) is an open-source,
embedded ISO GQL database. Install its CLI with Rust's cargo:

    cargo install graphlite-cli      # puts `graphlite` on your PATH

Then, after `python run.py`:

    python run_gql.py                # health-professions subgraph (fast)
    python run_gql.py --full         # the complete graph (slow: see below)

Notes on GraphLite 0.0.1, the version this was written against:

- Statements longer than a few thousand characters fail in its lexer, so
  nodes are inserted in small batches.
- Edges can only be created between nodes found with MATCH, and MATCH has no
  index, so each edge statement scans the graph. Loading all 16,068 edges
  took about seven minutes when this was written. By default this script
  loads every institution and CIP family but only the health-professions
  (CIP 51) offerings, which is everything the question can touch; --full
  loads all 8,034 offerings.
- FILTER, LET and predicates inside node patterns (all valid GQL) don't parse
  yet, so question.gql uses MATCH ... WHERE ... RETURN ... GROUP BY.

The database is created in .work/graphlite with a local-only admin login.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from build import OUT, WORK, load
from run import TRAPS, VARIANTS, normalize

HERE = Path(__file__).resolve().parent
DB = WORK / "graphlite"
USER, PASSWORD = "admin", "kgn-local"  # local embedded database only
LIMIT = 2500        # max characters per statement (GraphLite lexer limit)
EDGE_BATCH = 15     # offerings per MATCH ... INSERT statement
GRAPH = "/kgn/ipeds"


def graphlite_bin():
    exe = os.environ.get("GRAPHLITE") or shutil.which("graphlite")
    if not exe:
        sys.exit("graphlite not found. Install it with `cargo install graphlite-cli` "
                 "or set GRAPHLITE=/path/to/graphlite.")
    return exe


def lit(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    return '"' + str(v).replace("\\", "\\\\").replace('"', '\\"') + '"'


def node(label, props):
    body = ", ".join(f"{k}: {lit(v)}" for k, v in props.items() if v is not None)
    return f"(:{label} {{{body}}})"


def load_script(full):
    institutions, offerings, cip = load()
    if not full:
        offerings = [o for o in offerings if o["cip2"] == "51"]
    nodes = [node("CipFamily", {"code": f["code"], "title": f["title"]}) for f in cip]
    nodes += [node("Institution", {"unitid": i["unitid"], "name": i["name"],
                                   "gradRate150All": i["grad_rate_150_all"],
                                   "gradRate150Bach": i["grad_rate_150_bach"]}) for i in institutions]
    nodes += [node("Offering", {"id": o["id"], "cipcode": o["cipcode"],
                                "awardLevelCode": o["awlevel_code"],
                                "fullyDistance": o["fully_distance"],
                                "someDistance": o["some_distance"]}) for o in offerings]
    stmts, cur = [], []
    for n in nodes:
        if cur and len("INSERT " + ", ".join(cur + [n])) > LIMIT:
            stmts.append("INSERT " + ", ".join(cur) + ";")
            cur = []
        cur.append(n)
    if cur:
        stmts.append("INSERT " + ", ".join(cur) + ";")

    groups = defaultdict(list)
    for o in offerings:
        groups[(o["unitid"], o["cip2"])].append(o)
    for (u, c), group in groups.items():
        for k in range(0, len(group), EDGE_BATCH):
            chunk = group[k:k + EDGE_BATCH]
            m = [f'(i:Institution {{unitid: "{u}"}})', f'(f:CipFamily {{code: "{c}"}})']
            m += [f'(o{n}:Offering {{id: "{o["id"]}"}})' for n, o in enumerate(chunk)]
            ins = [f"(i)-[:OFFERS]->(o{n}), (o{n})-[:IN_FAMILY]->(f)" for n in range(len(chunk))]
            stmts.append("MATCH " + ", ".join(m) + " INSERT " + ", ".join(ins) + ";")
    return stmts, len(nodes), 2 * len(offerings)


def console(exe, statements, timeout=None):
    """Pipe statements into the GraphLite console and return its output."""
    script = "\n".join([f"SESSION SET GRAPH {GRAPH};", *statements, "exit"]) + "\n"
    r = subprocess.run([exe, "gql", "--path", str(DB), "-u", USER, "-p", PASSWORD, "-l", "off"],
                       input=script, capture_output=True, text=True, timeout=timeout)
    return r.stdout + r.stderr


def parse_tables(text):
    """Extract result tables (lists of row lists) from console output."""
    tables, rows, inside = [], [], False
    for line in text.splitlines():
        if line.startswith("╞"):
            inside, rows = True, []
        elif line.startswith("└") and inside:
            tables.append(rows)
            inside = False
        elif inside and line.startswith("│"):
            rows.append([c.strip() for c in line.strip("│").split("┆")])
    return tables


def gql_for(variant, table=None):
    text = (HERE / "queries" / "question.gql").read_text()
    for old, new in (table or VARIANTS)[variant]["edits"].get("Cypher", []):  # same property names
        assert old in text, f"GQL/{variant}: '{old}' not found"
        text = text.replace(old, new)
    # GraphLite reads the console one statement at a time: drop comments, keep one statement
    return " ".join(l.split("//")[0].strip() for l in text.splitlines() if l.split("//")[0].strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="load all 8,034 offerings (slow)")
    args = ap.parse_args()
    exe = graphlite_bin()
    results_path = OUT / "results.json"
    if not results_path.exists():
        sys.exit("Run `python run.py` first.")
    results = json.loads(results_path.read_text())

    if DB.exists():
        shutil.rmtree(DB)
    WORK.mkdir(exist_ok=True)
    subprocess.run([exe, "install", "--path", str(DB), "--admin-user", USER,
                    "--admin-password", PASSWORD, "-l", "off"], check=True, capture_output=True)
    subprocess.run([exe, "query", "--path", str(DB), "-u", USER, "-p", PASSWORD, "-l", "off",
                    "CREATE SCHEMA /kgn"], check=True, capture_output=True)
    subprocess.run([exe, "query", "--path", str(DB), "-u", USER, "-p", PASSWORD, "-l", "off",
                    f"CREATE GRAPH {GRAPH}"], check=True, capture_output=True)

    stmts, n_nodes, n_edges = load_script(args.full)
    print(f"Loading {n_nodes} nodes and {n_edges} edges into GraphLite "
          f"({'full graph' if args.full else 'health-professions subgraph'})...", flush=True)
    out = console(exe, stmts)
    errors = [l for l in out.splitlines() if l.startswith("Error")]
    if errors:
        sys.exit(f"Load failed: {errors[0]}")
    counts = parse_tables(console(exe, ["MATCH (n) RETURN count(n) AS nodes;",
                                        "MATCH ()-[r]->() RETURN count(r) AS rels;"]))
    loaded = (int(counts[0][0][0]), int(counts[1][0][0]))
    assert loaded == (n_nodes, n_edges), f"loaded {loaded}, expected {(n_nodes, n_edges)}"

    report = ["# GQL results (GraphLite)", "",
              f"Graph: {n_nodes} nodes, {n_edges} edges "
              f"({'complete graph' if args.full else 'all institutions and CIP families, health-professions offerings only'}).", ""]
    gql_answers, all_match = {}, True
    for v in VARIANTS:
        q = gql_for(v)
        text = console(exe, [q])
        if "Error" in text:
            sys.exit(f"{v}: {next(l for l in text.splitlines() if 'Error' in l)}")
        tables = parse_tables(text)
        rows = tables[0] if tables else []
        ans = normalize([(r[0], r[1], r[2], r[3]) for r in rows])
        expected = [tuple(x) for x in results["variants"][v]["answers"]["SQL"]]
        match = ans == expected
        all_match &= match
        gql_answers[v] = ans
        report.append(f"- **{v}:** GQL returned {len(ans)} schools, "
                      f"{'identical to' if match else 'DIFFERENT from'} SQL, SPARQL and Cypher.")
    report.append("")

    traps = {}
    for t, spec in TRAPS.items():
        if "GQL" in spec.get("na", {}):
            traps[t] = {"na": spec["na"]["GQL"]}
            continue
        text = console(exe, [gql_for(t, TRAPS)])
        err = next((l for l in text.splitlines() if l.startswith("Error")), None)
        if err:
            traps[t] = {"error": err[:160]}
        else:
            tables = parse_tables(text)
            traps[t] = {"rows": normalize([(r[0], r[1], r[2], r[3]) for r in (tables[0] if tables else [])])}
        shown = len(traps[t]["rows"]) if "rows" in traps[t] else ("error" if "error" in traps[t] else "n/a")
        report.append(f"- **{spec['label'].rstrip('?.')}:** GQL returned {shown}.")
    report.append("")
    version = subprocess.run([exe, "--version"], capture_output=True, text=True).stdout.strip()
    (OUT / "gql-results.json").write_text(json.dumps(
        {"engine": version, "full_graph": args.full, "nodes": n_nodes, "edges": n_edges,
         "answers": gql_answers, "all_match": all_match, "traps": traps}, indent=2), encoding="utf-8")
    (OUT / "gql-results.md").write_text("\n".join(report), encoding="utf-8")
    print("\n".join(report))
    return all_match


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
