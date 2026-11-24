# All Major AI Prompts and Reproducible Prompt Protocol

**Author:** Daniel O'Keefe · CPS 310 Midterm #2 · Fall 2026

This file makes the prompts explicit rather than merely saying "AI helped."
Each prompt includes the **objective**, **input**, **full replayable text**,
and **expected artifact**. The baseline and ontology-controlled source files
were produced with AI assistance during development of this submission.

**Provenance limitation:** These are **complete, reconstructed/replayable
prompt specifications** for the supplied reference implementations.
They are **not asserted to be verbatim historical ChatGPT message logs**
or a randomized experiment across different AI accounts. The repo does
not include hidden model reasoning or an external API transcript.
A person can copy these prompts into a free-tier AI tool to reproduce
and further evaluate the pipeline.

Each prompt is bounded by the source file locations; do not give AI write
permission to the group `CPS310-Zombie-Game` repository.

---

## P0 — Requirements and system boundary

**Purpose:** Extract and formalize the individual Midterm #2 assignment
before asking AI to write any code.

**Full prompt:**

> You are assisting an individual CPS 310 student with an assignment to
> design and implement an ontology-controlled AI-driven development process
> for an existing Zombie Game Simulation Framework.
>
> The submission must explicitly state every stage of the pipeline, explain
> the control design, rigorously compare it with naive AI development,
> include all major prompts, and supply a runnable demonstration with
> concrete outcomes and intermediate ontology artifacts on GitHub.
>
> Design the smallest *nontrivial* independently runnable game slice that
> demonstrates these requirements without changing the group's original
> `Zombie_Game.py`, `models.py`, or other game-theory code.
> Preserve meaningful agent types, bite events, conversion, population,
> and a small read-only forecast.
>
> Output a scope statement, a list of entities and invariants, non-goals,
> the exact pipeline stages, and acceptance criteria. Distinguish anything
> implemented from what is only proposed. Do not claim empirical results
> until code has actually been executed.

**Output:** The S0/S1 portions of
[`docs/PIPELINE_DESIGN.md`](../docs/PIPELINE_DESIGN.md).

## P1 — Ontology design

**Purpose:** Convert informal domain concepts into named, reviewable
machine-readable constraints **before** accepting AI-generated code.

**Full prompt:**

> Act as a domain ontology designer. Using the Zombie Game scope below,
> specify the ontology in Turtle RDF/OWL, separate SHACL node shapes,
> and a JSON manifest listing the required vocabulary and tests.
>
> Required classes: Agent, Human, ArmedHuman, Zombie, Simulation, Event,
> BiteEvent, ConversionEvent, PopulationSnapshot, Prediction, Policy,
> SwarmPolicy, ForecastObserver, PolicyDecision.
>
> Required subclass relations: Human→Agent, ArmedHuman→Human,
> Zombie→Agent, BiteEvent→Event, ConversionEvent→Event,
> SwarmPolicy→Policy.
>
> Required event relations: BiteEvent.actor→Zombie;
> BiteEvent.target→Human; ConversionEvent.sourceHuman→Human;
> ConversionEvent.createdZombie→Zombie; Prediction.computedBy→ForecastObserver;
> PolicyDecision.chosenBy→SwarmPolicy.
>
> Acceptance rules: a human converts at most once per tick; accepted
> bite actors and targets have correct roles; live counts cannot exceed
> the initial population; forecasting must not mutate game state and
> predictions are bounded; a fixed duplicate/invalid bite scenario
> has one correct outcome.
>
> Use namespace
> `https://example.org/cps310/zombie-ontology#`.
> Save output as `ontology/zombie_ontology.ttl`,
> `ontology/shapes.ttl`, and `ontology/constraints.json`.
> Explain the limitations of RDF/OWL's open-world semantics: class range
> declarations are not automatically data-validation errors. SHACL
> expresses constraints, while our Python gates will enforce the
> demonstrated semantics. Do not pretend to have implemented a complete
> SHACL engine.

**Output:** Three files under [`ontology/`](../ontology/).

## P2 — Naive baseline candidate prompt (without ontology constraints)

**Purpose:** Provide a weak prompt for an illustrative comparison.
This prompt intentionally omits adversarial event semantics.

**Full prompt:**

