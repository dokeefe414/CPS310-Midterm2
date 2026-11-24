# Midterm #2 Oral Defense Guide

**Daniel O'Keefe · CPS 310 · Individual Submission**

This is a practical walkthrough for explaining, running, and defending
the actual submitted files. Read it together with the [README](../README.md)
and the [pipeline design](PIPELINE_DESIGN.md).

## 1. Your opening statement (about 45 seconds)

> For Midterm #2, I designed an ontology-controlled pipeline for
> AI-assisted software development of a simplified Zombie Game.
> Instead of trusting whatever code AI generates, I first define
> the game's entities, relationships, and rules in an ontology.
> I then use these rules to constrain generation and to build
> executable acceptance tests. The tests check things like whether
> only zombies can cause bite events, whether a human converts
> only once, and whether a population forecast is read-only and
> stays within possible bounds. I compared an unconstrained
> reference implementation with a constrained implementation,
> then generated JSON and RDF evidence showing which checks
> each one passed or failed. Everything is in my own repository,
> separate from the group's original game.

## 2. Five-minute live demonstration

**Before the meeting**, in VS Code PowerShell:

```powershell
git switch main
git pull origin main
py -m pip install -r requirements.txt
py -m unittest discover -s tests -v
py tools/pipeline.py
```

Then show the following files in this order.

| Timing | Open | What to explain |
| --- | --- | --- |
| 0:00–0:45 | `README.md` | Goal: process control, not a brand-new full game |
| 0:45–1:30 | `ontology/zombie_ontology.ttl` | Class hierarchy and BiteEvent/ConversionEvent roles |
| 1:30–2:00 | `ontology/shapes.ttl`, `constraints.json` | Rules are formal, named, and machine-readable |
| 2:00–2:45 | `prompts/MAJOR_PROMPTS.md` | Baseline prompt vs constrained prompt, plus test prompt |
| 2:45–3:45 | Terminal: `py tools/pipeline.py` | Same adversarial case, gates and comparison outputs |
| 3:45–4:20 | `evidence/replayed/comparison.json`, RDF traces | Actual events behind each pass/fail result |
| 4:20–5:00 | `tests/test_pipeline.py`, `docs/PIPELINE_DESIGN.md` | Automated controls, failure policy, limitations |

Do not promise any unverified output. If the script fails, inspect
its error, show the evidence you do have, and explain why the failing
control appropriately prevents acceptance.

## 3. The exact pipeline to memorize

Use this sequence in order, without skipping stages:

```text
S0 Scope and requirements
S1 Extract domain concepts
S2 Write RDF/OWL, SHACL, JSON constraints
S3 Create ontology-constrained prompts
S4 Generate isolated AI candidate implementations
S5 Verify the formal ontology vocabulary
S6 Run executable semantic acceptance gates
S7 Save comparison JSON and RDF event traces
S8 Review, repair, document, version, and release
```

Remember that **S5 and S6 are different**:
S5 checks that the *specification* is structurally complete;
S6 checks whether the *generated Python candidate* behaves
according to the specified rules.

## 4. Five gates to memorize

- **G1:** The same human must not create multiple zombies in one tick.
- **G2:** A bite event requires a zombie actor and a human target.
- **G3:** Population and remaining human health must satisfy invariants.
- **G4:** A forecast cannot change simulation state or exceed capacity.
- **G5:** A known adversarial scenario must finish in its exact expected state.

**G6** is an optional **external** audit of the group repo's
`models.py` and normal Thompson decision path. When you do not
provide the group repo path, report G6 as `not_checked`,
not passed. The two candidates are evaluated on G1–G5 only.

## 5. Questions the professor may ask

**Q: What exactly is ontology?**

> An ontology is a formal vocabulary that states the types of
> things that exist in a domain and their relationships.
> In this project it defines Agent, Human, Zombie, BiteEvent,
> ConversionEvent, Prediction, and their permitted roles.
> It helps turn ambiguous requirements into explicit constraints.

**Q: Why is using an ontology different from putting comments in code?**

> Comments explain an implementation but don't normally block
> incorrect behavior. My ontology supplies a structured
> requirement source that I map to concrete pass/fail tests.
> The tests can reject AI-generated code even if it executes.

**Q: What does RDF mean? What does OWL mean?**

> RDF represents knowledge as subject-predicate-object triples.
> OWL provides vocabulary for classes, inheritance, and
> properties. Turtle is the readable file syntax I used.

**Q: What does SHACL do?**

> SHACL expresses constraints for validating RDF data,
> such as requiring exactly one zombie actor for a BiteEvent.
> In this implementation I parse the SHACL declarations and
> check their presence, but my Python gates enforce the
> demonstrated behavior. I did not write a complete SHACL
> validator.

**Q: Doesn't RDFS range already prevent an invalid bite actor?**

