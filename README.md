# CPS 310 Midterm #2 — Ontology-Controlled AI Development Pipeline

Daniel O'Keefe

Tuesday, November 24, 2026  

## 1. Purpose and scope

The question is not just **"Can AI write a zombie simulation?"** It is:
**"How can we specify, control, inspect, test, and improve AI-generated software by
using a formal domain ontology and measurable acceptance gates?"**

I designed and implemented a **nine-stage, ontology-driven process control
pipeline** for a deliberately small but nontrivial Zombie Game slice.
The code retains humans, zombies, bite events, lethal human-to-zombie conversions,
population counts, and a simple population forecast. The demo intentionally
does not copy or change the full production framework, Owen's
`LinearThompsonSwarmLearner`, or my Adaptive Kalman Filter.

The source game remains at
[**CPS310-Zombie-Game**](https://github.com/dokeefe414/CPS310-Zombie-Game).
This is a separate **process-control research/demo submission**.

## 2. Start here: what to read

| Question | Document / artifact |
| --- | --- |
| What are all the stages of the process pipeline, and why? | [Pipeline design and controlled development process](docs/PIPELINE_DESIGN.md) |
| What is an ontology, what are the classes and relationships, and how is it enforced? | [Ontology design explained](docs/ONTOLOGY_GUIDE.md) |
| What were the major AI prompts? | [Original prompt templates](prompts/MAJOR_PROMPTS.md) and [actual staged repair/provenance](prompts/REPAIR_CYCLE.md) |
| What does the naive-versus-controlled demo test? | [Demonstration, evidence, and comparison](docs/DEMONSTRATION_AND_COMPARISON.md) |
| How can I explain and defend this work? | [Professor defense guide](docs/DEFENSE_GUIDE.md) |
| What exactly is the ontology? | [OWL/RDF Turtle](ontology/zombie_ontology.ttl), [SHACL constraints](ontology/shapes.ttl), [executable gate manifest](ontology/constraints.json) |
| Where is the implementation? | [Pipeline code](tools/pipeline.py) and [unit tests](tests/test_pipeline.py) |
| Where are the AI-assisted code candidates? | [Uncontrolled draft](demo/naive_candidate.py), [first repair](demo/repair_candidate_v1.py), and [final controlled draft](demo/controlled_candidate.py) |
| Where are the recorded runs? | [GitHub Actions workflow](.github/workflows/ontology-validation.yml) — run artifacts contain comparison JSON and RDF traces |

## 3. Nine explicit pipeline stages

```text
[S0] Scope/requirements for a nontrivial slice
  -> [S1] Identify ontology entities, relationships, invariants
  -> [S2] Formalize ontology (RDF/OWL + SHACL + JSON gate manifest)
  -> [S3] Construct controlled AI prompts from the ontology
  -> [S4] Generate candidate software (naive baseline + controlled draft)
  -> [S5] Verify ontology consistency / required vocabulary
  -> [S6] Verify executable semantic contracts (G1-G5) and tests
  -> [S7] Produce event-level RDF traces and objective comparison JSON
  -> [S8] Review failures, repair, record decisions, version and defend
```

This is a **human-in-the-loop AI development pipeline**. The AI-generated
candidate is treated as untrusted until the verification gates accept it.
The implemented controller runs with Python, `rdflib`, and `pyshacl`; it
does not silently call an AI model or incur API charges.

**Where the ontology controls the process:** the entities/relationships
determine acceptable code structure and event roles; the constraints
are converted to executable tests; any failing test blocks acceptance;
each attempt produces evidence that a reviewer can inspect.

For the complete design rationale, comparison with naive AI-assisted
coding, and all inputs/outputs per stage, read
[PIPELINE_DESIGN.md](docs/PIPELINE_DESIGN.md).

## 4. How to run the full demo (Windows PowerShell)

```powershell
git clone https://github.com/dokeefe414/CPS310-Midterm2.git
cd CPS310-Midterm2
py -m pip install -r requirements.txt
py -m unittest discover -s tests -v
py tools/pipeline.py
```

The pipeline prints the number of passed gates for all three candidate stages and
writes fresh output to `evidence/replayed/`:

```text
comparison.json            # G1-G5 for naive, repair_v1, controlled + SHACL verdicts
naive_trace.ttl            # baseline RDF evidence
repair_v1_trace.ttl        # intermediate repair RDF evidence
controlled_trace.ttl       # final controlled RDF evidence
*_shacl_report.ttl         # real SHACL machine-readable validation reports
*_shacl_report.txt         # readable SHACL violation explanations
```

To check the group code **without modifying it**, optional:

```powershell
py tools/pipeline.py --group-repo ..\CPS310-Zombie-Game
```

This optional G6 audit compares the group `models.py` Git blob SHA with
its pinned known baseline and verifies the default Thompson integration
markers in `Zombie_Game.py`. It reports **`not_checked`**, rather than
a false pass, if the group repository path was not provided.

On macOS/Linux use `python3` instead of `py`.

## 5. What is being tested?

The same adversarial input is applied to both candidates:

1. Start with `H1` (1 HP), `H2` (2 HP), and `Z0` (one zombie).
2. Queue **two** `Z0 -> H1` bites within a single tick.
3. Queue an **invalid** `H2 -> H2` bite (human as purported zombie actor).
4. Advance the tick.
5. Request a three-tick zombie-population prediction.

Five executable criteria, derived from the ontology, are applied equally:

| Gate | Acceptance criterion |
| --- | --- |
| **G1** | One human can produce no more than one conversion during the demonstration tick |
| **G2** | Every accepted bite has a zombie actor and human target |
| **G3** | Counts and live health remain valid; surviving agents never exceed initial capacity |
| **G4** | Forecasting is read-only and returns a count between zero and capacity |
| **G5** | The specific scenario leaves `H2` alive/unhurt and converts `H1` exactly once |
| **G6** | Optional **external** protection check of the original group learner; excluded from the standalone score unless supplied |

The naive reference draft demonstrates the absence of these safeguards;
the intermediate repair fixes event handling but retains an over-capacity forecast;
the controlled draft implements duplicate suppression, type validation,
population caps, and a pure forecasting function. These candidate modules
are intentionally separate from the group's real code.

### Executable ontology validation and a two-step repair demonstration

The final update adds an actual **SHACL execution step** using `pyshacl`.
The software generates RDF graphs containing BiteEvents, ConversionEvents,
PopulationSnapshots, and Predictions; these are checked against
`ontology/shapes.ttl`. A failure is recorded as a SHACL report and can
block acceptance even when Python code executes without exceptions.
Separately, the five original Python behavioral gates check role validity,
event uniqueness, population conservation, forecast purity and exact state.

The staged demonstration preserves all three AI-assisted source snapshots:
**naive → repair_v1 → controlled**. The repair v1 snapshot deliberately leaves
an over-capacity forecast, so the next step fixes a *measured remaining
violation*, not just an imagined one. The [full repair task specifications,
provenance, expected results and commands](prompts/REPAIR_CYCLE.md)
are committed for your defense. The pipeline runs **deterministic
validation**; it does not generate new LLM answers at runtime.

## 6. Expected demonstration behavior and limits

For this deliberately selected test scenario, the controlled draft is
designed to pass **5/5** executable candidate gates, whereas the naive
draft exhibits all five violations (**0/5**). The outcome has been **confirmed in [successful GitHub Actions run #10](https://github.com/dokeefe414/CPS310-Midterm2/actions/runs/45322367482)**: all five unit tests passed; the baseline scored 0/5 and the controlled draft 5/5. The actual CI comparison JSON is [archived in Git](evidence/verified_run_45322367482/comparison.json), with [event-trace evidence](evidence/README.md).

**Do not misinterpret the comparison:** the naive and controlled
reference implementations are small AI-assisted examples designed for
this submission. They are **not** independently sampled, blinded,
or a statistical comparison across many LLM generations. The demo
shows that ontology-derived controls **detect and prevent the specified
failures in this scenario**. It does not prove that AI always generates
better code, that the ontology is complete, or that the full group
framework has been formally verified.

The demonstration's forecast is a **simple capped trend**, NOT the
production Adaptive Kalman Filter. This keeps the exam task focused
on process control while still testing a genuine prediction component.

## 7. How to describe the improvement over naive development

A naive AI workflow commonly looks like this:

```text
one broad prompt -> generated code -> quick manual glance -> accept
```

It can omit implicit requirements, accept invalid event types, and
silently violate invariants. The controlled workflow instead makes
requirements explicit **before generation**, tests them **after
generation**, and gives the developer traceable evidence for repairs.

This pipeline improves **requirement traceability**, **controlled
vocabulary**, **deterministic invariant checking**, **regression
detection**, **reviewability**, and **auditability**. These are concrete
controls over *the development process*, not claims of a speedup or
general improvement in model intelligence.

## 8. Submission map and missing files

```text
CPS310-Midterm2/
  README.md
  requirements.txt
  .github/workflows/ontology-validation.yml
  docs/
    PIPELINE_DESIGN.md
    ONTOLOGY_GUIDE.md
    DEMONSTRATION_AND_COMPARISON.md
    DEFENSE_GUIDE.md
  prompts/
    MAJOR_PROMPTS.md
  ontology/
    zombie_ontology.ttl
    shapes.ttl
    constraints.json
  demo/
    __init__.py
    naive_candidate.py
    controlled_candidate.py
  tools/
    __init__.py
    pipeline.py
  tests/
    __init__.py
    test_pipeline.py
  evidence/
    README.md
    verified_run_45322367482/
      comparison.json
      naive_trace.ttl
      controlled_trace.ttl
```

**No oversized files are needed for this submission.** Generated
`evidence/replayed/` files are ignored to avoid churn, and GitHub
Actions uploads the original generated JSON and RDF traces.
The **actual verified CI comparison JSON** and event-graph reconstructions
derived from its recorded events are also permanently committed under
[`evidence/verified_run_45322367482/`](evidence/verified_run_45322367482/).
No full group game files, AI model weights, or proprietary service
logs are required. If a run artifact expires, the exact command
recreates the output.

## 9. Prompt and evidence provenance

The prompt file includes the full, **replayable prompt specifications**
for the major stages. It is **not** presented as a verbatim historical
API transcript or as proof of a blind two-model experiment. The
reference candidates and process documents were written with
AI assistance under human direction. The independently executable
gates and CI evidence are what demonstrate the code's behavior.

**Student responsible for understanding, reviewing, and defending this
submission: Daniel O'Keefe.**

## Final verified result — November 24, 2026

The final [CI validation run](https://github.com/dokeefe414/CPS310-Midterm2/actions/runs/45450883812)
completed **8/8 automated tests successfully**, installed and executed
`pyshacl`, and uploaded the RDF traces, readable SHACL reports, and
the machine-readable `comparison.json` as an Actions artifact.

| Candidate checkpoint | Python acceptance gates | SHACL conformant? | SHACL violation count |
| --- | --- | --- | --- |
| Original naive draft | **0/5** | No | **4** |
| Event-repair version 1 | **4/5** | No | **1** |
| Final controlled draft | **5/5** | **Yes** | **0** |

The real generated `comparison.json` from the CI job is permanently
archived at [`evidence/verified_run_45450883812/comparison.json`](evidence/verified_run_45450883812/comparison.json).
The [workflow artifact](https://github.com/dokeefe414/CPS310-Midterm2/actions/runs/45450883812)
contains all generated RDF traces and SHACL validation reports.

This is a reproducible demonstration of the controls on one specified
scenario. It does **not** prove universal AI-generation accuracy or
automatically invoke an AI model at pipeline runtime. All project files
and prompt specifications are in this individual repository.

Before submitting, consult [the final rubric checklist](docs/FINAL_SUBMISSION_AUDIT.md).