> Write a short, independent Python class named `MiniGame` for a zombie
> game. Start with two human IDs H1 and H2 and one zombie ID Z0.
> H1 should have 1 hit point and H2 should have 2 hit points.
> Add an `enqueue_bite(actor, target)` method that queues bites,
> a `step()` method that processes bites and converts killed humans
> into zombies, and a `forecast(horizon)` method that estimates future
> zombie count from recent change.
>
> Keep lists or sets of humans and zombies, record the processed events,
> and keep a history of zombie counts. Keep the implementation simple.
> Use only the Python standard library. Do not import the original
> group Zombie Game. Output Python source for `demo/naive_candidate.py`.

**Output:** [`demo/naive_candidate.py`](../demo/naive_candidate.py).

**Why this is naive:** It does *not* require validation of event actor
and target roles, suppress duplicate conversions, preserve a population
invariant, or enforce a forecast purity/bounds contract. The supplied
baseline code intentionally retains these omissions for inspection.
It is a **demonstration draft**, not a frequency estimate of AI errors.

## P3 — Ontology-controlled candidate prompt

**Purpose:** Generate the same public API constrained by the ontology
and explicit invariants.

**Full prompt:**

> You are implementing a strictly ontology-controlled portion of a
> Python Zombie Game. The governing ontology defines:
> `Human` and `Zombie` as types of `Agent`; a `BiteEvent`
> has one Zombie `actor` and one Human `target`;
> a `ConversionEvent` links a Human `sourceHuman` to one
> `createdZombie`. A prediction belongs to a read-only
> ForecastObserver, not to the swarm policy.
>
> Build an independent Python `MiniGame` with exactly this API:
> `__init__()`, `enqueue_bite(actor,target)`, `step()`,
> `forecast(horizon)`, and public `humans`, `zombies`,
> `pending`, `events`, `history`, `initial_total`.
> The starting state is H1:1 HP, H2:2 HP, Z0:Zombie, with
> initial_total=3.
>
> Important required invariants:
> 1. Queuing a bite never immediately changes the population.
> 2. During `step()`, reject or ignore a bite if the actor is
>    not a currently valid Zombie or the target is not a living Human.
> 3. Convert each human *at most once* in a tick even if multiple
>    lethal bite events for that human are pending.
> 4. Use a deterministic conversion ID `Z_<human_id>` and record
>    BiteEvent and ConversionEvent dictionaries for audit.
> 5. Never allow the number of living humans + zombies to exceed
>    initial_total; living humans must have positive HP.
> 6. `forecast(horizon)` must not modify any object state, must reject
>    nonpositive/non-integer horizons, and must return a numeric count
>    clipped to [0, initial_total]. For simplicity, use the last
>    difference in zombie counts extrapolated by `horizon`.
> 7. Do not import or edit the production `Zombie_Game.py` or
>    `models.py`. This mini forecaster is *not* the group's
>    Adaptive Kalman Filter.
>
> Output only the complete file `demo/controlled_candidate.py`
> using the Python standard library. Document the invariants in
> docstrings/comments. Preserve the given API exactly.

**Output:** [`demo/controlled_candidate.py`](../demo/controlled_candidate.py).

## P4 — Ontology-to-tests and process-control prompt

**Purpose:** Build acceptance gates that test behavior rather than
trusting the code's own claims.

**Full prompt:**

> Write a deterministic ontology-derived verification harness in
> `tools/pipeline.py` using Python and rdflib.
>
> Read `ontology/zombie_ontology.ttl`,
> `ontology/shapes.ttl`, and `ontology/constraints.json`.
> Check the required OWL classes, subclass relations, object property
> domain/range statements, and declared SHACL shapes are present.
> **Do not claim to implement a general SHACL engine.**
>
> Import the two separate MiniGame implementations. Run the same
> adversarial case against both: H1 has 1 HP; H2 has 2 HP; Z0 is
> a zombie. Queue Z0→H1 twice and H2→H2 once within a tick;
> then step and request a three-tick prediction.
>
> Implement five named gates:
> G1 unique source human in conversions; G2 valid original
> actor/target roles; G3 bounded population and valid live HP;
> G4 forecast is pure (full state unchanged) and bounded;
> G5 exact expected outcome H1 converted once, H2 untouched,
> two zombies total.
>
> Save `comparison.json` with each boolean and the final state;
> save `naive_trace.ttl` and `controlled_trace.ttl` as RDF
> event evidence. Fail the command if ontology declarations are
> absent or the controlled candidate violates a required gate.
> Keep the naive failure report for teaching and debugging.
>
> Make any group-game protection check optional using
> `--group-repo PATH`; if omitted, report `not_checked`,
> NEVER falsely report that Owen's source was audited.
> Use the known group `models.py` Git blob hash only when
> an actual local clone has been supplied.
>
> Ensure the code has no Tkinter, PostgreSQL, or paid AI API
> dependency and that the GitHub Actions runner can execute it.

