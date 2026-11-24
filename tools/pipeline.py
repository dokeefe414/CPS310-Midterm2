"""Executable ontology gates and reproducible naive/controlled comparison.

Run from repository root:
  py tools/pipeline.py
  py tools/pipeline.py --output-dir evidence/local-run
  py tools/pipeline.py --group-repo ..\\CPS310-Zombie-Game

Only Python's standard library and rdflib are required. The code parses RDF
ontology and SHACL declarations; Python evaluates the documented subset of
constraints as executable gates. It is NOT a complete SHACL implementation.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

from rdflib import Graph, Namespace, RDF, RDFS, OWL

BASE = Path(__file__).resolve().parents[1]
ZG = Namespace("https://example.org/cps310/zombie-ontology#")
SH = Namespace("http://www.w3.org/ns/shacl#")
EXPECTED_MODELS_BLOB = "2c4f7e0fd9af67647e9f4d48a25199d405664031"

sys.path.insert(0, str(BASE))
from demo import naive_candidate, controlled_candidate  # noqa: E402


def git_blob_sha(data: bytes) -> str:
    """Compute Git's content-object SHA-1 (NOT raw file SHA-1)."""
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def ontology_gate() -> list[str]:
    """Require declared classes, inheritance, properties, and SHACL shapes."""
    ontology = Graph().parse(BASE / "ontology/zombie_ontology.ttl", format="turtle")
    shapes = Graph().parse(BASE / "ontology/shapes.ttl", format="turtle")
    rules = json.loads((BASE / "ontology/constraints.json").read_text(encoding="utf-8"))
    failures = []
    for name in rules["required_classes"]:
        if (ZG[name], RDF.type, OWL.Class) not in ontology:
            failures.append(f"Missing owl:Class {name}")
    for child, parent in rules["required_subclasses"].items():
        if (ZG[child], RDFS.subClassOf, ZG[parent]) not in ontology:
            failures.append(f"Missing subclass {child} -> {parent}")
    for rel, (domain, range_) in rules["required_relations"].items():
        if (ZG[rel], RDF.type, OWL.ObjectProperty) not in ontology:
            failures.append(f"Missing object property {rel}")
        if (ZG[rel], RDFS.domain, ZG[domain]) not in ontology:
            failures.append(f"Incorrect domain {rel}")
        if (ZG[rel], RDFS.range, ZG[range_]) not in ontology:
            failures.append(f"Incorrect range {rel}")
    for shape in ("BiteShape", "ConversionShape", "HumanConvertedAtMostOnceShape",
                  "PredictionShape"):
        if (ZG[shape], RDF.type, SH.NodeShape) not in shapes:
            failures.append(f"Missing SHACL shape {shape}")
    return failures


def production_gate(group_repo: Path | None) -> dict:
    """Optional external check: group model must remain unchanged.

    The individual submission intentionally does not vendor or edit Owen's
    group-project models.py. Provide --group-repo when the group working copy
    is accessible; otherwise this audit is explicitly NOT CHECKED.
    """
    if group_repo is None:
        return {"status": "not_checked", "pass": None,
                "issues": ["Supply --group-repo PATH to verify the group repo; "
                           "not required for the standalone demo."]}
    if not (group_repo / "models.py").is_file() or not (group_repo / "Zombie_Game.py").is_file():
        return {"status": "failed", "pass": False,
                "issues": ["Group repository must contain models.py and Zombie_Game.py"]}
    model = (group_repo / "models.py").read_bytes()
    game = (group_repo / "Zombie_Game.py").read_text(encoding="utf-8")
    failures = []
    sha = git_blob_sha(model)
    if sha != EXPECTED_MODELS_BLOB:
        failures.append(f"models.py changed: expected {EXPECTED_MODELS_BLOB}, got {sha}")
    for marker in ('self.strategy_mode = "thompson"',
                   "arena.swarm_learner.select_action(ctx)"):
        if marker not in game:
            failures.append(f"Required default game-theory integration missing: {marker}")
    return {"status": "passed" if not failures else "failed",
            "pass": not failures, "issues": failures}

