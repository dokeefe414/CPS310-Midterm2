# Pipeline Design: Every Process-Control Stage

**Author:** Daniel O'Keefe — CPS 310 Midterm #2, Fall 2026.

## I. Problem statement and control objective

I am controlling the **AI-assisted software development process**, not merely
controlling a zombie in the game. The AI's draft code is an untrusted proposal
that must satisfy a machine-readable specification before acceptance.

The goal is to build a small but nontrivial slice of the Zombie Game in which
humans and zombies interact through bite and conversion events, the population
is recorded, and a pure forecasting component predicts future counts.
A significant problem is that natural-language instructions are ambiguous:
"bite and convert a human" doesn't say what happens if the same human is bitten
twice in a tick, whether a non-zombie may issue a bite, or whether a forecast
is allowed to mutate the game state.

The ontology gives these implicit assumptions **explicit names, relationships,
and constraints**. A corresponding gate runner converts selected constraints
into executable checks. A candidate is accepted only after the gates pass.

## II. Complete nine-stage pipeline

Each stage has a specified **input, activity, control, output, and failure
response**. That is what makes it a controlled process instead of an ad hoc
sequence of ChatGPT answers.

### S0 — Scope and requirements baseline

**Input:** CPS 310 assignment requirements, original game's entity concepts,
individual-work boundary.  
**Action:** Select one testable slice: one zombie, two humans, queued bites,
conversion, count history, and a prediction. Define non-goals: no 10k-agent
simulation, no Tkinter, no PostgreSQL, no reimplementation of Owen's policy.  
**Control:** Prevent scope creep and prohibit modifying the group project.
The independent repository is a hard boundary.  
**Output:** This specification and [README](../README.md).  
**If it fails:** Narrow the scope but retain a meaningful conversion rule,
a real event pathway, and a measurable prediction.

### S1 — Identify ontology concepts

**Input:** Requirements baseline.  
**Action:** Extract nouns (Agent, Human, Zombie, Event, Simulation,
Prediction), roles (actor, target, source human, created zombie), hierarchy
(ArmedHuman is Human is Agent), and constraints.  
**Control:** Keep one canonical vocabulary for prompting, code review, and
testing.  
**Output:** Concept map in [ONTOLOGY_GUIDE](ONTOLOGY_GUIDE.md).  
**If it fails:** Resolve terminology conflicts before generating code.

### S2 — Formalize ontology and contracts

**Input:** Concept map.  
**Action:** Write `ontology/zombie_ontology.ttl` (RDF/OWL classes and
properties), `ontology/shapes.ttl` (SHACL node/property constraints), and
`ontology/constraints.json` (versioned executable-gate contract).  
**Control:** `ontology_gate()` parses both Turtle files and checks that
required class declarations, subclass axioms, and event-property domains/
ranges exist. This blocks accidental removal of required vocabulary.  
**Output:** Version-controlled ontology artifacts.  
**If it fails:** Reject the ontology or revise the manifest and constraints
*before* changing candidate code. Do not silently weaken the tests to pass.

### S3 — Construct prompts with constraints

**Input:** Ontology + acceptance gates.  
**Action:** Give an AI assistant the entity types, event-flow requirements,
explicit "no duplicate conversion" condition, expected population bound,
and forecast purity requirement. Request a small `MiniGame` API that
can be tested independently.  
**Control:** Require `enqueue_bite(actor,target)`, `step()`,
`forecast(horizon)`, `humans`, `zombies`, `events`, and `history`.
Specify that the AI must **not edit production code** or rely on a GUI/DB.  
**Output:** Full prompt text in [MAJOR_PROMPTS](../prompts/MAJOR_PROMPTS.md).  
**If it fails:** Re-prompt with the missing exact ontology term or invariant.
Record the revised prompt rather than accepting undocumented behavior.

### S4 — Generate and isolate code candidates

