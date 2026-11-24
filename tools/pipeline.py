"""Executable ontology gates and reproducible naive/controlled comparison.

Run from repository root:
  py tools/pipeline.py
  py tools/pipeline.py --output-dir evidence/local-run
  py tools/pipeline.py --group-repo ..\\CPS310-Zombie-Game

Uses rdflib and pyshacl to validate RDF event traces against SHACL shapes,
plus separate executable Python acceptance gates for non-RDF properties such
as forecast purity. Does not invoke any AI API at runtime.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

from rdflib import Graph, Namespace, RDF, RDFS, OWL, XSD, Literal
from pyshacl import validate as shacl_validate

BASE = Path(__file__).resolve().parents[1]
ZG = Namespace("https://example.org/cps310/zombie-ontology#")
SH = Namespace("http://www.w3.org/ns/shacl#")
EXPECTED_MODELS_BLOB = "2c4f7e0fd9af67647e9f4d48a25199d405664031"

sys.path.insert(0, str(BASE))
from demo import naive_candidate, controlled_candidate, repair_candidate_v1  # noqa: E402


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
                  "PredictionShape", "PopulationSnapshotShape"):
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


def event_graph(events, final=None):
    """Construct an RDF graph of the trace and observed final snapshot.

    The concrete data graph includes explicit types; SHACL checks these facts
    without applying RDFS/OWL inference that could mask bad actor roles.
    """
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
    if final is not None:
        snapshot = inst["snapshot_tick_1"]
        graph.add((snapshot, RDF.type, ZG.PopulationSnapshot))
        graph.add((snapshot, ZG.zombieCount, Literal(final["zombies"], datatype=XSD.integer)))
        graph.add((snapshot, ZG.survivingAgents, Literal(
            final["humans"] + final["zombies"], datatype=XSD.integer)))
        # The demo has a fixed initial population of H1, H2, and Z0.
        graph.add((snapshot, ZG.initialPopulation, Literal(3, datatype=XSD.integer)))
        observer = inst["forecast_observer"]
        prediction = inst["forecast_tick_1_h3"]
        graph.add((observer, RDF.type, ZG.ForecastObserver))
        graph.add((prediction, RDF.type, ZG.Prediction))
        graph.add((prediction, ZG.computedBy, observer))
        graph.add((prediction, ZG.predictedCount, Literal(
            int(final["forecast_h3"]), datatype=XSD.integer)))
        graph.add((prediction, ZG.populationCapacity, Literal(3, datatype=XSD.integer)))
    return graph


def validate_event_graph(graph):
    """Run a real SHACL validator and expose checkable violation counts."""
    shapes = Graph().parse(BASE / "ontology/shapes.ttl", format="turtle")
    conforms, validation_graph, message = shacl_validate(
        data_graph=graph, shacl_graph=shapes, inference="none",
        abort_on_first=False, allow_infos=False, allow_warnings=False,
    )
    violations = sum(
        1 for _ in validation_graph.subjects(RDF.type, SH.ValidationResult)
    )
    return {"conforms": bool(conforms), "violations": violations}, validation_graph, str(message)


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
    cases = {
        "naive": run_case(naive_candidate),
        "repair_v1": run_case(repair_candidate_v1),
        "controlled": run_case(controlled_candidate),
    }
    shacl_checks = {}
    for name, result in cases.items():
        graph = event_graph(result["final"]["events"], final=result["final"])
        graph.serialize(destination=str(destination / f"{name}_trace.ttl"),
                        format="turtle")
        verdict, report_graph, message = validate_event_graph(graph)
        shacl_checks[name] = verdict
        report_graph.serialize(destination=str(destination / f"{name}_shacl_report.ttl"),
                               format="turtle")
        (destination / f"{name}_shacl_report.txt").write_text(
            message, encoding="utf-8"
        )
    report = {
        "submission": "Daniel O'Keefe - CPS 310 Midterm #2",
        "scenario": "two duplicate Z0->H1 bites plus invalid H2->H2 bite in one tick",
        "ontology_gate": {"pass": not ontology_issues, "issues": ontology_issues},
        "production_gate": production_audit,
        **cases,
        "shacl_validation": shacl_checks,
        "interpretation": (
            "One reproducible AI-assisted failure/repair illustration; "
            "not an independent-sampling study of LLM outputs."
        ),
    }
    (destination / "comparison.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "ontology_ok": not ontology_issues,
        "production_audit": production_audit["status"],
        "naive": f'{cases["naive"]["passes"]}/{cases["naive"]["total_checks"]}',
        "repair_v1": f'{cases["repair_v1"]["passes"]}/{cases["repair_v1"]["total_checks"]}',
        "controlled": f'{cases["controlled"]["passes"]}/{cases["controlled"]["total_checks"]}',
        "shacl": shacl_checks,
        "out": str(destination),
    }, indent=2))
    expected = (cases["naive"]["passes"] == 0
                and cases["repair_v1"]["passes"] == 4
                and cases["controlled"]["passes"] == 5
                and not shacl_checks["naive"]["conforms"]
                and not shacl_checks["repair_v1"]["conforms"]
                and shacl_checks["controlled"]["conforms"])
    return 0 if not ontology_issues and production_audit["status"] != "failed" and expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
