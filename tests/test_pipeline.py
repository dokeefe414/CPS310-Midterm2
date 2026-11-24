"""Reproducible tests for the Midterm #2 ontology-controlled demo."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from rdflib import Graph, RDF
from tools import pipeline
from demo import controlled_candidate, naive_candidate


class OntologyPipelineTests(unittest.TestCase):
    def test_ontology_and_shapes_parse_and_have_required_terms(self):
        self.assertEqual(pipeline.ontology_gate(), [])
        shape_graph = Graph().parse(
            pipeline.BASE / "ontology/shapes.ttl", format="turtle"
        )
        self.assertIn(
            (pipeline.ZG.PredictionShape, RDF.type, pipeline.SH.NodeShape),
            shape_graph,
        )

    def test_controlled_candidate_passes_all_five_executable_gates(self):
        result = pipeline.run_case(controlled_candidate)
        self.assertEqual(result["passes"], 5)
        self.assertEqual(result["total_checks"], 5)
        self.assertTrue(all(result["checks"].values()))
        self.assertEqual(result["final"]["zombies"], 2)
        self.assertEqual(result["final"]["remaining_human_health"], {"H2": 2})

    def test_unconstrained_draft_exposes_ontology_violations(self):
        result = pipeline.run_case(naive_candidate)
        self.assertEqual(result["total_checks"], 5)
        self.assertFalse(result["checks"]["G1_unique_conversion"])
        self.assertFalse(result["checks"]["G2_valid_event_roles"])
        self.assertFalse(result["checks"]["G3_bounded_population"])
        self.assertFalse(result["checks"]["G4_pure_bounded_forecast"])
        self.assertFalse(result["checks"]["G5_expected_scenario"])

    def test_pipeline_writes_report_and_machine_readable_rdf_traces(self):
        with TemporaryDirectory() as tmp:
            code = pipeline.main(["--output-dir", tmp])
            self.assertEqual(code, 0)
            report = json.loads(
                (Path(tmp) / "comparison.json").read_text(encoding="utf-8")
            )
            self.assertTrue(report["ontology_gate"]["pass"])
            self.assertEqual(report["controlled"]["passes"], 5)
            self.assertEqual(report["naive"]["passes"], 0)
            self.assertEqual(report["production_gate"]["status"], "not_checked")
            naive_graph = Graph().parse(Path(tmp) / "naive_trace.ttl", format="turtle")
            fixed_graph = Graph().parse(
                Path(tmp) / "controlled_trace.ttl", format="turtle"
            )
            self.assertGreater(len(naive_graph), len(fixed_graph))

    def test_optional_external_audit_cannot_silently_claim_success(self):
        status = pipeline.production_gate(None)
        self.assertEqual(status["status"], "not_checked")
        self.assertIsNone(status["pass"])
        with TemporaryDirectory() as tmp:
            status = pipeline.production_gate(Path(tmp))
            self.assertEqual(status["status"], "failed")


if __name__ == "__main__":
    unittest.main()