**Input:** Baseline and controlled prompts.  
**Action:** Save two AI-assisted small candidates:
`demo/naive_candidate.py` and `demo/controlled_candidate.py`.  
**Control:** They use identical public interfaces, identical initial
state, and no imports from or writes to the full group Zombie Game.
The baseline illustrates typical missing constraints, while the
controlled candidate is designed to satisfy the contracts.  
**Output:** Two reviewable Python files, retaining the failing candidate
rather than deleting it.  
**If it fails:** Fix generated syntax/import problems before comparing
semantic behavior; preserve the pre-repair draft for traceability.

### S5 — Static semantic vocabulary gate

**Input:** Ontology and manifest.  
**Action:** Parse Turtle and check required classes, inheritance,
property types, domain and range, and declared SHACL shapes.  
**Control:** Machine-readable definitions must match the listed required
concepts. A missing `ConversionEvent` or incorrect `actor` range is
not a subjective "looks fine" issue.  
**Output:** `ontology_gate` pass/fail in `comparison.json`.  
**If it fails:** Do not accept generated code; correct ontology artifact
or clearly version and justify changed requirements.

### S6 — Executable behavior gates G1-G5

**Input:** Candidate implementation + ontology-derived rules.  
**Action:** Apply exactly the same adversarial sequence of two duplicate
zombie bites and one invalid human-as-actor bite. Then request a
three-tick forecast.  
**Control:** Test duplicate conversion, actor/target roles,
nonnegative/bounded population and live health, purity/bounds of the
forecast, and the exact expected final state.  
**Output:** Five named booleans for each candidate; independent
`unittest` regression tests.  
**If it fails:** Reject/repair the candidate; don't substitute
explanations for failing assertions.

### S7 — Capture an audit trail

**Input:** Recorded runtime events and gate booleans.  
**Action:** Convert `BiteEvent` and `ConversionEvent` records into
RDF triples, save them as `naive_trace.ttl` and
`controlled_trace.ttl`, and write a structured `comparison.json`.  
**Control:** Every reported comparison is traceable to a concrete
test input, actual candidate behavior, and a named rule. The
pipeline prints a short summary, and GitHub Actions uploads full traces.  
**Output:** Generated `evidence/replayed/` and CI run artifact
`ontology-demo-evidence`.  
**If it fails:** Treat the run as incomplete; do not claim results
without the underlying evidence.

### S8 — Human review, correction, and release

**Input:** Gates, traces, tests, prompt specifications, prior draft.  
**Action:** Interpret failures, explain causes, review whether
test constraints faithfully reflect the domain, add regression tests,
and finalize the independent GitHub submission.  
**Control:** No acceptance until required gates pass and the owner can
describe the system and its limitations. Do not automatically merge
changes to the group game.  
**Output:** README, design argument, provenance, defense guide,
CI evidence, and reproducible commands.  
**If it fails:** Revise requirements and test coverage transparently;
keep an audit trail and rerun every gate.

## III. Gate specification and traceability

| Gate | Ontology-level source | Exact executable behavior | Controlled by |
| --- | --- | --- | --- |
| G1 | ConversionEvent.sourceHuman (at most one conversion per demonstrated tick) | Unique source human across conversions; expected exactly one conversion | `run_case()` duplicate-source check |
| G2 | BiteEvent.actor → Zombie; target → Human | Assert actors belong to original zombie set and targets to original human set | `run_case()` role validation |
| G3 | PopulationSnapshot/count invariants | Live population bounded by initial capacity, nonnegative counts, positive HP for live humans | `run_case()` bounded-population check |
| G4 | Prediction computed by ForecastObserver | Calling forecast does not change state; predicted count within valid range | `run_case()` deepcopy purity check and bound |
| G5 | Scenario semantics (H1 lethal hit, H2 invalid actor) | H1 gone, H2 survives with 2 HP, exactly 2 zombies and 1 conversion | `run_case()` expected-case check |
| G6 | Policy isolation and unchanged group implementation | Optional SHA-1 Git blob and default policy-dispatch marker audit | `production_gate(--group-repo)` |