> No. RDF/OWL range and domain axioms often lead to type
> inferences under open-world semantics; they are not
> automatically closed-world rejection rules. I enforce the
> actor and target membership check explicitly in Python.

**Q: What makes the development pipeline controlled?**

> AI output is not automatically accepted. Its required
> vocabulary is specified, the implementation is tested
> against derived contracts, failed drafts are kept for
> diagnosis, and evidence is recorded. A failing required
> check prevents approval.

**Q: How are your naive and controlled candidates compared fairly?**

> They expose the same MiniGame interface and start from
> the same human and zombie state. They receive the same
> queued events and forecast request, and the same five
> gates evaluate both. This is a controlled demonstration
> of the constraints, not a statistically unbiased
> evaluation of multiple independent AI generations.

**Q: What was the main bug in the naive candidate?**

> Duplicate lethal bites could each queue a human
> conversion. The same human then created two zombies,
> violating the population invariant. The code also
> accepted a human as a bite actor and could forecast
> more zombies than the initial population.

**Q: How exactly did the ontology improve development?**

> It made the type rules and invariants explicit up
> front, so a checker could flag illegal interactions,
> repeated conversions, and observer mutation. That
> improves traceability and repeatability compared
> with a broad prompt followed by visual inspection.

**Q: Does your pipeline use an AI model at runtime?**

> No. I used AI assistance to create candidate code
> and designed prompts for repeatable generation.
> The runtime process-control stage uses deterministic
> Python validation, so anyone can run it without
> a paid AI service.

**Q: Where are your prompts?**

> The complete replayable prompts are in
> `prompts/MAJOR_PROMPTS.md`, covering scoping,
> ontology design, baseline generation, constrained
> generation, tests, review, and evidence. They are
> reproducible specifications, not fabricated historical
> model transcript logs.

**Q: Does this modify Owen's Game Theory?**

> No. This is an entirely separate repository.
> The demo doesn't import the group game's `models.py`.
> The optional audit can read the group clone and
> verify its expected model hash and dispatch markers,
> but it never writes the group repository.

**Q: Does your mini forecast contain the Adaptive Kalman Filter?**

> No. Here the forecast is a simple capped trend
> prediction because the exam focuses on ontology
> process control. The full Adaptive Kalman forecasting
> specialization remains in the group project.

**Q: What is a limitation?**

> The demonstration covers one small scenario and five
> semantic checks; it does not formally verify the
> entire game. The SHACL rules are validated on our one-tick RDF traces
> using `pyshacl`, but that doesn't verify the whole game.
> The prepackaged candidates aren't a statistical experiment
> across independent AI model outputs.

## 6. How to explain the "rigorous argument" requirement

Your argument should have four parts:

1. **Uncontrolled failure mode:** a broad AI prompt doesn't
   explicitly disallow double conversion or invalid actor types.
2. **Control mechanism:** encode roles and invariants in
   ontology files and executable gates.
3. **Concrete evidence:** feed the same adversarial input
   to both candidates, inspect per-gate JSON and RDF traces.
4. **Limited conclusion:** the controller detects and blocks
   these demonstrable defects, improving process control;
   it does not establish statistical AI quality gains.

## 7. Last-minute checks before submitting

- Confirm your name appears in the README and docs.
- Ensure the new repository is your submitted GitHub URL.
- Run `py -m unittest discover -s tests -v`.
- Run `py tools/pipeline.py` and inspect the real JSON.
- Open `evidence/replayed/controlled_trace.ttl` and
  `naive_trace.ttl`; point out the duplicate conversion.
- Look at the GitHub Actions run and its artifact, if CI ran.
- Confirm the group game on `main` remains unchanged.
- Explain that raw generated results are under
  `evidence/replayed/` locally and downloadable from CI.
  The verified comparison JSON and derived RDF trace snapshots
  are also committed under
  `evidence/verified_run_45322367482/`.
- Be ready to discuss every check without relying on AI.

## 8. Final short summary

> My main contribution is the process-control pipeline.
> I defined domain entities and constraints in an ontology,
> used them to guide AI code generation, and implemented
> executable gates so we can reject generated code that
> violates the domain rules. A controlled comparison and
> machine-readable evidence show exactly which problems
> those controls identify.


## 9. Last-minute additional demo

Show `prompts/REPAIR_CYCLE.md` and all three source files:
`naive_candidate.py`, `repair_candidate_v1.py`, and
`controlled_candidate.py`. The first repair addresses wrong actor
types and repeated human conversions; the second repair caps the
long-horizon forecast. Open `comparison.json` and
`repair_v1_shacl_report.txt` to show **real** constraint
violations, not merely a file containing SHACL declarations.

State clearly: the code candidates and corrections are AI-assisted,
but replaying the pipeline uses deterministic Python and
`pyshacl`, **not a live LLM API**. The three candidates are a
reproducible demonstration, not a statistical study of many independent
model outputs.
