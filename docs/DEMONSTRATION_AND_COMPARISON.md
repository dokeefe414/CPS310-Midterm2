# Demo and Comparison: Naive vs. Ontology-Controlled Development

**Author:** Daniel O'Keefe — CPS 310 Midterm #2

## 1. What this demonstration establishes

This is a **small, deterministic demonstration of process control**:
two separate AI-assisted reference implementations are run against
the *same* domain scenario, and the outputs are judged by the
*same* ontology-derived acceptance criteria.

The control strategy is **not** to hope that the AI "understands"
the rules. It is to state the rules, then **execute tests that can
reject a draft even if its Python code runs without throwing an
exception**.

This is an intentionally narrow example. The produced mini-game has
a bite/conversion event queue, typed IDs, human hit points, population
history, and a simple forecast; it is not the large GUI-driven group
project.

## 2. The exact scenario

Initial state:

| Entity | Type | Initial state |
| --- | --- | --- |
| `H1` | Human | 1 HP |
| `H2` | Human | 2 HP |
| `Z0` | Zombie | Alive |
| **Total** | 3 agents | 2 humans + 1 zombie |

The tester queues these three events **in this order, in one tick**:

```text
enqueue_bite("Z0", "H1")  # valid and lethal
enqueue_bite("Z0", "H1")  # duplicate targeting same human
enqueue_bite("H2", "H2")  # invalid actor: a human cannot bite
step()
forecast(horizon=3)
```

The correct outcome is precisely:

```text
humans = {"H2": 2}
zombies = {"Z0", "Z_H1"}
population = 1 + 2 = 3
zombie history = [1, 2]
one ConversionEvent from H1 to Z_H1
one valid BiteEvent Z0 -> H1
H2 never loses health
prediction is pure and lies within [0, 3]
```

For the simple trend forecaster in the controlled demo,
`forecast(3)` starts from zombie count 2, with last observed
change +1, extrapolates to 5, then clips to the total initial
capacity of 3. **Thus the expected forecast is 3**.

**This is not the production Adaptive Kalman Filter**. It is a
minimal observer used to demonstrate controlled boundaries.

## 3. What happens without the ontology constraints

In [`demo/naive_candidate.py`](../demo/naive_candidate.py),
the event loop checks whether a target ID exists among humans,
but it **does not verify the actor ID is a zombie**. It also
queues a conversion after every lethal hit even if the same
source human was already queued for conversion. It records
converted zombies with distinct generated IDs and does not
cap the long-horizon forecast.

For this scenario, the candidate therefore:

1. Processes the first bite against H1 (HP reaches 0).
2. Processes the second bite against the same still-present H1
   (HP becomes -1) and queues a **second conversion**.
3. Processes the invalid H2→H2 bite, decrementing H2 from
   2 HP to 1 HP even though H2 is not a zombie.
4. Generates two zombies from H1, creating 3 zombies total,
   while H2 remains the only human: **4 surviving agents**
   from only 3 initial agents.
5. Uses the naive last-difference extrapolation
   `3 + 3*(3-1) = 9`, an impossible zombie count given the
   three-agent initial capacity.

The draft executes without an exception. That is exactly the
development risk being demonstrated: **syntactically runnable
does not imply semantically valid.**

## 4. What happens with ontology-controlled generation

[`demo/controlled_candidate.py`](../demo/controlled_candidate.py)
implements these changes:

- Validate that `actor` is currently in the zombie set.
- Validate that `target` is currently a human.
- Skip the already-converted target within the current tick
  using a `conversions` set.
- Create only one deterministic zombie ID `Z_H1`.
- Extrapolate population but clip within the initial capacity.
- Keep `forecast()` pure: it returns a number without
  mutating humans, zombies, queues, events, or history.

The result matches the required one-conversion semantics.

## 5. Exact gates and expected verdicts

The repository's [`tools/pipeline.py`](../tools/pipeline.py)
computes the following independent boolean outcomes:

| Gate | Description | Naive reference | Controlled reference |
| --- | --- | --- | --- |
| **G1** | Exactly one unique conversion source H1 | FAIL | PASS |
| **G2** | All recorded bite roles valid | FAIL | PASS |
| **G3** | Population/HP bounds valid | FAIL | PASS |
| **G4** | Read-only, bounded three-tick forecast | FAIL | PASS |
| **G5** | Exact final scenario matches specification | FAIL | PASS |
| **Total** | Per-candidate gates | **0 / 5 expected** | **5 / 5 expected** |

