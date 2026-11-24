# Final Submission Audit — CPS 310 Fall 2026 Midterm #2

**Student (printed): Daniel O'Keefe**  
**Deadline:** Tuesday, November 24, 2026, 11:59 p.m. EST  
**Submission repository:** [dokeefe414/CPS310-Midterm2](https://github.com/dokeefe414/CPS310-Midterm2)  
**Project type:** Individual submission, separate from group game.

## 1. Rubric-by-rubric evidence

| Exact assignment requirement | Evidence / files | What a reviewer should verify |
| --- | --- | --- |
| **Design a process control pipeline for AI-driven Zombie Game development using ontology** | [Pipeline design](PIPELINE_DESIGN.md), [ontology](../ontology/), [controller](../tools/pipeline.py) | Nine stages S0–S8, ontology classes, role types and executable gates |
| **Explicitly state every pipeline step** | [S0–S8 walkthrough](PIPELINE_DESIGN.md) | Each stage has input, action, control, output, failure response |
| **Explicitly explain pipeline design** | [Why the controls work](PIPELINE_DESIGN.md) and [ontology guide](ONTOLOGY_GUIDE.md) | Domain vocabulary separated from Python execution and SHACL |
| **Rigorously argue controls and improvements compared to naive AI coding** | [Naive comparison](DEMONSTRATION_AND_COMPARISON.md) and [pipeline design](PIPELINE_DESIGN.md) | Same initial state/event sequence; defects detected in semantic roles, conversion count, population bounds, prediction purity and end state |
| **Provide all major prompts** | [Major prompt specifications](../prompts/MAJOR_PROMPTS.md), [repair prompts R0–R3](../prompts/REPAIR_CYCLE.md) | Complete replayable input wording and truthful provenance limitations |
| **Demos with concrete outcomes** | [Three candidate implementations](../demo/), [test runner](../tools/pipeline.py), [CI run](https://github.com/dokeefe414/CPS310-Midterm2/actions/runs/45450883812) | Three-stage 0/5 → 4/5 → 5/5; real SHACL violation counts 4 → 1 → 0; eight passing unit tests |
| **Upload demos, intermediate results and especially ontologies to GitHub** | [Turtle ontology](../ontology/zombie_ontology.ttl), [SHACL shapes](../ontology/shapes.ttl), [constraints manifest](../ontology/constraints.json), [CI comparison JSON](../evidence/verified_run_45450883812/comparison.json), [Actions artifact](https://github.com/dokeefe414/CPS310-Midterm2/actions/runs/45450883812) | All source and static artifacts tracked in Git; generated RDF/SHACL reports downloadable under CI run |
| **Individual work** | This independent repository and scoped demo files | No modifications to the shared group's Game Theory or Adaptive Kalman sources |
| **Printed name in submission** | Top of [README](../README.md), ontology manifest, reports, and this audit | Daniel O'Keefe printed and visible |
| **Explain files too large to upload** | No large files omitted | Only small text and generated traces; workflow artifacts may expire, but they are reproducible |
| **Defend submission** | [Defense guide](DEFENSE_GUIDE.md) | Student can run tests, explain each stage and each invariant |

## 2. Executed evidence, not just predictions

- GitHub Actions run [45450883812](https://github.com/dokeefe414/CPS310-Midterm2/actions/runs/45450883812): **success**, eight unit tests passed.
- Saved actual report: [comparison.json](../evidence/verified_run_45450883812/comparison.json).
- Python G1–G5: **naive 0/5**, **repair v1 4/5**, **controlled 5/5**.
- Executed SHACL validator: **4, 1, 0 violations**, respectively.
- Workflow artifact: `ontology-demo-evidence`, containing per-stage Turtle graphs, SHACL reports (Turtle and readable text) and the JSON report.
- External group game audit G6: **not_checked** unless the optional `--group-repo` path is supplied. G6 is not counted in the 5/5 score.
- This is an illustrative candidate/repair sequence, **not** an unbiased multi-trial evaluation of randomly sampled AI responses.

## 3. Reproducible defense commands

Run inside this repository in VS Code PowerShell:

```powershell
py -m pip install -r requirements.txt
py -m unittest discover -s tests -v
py tools/pipeline.py
```

Show the professor these output files in `evidence/replayed/`:

```text
comparison.json
naive_trace.ttl
repair_v1_trace.ttl
controlled_trace.ttl
naive_shacl_report.ttl
repair_v1_shacl_report.ttl
controlled_shacl_report.ttl
naive_shacl_report.txt
repair_v1_shacl_report.txt
controlled_shacl_report.txt
```

These are actual computed traces and constraint reports.

## 4. Honest limitations and likely questions

1. **Does an AI model generate code every time I run `pipeline.py`?**
   No. ChatGPT assisted in producing the committed candidate snapshots and
   repair documentation. The runtime control pipeline uses RDF/SHACL and
   Python tests to validate those snapshots without external model access.
   The reproducible prompts enable further user-driven AI generation.
2. **Is the ontology a full formal proof of the entire game?**
   No. It controls a selected non-trivial slice and one adversarial scenario.
   The `pyshacl` step validates the generated one-tick RDF graphs, and
   Python gates check runtime-only properties not represented by RDF.
3. **Does the example contain the group's forecasting code?**
   No. Its pure, capped trend forecast is simpler than the group's Adaptive
   Kalman Filter. This keeps the midterm focused on process control.
4. **Did the process alter Owen's Game Theory or shared source?**
   No. All work is in `CPS310-Midterm2`. An optional integrity check can
   read the group's clone but never modifies it.
5. **Are the "all major prompts" real historical API logs?**
   They are complete replayable prompt specifications with transparent
   provenance. Do not claim they are immutable historical transcripts or
   independently sampled generations.

## 5. Final readiness

The implemented code, documentation, prompts, SHACL constraints, automated
tests, source-level repair examples and verified evidence have been committed
to this **individual GitHub repository**. One actual step remains outside
the code: **submit the GitHub repository link using the course's required
submission process before the deadline.**

No need for paid AI model access to replay the demonstration.