def run_case(candidate):
    """Apply one identical adversarial scenario to each generated draft.

    Initial state: H1 (1 HP), H2 (2 HP), Z0. During one tick, Z0 bites H1
    twice, while an invalid actor H2 tries to bite H2. Correct processing
    converts H1 exactly once and ignores the invalid event.
    """
    sim = candidate.MiniGame()
    initial_humans = set(sim.humans)
    initial_zombies = set(sim.zombies)
    sim.enqueue_bite("Z0", "H1")
    sim.enqueue_bite("Z0", "H1")
    sim.enqueue_bite("H2", "H2")  # Not a Zombie: should be rejected
    sim.step()
    before_forecast = copy.deepcopy(vars(sim))
    value = sim.forecast(3)
    unchanged = before_forecast == vars(sim)

    conversions = [e for e in sim.events if e.get("type") == "ConversionEvent"]
    bites = [e for e in sim.events if e.get("type") == "BiteEvent"]
    source_ids = [e["source"] for e in conversions]

    checks = {
        "G1_unique_conversion": len(source_ids) == len(set(source_ids)) == 1,
        "G2_valid_event_roles": all(
            e["actor"] in initial_zombies and e["target"] in initial_humans
            for e in bites
        ),
        "G3_bounded_population": (
            len(sim.humans) >= 0 and len(sim.zombies) >= 0
            and len(sim.humans) + len(sim.zombies) <= sim.initial_total
            and all(hp > 0 for hp in sim.humans.values())
        ),
        "G4_pure_bounded_forecast": (
            unchanged and isinstance(value, (int, float))
            and 0 <= value <= sim.initial_total
        ),
        "G5_expected_scenario": (
            set(sim.humans) == {"H2"} and len(sim.zombies) == 2
            and len(conversions) == 1 and sim.humans["H2"] == 2
        ),
    }
    return {
        "checks": checks,
        "passes": sum(checks.values()),
        "total_checks": len(checks),
        "final": {
            "humans": len(sim.humans),
            "zombies": len(sim.zombies),
            "history": sim.history,
            "forecast_h3": value,
            "events": sim.events,
            "remaining_human_health": sim.humans,
        },
    }


def event_graph(events):
    """Construct an RDF evidence graph using ontology-defined event roles."""
    graph = Graph()
    graph.bind("zg", ZG)
    inst = Namespace("https://example.org/cps310/demo/")
    graph.bind("demo", inst)
    for i, event in enumerate(events):
        subject = inst[f"event_{i}"]
        typ = event.get("type")
        if typ == "BiteEvent":
            graph.add((subject, RDF.type, ZG.BiteEvent))
            a, t = inst[event["actor"]], inst[event["target"]]
            graph.add((a, RDF.type, ZG.Zombie if event["actor"].startswith("Z") else ZG.Human))
            graph.add((t, RDF.type, ZG.Human))
            graph.add((subject, ZG.actor, a))
            graph.add((subject, ZG.target, t))
        elif typ == "ConversionEvent":
            graph.add((subject, RDF.type, ZG.ConversionEvent))
            h, z = inst[event["source"]], inst[event["created"]]
            graph.add((h, RDF.type, ZG.Human))
            graph.add((z, RDF.type, ZG.Zombie))
            graph.add((subject, ZG.sourceHuman, h))
            graph.add((subject, ZG.createdZombie, z))
    return graph


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(BASE / "evidence" / "replayed"))
    parser.add_argument("--group-repo", default=None,
                        help="Optional path to sibling CPS310-Zombie-Game clone for G6 audit")
    args = parser.parse_args(argv)
    destination = Path(args.output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    ontology_issues = ontology_gate()
    group_repo = Path(args.group_repo).resolve() if args.group_repo else None
    production_audit = production_gate(group_repo)
    naive = run_case(naive_candidate)
    controlled = run_case(controlled_candidate)
    report = {
        "submission": "Daniel O'Keefe - CPS 310 Midterm #2",
        "scenario": "two duplicate Z0->H1 bites plus invalid H2->H2 bite in one tick",
        "ontology_gate": {"pass": not ontology_issues, "issues": ontology_issues},
        "production_gate": production_audit,
        "naive": naive,
        "controlled": controlled,
        "interpretation": "One illustrative paired demo, not statistically generalizable.",
    }
    (destination / "comparison.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    event_graph(naive["final"]["events"]).serialize(
        destination=str(destination / "naive_trace.ttl"), format="turtle"
    )
    event_graph(controlled["final"]["events"]).serialize(
        destination=str(destination / "controlled_trace.ttl"), format="turtle"
    )
    print(json.dumps({
        "ontology_ok": not ontology_issues,
        "production_audit": production_audit["status"],
        "naive": f'{naive["passes"]}/{naive["total_checks"]}',
        "controlled": f'{controlled["passes"]}/{controlled["total_checks"]}',
        "out": str(destination),
    }, indent=2))
    return 0 if not ontology_issues and production_audit["status"] != "failed" and all(
        controlled["checks"].values()
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