**Important distinction:** Not every rule is directly expressible by
plain OWL classes and ranges. In particular, "unique per tick" is a
closed-world temporal constraint. We give it a SHACL-style shape for
the *single-tick trace* and enforce it in deterministic Python.
The repository does **not** implement a full OWL reasoner or general
SHACL validation engine.

## IV. Why these controls work

**Requirement ambiguity:** A broad prompt leaves event roles, identity,
state mutations, and invariants implicit. Ontology class names and
property constraints make these explicit and referable.

**Type correctness:** Role checks reject events where a non-zombie
initiates a bite. A natural-language code review can miss this; the
gate deliberately constructs an adversarial event.

**Update consistency:** Handling queued conversions once avoids a single
dead human yielding two new zombies. The gate checks event trace and
actual surviving population, not just whether an exception occurred.

**Separation of concerns:** Read-only `forecast()` prevents a predictive
component from mutating game state. This is directly checked by
comparing a deep copy of all instance attributes before/after calling
the function.

**Regression prevention:** The same suite can be rerun against future
AI edits. Named `G1`–`G5` booleans make failures localizable.

**Reproducibility:** A fixed initial state and event sequence let
reviewers recreate the exact observed behavior, unlike a free-form
video demonstration alone.

**Auditability:** JSON, RDF traces, explicit prompts, ontology versions,
and Git commits document the decision path.

These are improvements in **development control**, not proof that
the constrained candidate is the fastest, most elegant, or generally
best program. The small side-by-side demo isolates what the gates
can establish.

## V. Comparison against naive AI development

| Dimension | Naive prompt-and-accept | Ontology-controlled workflow |
| --- | --- | --- |
| Requirements | Implicit prose | Named entities, roles, invariants |
| Input validation | May be omitted | Actor and target types are checked |
| Conversion semantics | Multiple queued hits may convert twice | Per-tick uniqueness gate |
| Forecast safety | Can extrapolate beyond population bound | Bounded, read-only forecast gate |
| Acceptance | Visual review, perhaps "runs" | Objective test and complete gate report |
| Debuggability | "Something went wrong" | G1-G5 pinpoint violated contract |
| Evidence | Screenshot or subjective statement | JSON, RDF trace, unit-test and CI record |
| Team safety | Easy to edit production files | Standalone submission with optional read-only audit |
| Failure response | Edit until output looks plausible | Fail, diagnose, repair, rerun, preserve record |

In the intentionally adversarial scenario, the uncontrolled reference
draft exposes all five selected failures, while the controlled draft
satisfies all five. **This does not estimate real-world failure rates**:
one curated scenario and two reference candidates cannot support
general accuracy, time-saved, or statistical claims.

## VI. What is implemented versus proposed

**Implemented:** Versioned RDF/OWL vocabulary, SHACL shapes, JSON gate manifest,
independent candidate modules, vocabulary checks with `rdflib`,
five executable candidate checks, optional group-repo integrity audit,
RDF trace export, comparison JSON, Python regression tests, automated
GitHub Actions workflow, full prompts and defense documentation.

**Not implemented or claimed:** Automated LLM API calls, full SHACL engine,
formal verification of the complete multiplayer group game, unbiased
multi-model A/B trials, statistical significance, full-scale concurrent
event processing, or integrated deployment of this mini-game.

## VII. Failure and repair example

Suppose the naive draft sees two lethal bites queued against `H1`.
Because it adds a conversion for each lethal check and does not block
the second conversion, `H1` can create two zombies. That violates
G1 and G3. A naive developer might only notice that the program ran.
The ontology-controlled response instead is:

1. Reject the candidate because the conversion source is not unique.
2. Preserve the failing `naive_trace.ttl`.
3. Explain the requirement in the next prompt: "At most one conversion
   of any source human in a tick."
4. Correct code to collect converted human IDs in a set.
5. Rerun the identical event sequence and all acceptance gates.
6. Record the new trace and code commit.

This creates a closed **specify → generate → verify → repair** loop.