**Output:** [`tools/pipeline.py`](../tools/pipeline.py),
[`tests/test_pipeline.py`](../tests/test_pipeline.py),
and [.github workflow](../.github/workflows/ontology-validation.yml).

## P5 — Independent review and repair prompt

**Purpose:** Keep the evaluation stage independent of candidate
self-description and support controlled repairs.

**Full prompt:**

> Critically inspect both MiniGame candidates against the ontology
> and G1–G5 acceptance criteria. Do not assume generated code is correct.
> Identify the earliest counterexample for each failing gate and say
> which source operation causes it.
>
> First report the baseline's failures **without fixing its file**;
> it must stay as an auditable bad example. Then review the
> controlled candidate and propose the smallest correction for any
> failing gate. Do not weaken the ontology or tests just to make
> the candidate pass.
>
> Require a rerun of the same event sequence and regression suite
> after corrections. State which checks were actually run and which
> were not. Preserve the group `models.py` unchanged.

**Output:** Test failures/repairs, structured report, and
[`docs/DEMONSTRATION_AND_COMPARISON.md`](../docs/DEMONSTRATION_AND_COMPARISON.md).

## P6 — Evidence and defense prompt

**Purpose:** Make the submission understandable and independently
defensible, not just a collection of AI files.

**Full prompt:**

> Prepare a final CPS 310 Midterm #2 individual-submission README,
> a step-by-step process design with input/control/output/failure
> handling for every stage, ontology documentation, a controlled
> naive-versus-constrained comparison, and an oral-defense guide.
>
> Explain why each control is effective, exactly what it controls,
> what the demo empirically establishes, and what it cannot prove.
> Provide commands for Windows PowerShell and GitHub Actions.
> Include the student's printed name and a clear list of any files
> not uploaded, including generated artifacts stored in CI.
>
> Preserve the important distinction: this is a small,
> ontology-controlled *development process* demonstration,
> not a replacement for the team's full Zombie Game or Owen's
> contextual Thompson Sampling. Never fabricate AI transcripts,
> test runs, generalization statistics, or unobserved approvals.

**Output:** [README](../README.md), [pipeline rationale](../docs/PIPELINE_DESIGN.md),
[ontology explanation](../docs/ONTOLOGY_GUIDE.md),
[comparison guide](../docs/DEMONSTRATION_AND_COMPARISON.md),
and [defense guide](../docs/DEFENSE_GUIDE.md).

---

## How to reproduce or extend the AI-generation step

1. Copy prompt P2 into an accessible AI assistant, save the resulting
   draft under a new filename, and record the model/version and date.
2. Copy P3 into the **same** model under comparable settings, save the
   generated controlled draft under a separate filename.
3. Adapt the runner to load those alternative modules (identical
   MiniGame API required) and run the same gates.
4. Preserve raw prompts, raw outputs, corrected outputs, tests, and
   comparison evidence as separate commits.
5. If the professor wants a randomized comparison, repeat the trial
   across more independent model generations and report the sampling
   procedure and uncertainty, not only the successful cases.

**Key honesty rule:** This repository's prepackaged candidate files and
the prompt specifications allow deterministic review of the
control mechanism, but do not constitute independent model-generation
transcripts. Keep that distinction in your defense.


## P7–P10 — Final documented AI-assisted repair cycle

The [complete follow-up instructions and source-level evidence](REPAIR_CYCLE.md)
cover: R0 (analyze baseline failure), R1 (repair event roles and conversion
uniqueness), R2 (repair forecast bounds while preserving purity), and R3
(run actual SHACL validation and capture RDF reports). These provide explicit
full prompt text, artifact links and honest provenance. The first two
reference drafts were AI-assisted prepackaged examples rather than an
independent sampling experiment; the final pipeline executes deterministically
without an LLM API.
