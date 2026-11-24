# AI-Assisted Repair Cycle — Prompts, Outputs, Failures, and Corrections

**Daniel O'Keefe — CPS 310 Fall 2026 Midterm #2.**  
**Development session:** November 24, 2026.  
**Model-assisted coding environment:** ChatGPT (GPT-6), with human review and GitHub commits.  
**Scope:** A standalone three-agent Zombie Game demonstration, not changes to the group project.

## Provenance: what was actually done

This submission was developed in a conversational AI coding session.
The original broad-prompt and constrained reference candidates predate
this repair-cycle update. In this session an additional **intermediate
AI-assisted repair** was constructed and committed as
[`demo/repair_candidate_v1.py`](../demo/repair_candidate_v1.py).
The final compliant reference already existed at
[`demo/controlled_candidate.py`](../demo/controlled_candidate.py).

**Do not describe the following prompts as immutable historical API
transcripts.** They are complete, replayable **task specifications**
corresponding to the edits and acceptance criteria used in this
documented AI-assisted development cycle. The externally observed
evidence is the versioned Python code, actual GitHub Actions execution,
and generated reports — not an unverifiable claim about exact model
sampling or hidden reasoning. No paid AI inference API is invoked by
`tools/pipeline.py` when the demo is replayed.

## Full prompt R0 — Identify the failure in the naive implementation

> Review `demo/naive_candidate.py` against the ontology and
> `ontology/constraints.json`, specifically gates G1–G5.
> Keep the game initial state H1 at one HP, H2 at two HP,
> and Z0 as a zombie. Execute the same event sequence:
> Z0 bites H1 twice and H2 attempts to bite H2, all in one tick.
> Treat the code as untrusted even if it runs.
> Identify exactly which domain rules fail and what state and
> event records show each failure. Do not edit the naive
> reference file, since it is needed as the baseline artifact.
> Explain the proposed repair in small, testable steps and do
> not edit the group's original Zombie Game repository.

**Baseline file:** [`demo/naive_candidate.py`](../demo/naive_candidate.py).

**Failure mechanism:** The naive code checks that the target is a
human but not that the actor is a zombie; multiple hits can queue
multiple conversions for H1. Its naive extrapolation also returns
an impossible zombie count in the selected long-horizon example.

## Full prompt R1 — First repair: event validity and conversion uniqueness

> Implement the first repair as a new standalone Python file
> `demo/repair_candidate_v1.py`, preserving the same MiniGame
> public API and initial entities as the baseline.
> Use the ontology's BiteEvent.actor→Zombie,
> BiteEvent.target→Human, and ConversionEvent.sourceHuman
> relationships as explicit conditions.
> Reject bites from actors not in the current zombie set,
> ignore targets no longer alive, and track a set of humans
> pending conversion so each human can convert no more than
> once during a tick. Use a deterministic zombie ID.
>
> **For incremental validation, do not change the existing
> last-change trend forecasting expression yet**. This first
> repair deliberately isolates the event-processing controls
> so that the forecast-bound gate can identify the remaining
> defect. Do not touch `demo/naive_candidate.py`, the
> production game or the group's `models.py`.
> Record which gates this version passes and fails.

**Intermediate code artifact:** [`demo/repair_candidate_v1.py`](../demo/repair_candidate_v1.py).

**Intended/observed gate progression:** The event and final-state
checks G1, G2, G3, G5 now pass. G4 remains unsatisfied because a
three-tick forecast returns 5 zombies while only 3 agents ever
existed in the simulation.

## Full prompt R2 — Second repair: bounded, read-only prediction

> Evaluate the intermediate MiniGame against the remaining
> acceptance rule G4. A Prediction must be produced by the
> ForecastObserver without mutating any live game attributes.
> Any predicted zombie count must be within zero and the
> initial population capacity, inclusive.
>
> Produce a final controlled variant retaining the validated
> event-processing behavior. Validate the integer-positive
> forecast horizon and cap the forecast to `initial_total`.
> Do not alter the initial state, event IDs, or expected
> 3-event scenario. The final implementation must pass all
> G1–G5 gates; preserve the intermediate file for comparison.
> Do not claim the example trend forecast is the full
> group's Adaptive Kalman Filter.

**Final code artifact:** [`demo/controlled_candidate.py`](../demo/controlled_candidate.py).

The relevant final expression is:

```python
prediction = self.history[-1] + horizon * recent_change
return min(self.initial_total, max(0, prediction))
```

The final reference already contains this capacity cap and stricter
horizon validation. It is used as the destination of the repair-cycle
illustration; do not present it as a new independent model output.

## Full prompt R3 — Make the ontology executable and verify the repairs

> Implement real SHACL validation of the event graphs using
> `pyshacl`. Retain `rdflib` parsing and the existing independent
> Python G1–G5 checks. For every candidate, generate a
> single-tick RDF graph of accepted BiteEvent/ConversionEvent
> records, a PopulationSnapshot with observed counts and
> starting capacity, and a Prediction with its forecaster and
> population capacity.
>
> Write SHACL shapes that check required actor/target classes,
> conversion source uniqueness within the one-tick graph,
> snapshot survivor count no greater than initial count,
> and predicted count no greater than capacity.
> Evaluate naive, intermediate repair, and final controlled
> candidates with the same event sequence. Save a structured
> comparison JSON, three event traces, and individual SHACL
> reports. Do not use reasoning/inference that converts invalid
> bite actors into zombies and masks an error.
> Exit nonzero if the controlled implementation fails any Python
> or SHACL acceptance criterion. Add unit tests and run the
> workflow on GitHub Actions. Preserve the exact results.

**Implementation:** [`ontology/shapes.ttl`](../ontology/shapes.ttl),
[`tools/pipeline.py`](../tools/pipeline.py),
[`tests/test_pipeline.py`](../tests/test_pipeline.py),
and [GitHub Actions](../.github/workflows/ontology-validation.yml).

## Reproducing the results

Run from the root of the individual repository:

```powershell
py -m pip install -r requirements.txt
py -m unittest discover -s tests -v
py tools/pipeline.py
```

The runner writes `comparison.json` with `naive`,
`repair_v1`, `controlled`, and `shacl_validation`.
It also saves:

```text
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

### Gate trajectory under the fixed adversarial case

| Implementation | Expected Python gates | Expected SHACL result | Meaning |
| --- | --- | --- | --- |
| Baseline reference | 0 / 5 | Nonconformant | Invalid actor, repeated conversion, excess population and forecast |
| Repair v1 | 4 / 5 | Nonconformant | Event rules repaired; prediction still exceeds capacity |
| Controlled reference | 5 / 5 | Conformant | Selected rules enforced on this one scenario |

**Review the actual CI run before citing these numbers as results.**

### Why this is a genuine control loop

A process that only produces the final corrected file hides the
mechanism. Preserving the baseline, intermediate revision, and
final corrected code allows a reviewer to observe:

1. A **specification**: ontology vocabulary, SHACL rules and G1–G5.
2. A **candidate**: the naive file.
3. **Failure evidence**: test report and event RDF trace.
4. A **targeted repair**: the intermediate file fixes event semantics.
5. A second **failure**: forecast capacity remains violated.
6. A final **repair**: bounded, read-only forecast.
7. **Re-validation**: same tests and machine-readable evidence.

This demonstrates a controlled feedback loop on one example.
The reference files are not independent statistical samples of
a language model; the pipeline does not autonomously call GPT-6
during `py tools/pipeline.py`. Automated generation through
an external LLM API and unbiased multi-trial testing would be
separate future extensions.