These outcomes were **verified by GitHub Actions run #10**:
[View passing tests and evidence artifact](https://github.com/dokeefe414/CPS310-Midterm2/actions/runs/45322367482).
The **actual CI-produced JSON report** is permanently archived at
[\`evidence/verified_run_45322367482/comparison.json\`](../evidence/verified_run_45322367482/comparison.json).
Both candidates were tested with the same fixed input, and the job uploaded
the original generated RDF traces as downloadable artifacts.

An additional **G6** audits the external group game's original
Thompson Sampling file *only when the group's local path is supplied*.
It is **not silently counted as passed** when the group game
is absent from the standalone repo.

## 6. Reproduce the output yourself

From PowerShell in the Midterm #2 repository:

```powershell
py -m pip install -r requirements.txt
py -m unittest discover -s tests -v
py tools/pipeline.py
```

Or choose a different evidence directory:

```powershell
py tools/pipeline.py --output-dir evidence/local-defended-run
```

The command saves:

```text
evidence/replayed/
    comparison.json
    naive_trace.ttl
    controlled_trace.ttl
```

These reports are generated at runtime; they are not manually invented
prewritten results. A verified archival snapshot is also checked into Git. The
[GitHub Actions workflow](../.github/workflows/ontology-validation.yml)
also runs the tests and the pipeline automatically and uploads
these files as an artifact named `ontology-demo-evidence`.
The artifact remains available under its workflow run subject
to GitHub artifact retention settings.

### How to read `comparison.json`

```json
{
  "ontology_gate": {"pass": true, "issues": []},
  "production_gate": {"status": "not_checked", "pass": null},
  "naive": {
    "checks": {"G1_unique_conversion": false},
    "passes": 0,
    "total_checks": 5
  },
  "controlled": {
    "checks": {"G1_unique_conversion": true},
    "passes": 5,
    "total_checks": 5
  }
}
```

The fragment above shows the **field structure and representative
values**, not a complete captured run. The generated report contains
all G1-G5 booleans, full event lists, population histories, and
final human HP; inspect it for the real result.

### How to read the Turtle event traces

`naive_trace.ttl` should include multiple
`ConversionEvent` nodes with `sourceHuman` pointing to H1.
It should also include a BiteEvent with `actor` H2, recorded as
a Human. `controlled_trace.ttl` should have only the accepted
Z0→H1 BiteEvent and one ConversionEvent mapping H1→Z_H1.

These are structured artifacts that let a reviewer inspect
*why* a gate failed, beyond just reading a pass/fail count.

## 7. Why this is a development-pipeline demonstration

A weak workflow stops after AI code **runs**.
This one has specification, candidate generation, static
concept validation, a shared adversarial scenario, objective
invariant checks, trace generation, and required human review.
The control is the **accept/reject decision around AI outputs**.

Specifically:

| Process concern | Controlled artifact |
| --- | --- |
| Ambiguous domain vocabulary | RDF/OWL ontology |
| Missing event relationships | SHACL shapes and JSON required-relations gate |
| Unchecked conversion invariant | G1, G3, G5 |
| Incorrect event roles | G2 |
| Forecast interfering with game | G4 |
| Unrepeatable human inspection | Fixed test case, unit suite, CI workflow |
| No intermediate evidence | Event-level RDF traces and comparison JSON |
| Danger to team project | Standalone repository plus optional G6 external integrity check |

## 8. Why the conclusion is limited but defensible

The case is **purposely adversarial** and the candidates are
prepackaged AI-assisted reference drafts. Their differences are not
statistical estimates of the chance that a model generates bugs
under broad versus constrained prompting. They do not measure
development time or claim all ontology constraints are covered.

What *is* demonstrated is narrower and testable:

> Under one identical nontrivial input, five checks derived from
> the ontology identify five semantic failures in an unconstrained
> reference implementation and accept a constrained implementation
> that satisfies the specified contracts.

The result supports the value of **explicit software controls,
repeatable validation, and auditable evidence**, not a universal
claim that any particular language model is "better".

## 9. Next experiment if asked to go further

To perform a true empirical AI prompt experiment, sample multiple
independent model outputs under P2 and P3, preserve every prompt
and raw response, import each candidate into a common test harness,
and report gate pass rates across attempts. Keep model settings
and the comparison methodology matched. This is **future work**,
not a claim about the current submission.
