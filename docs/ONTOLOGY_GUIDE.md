# Understanding the Ontology

**Daniel O'Keefe · CPS 310 Midterm #2**

## 1. What is an ontology in this assignment?

An ontology is an **explicit shared model of what exists in a domain,
what kinds of things they are, and what relationships are permitted**.

For the Zombie Game, it captures concepts such as:

- A `Zombie` is an `Agent`.
- A `Human` is an `Agent`; an `ArmedHuman` is a `Human`.
- A `BiteEvent` must be associated with a zombie actor and a human target.
- A `ConversionEvent` links a source human to the new zombie.
- A `Prediction` belongs to a `ForecastObserver`.
- A policy decision belongs to the swarm policy, **not** the forecaster.

This vocabulary lets prompts, generated code, tests, and documentation
use consistent names rather than having different tools invent
different meanings for "convert," "attack," "population," or "forecast."

**An ontology is not the program itself.** The ontology says what
concepts and valid relationships should exist. The executable
pipeline checks selected consequences of those definitions.

## 2. The domain model

```text
                 Agent
                /     \
             Human    Zombie
               |
           ArmedHuman

Event
  |-- BiteEvent
  |       actor  ------> Zombie
  |       target ------> Human
  |
  |-- ConversionEvent
          sourceHuman ---> Human
          createdZombie -> Zombie

Simulation
  |-- produces PopulationSnapshot (zombieCount, initialPopulation, tick)
  |-- supports PolicyDecision ----chosenBy----> SwarmPolicy
  |-- produces Prediction --------computedBy--> ForecastObserver
```

The relationships in the drawing are reflected in
[`ontology/zombie_ontology.ttl`](../ontology/zombie_ontology.ttl).

## 3. Why three specification files?

### A. `zombie_ontology.ttl`: ontology vocabulary and relationships

This is written in **Turtle**, a text notation for RDF triples.
For example:

```turtle
zg:Zombie a owl:Class ;
    rdfs:subClassOf zg:Agent .

zg:actor a owl:ObjectProperty ;
    rdfs:domain zg:BiteEvent ;
    rdfs:range zg:Zombie .
```

This expresses that the class Zombie is a subclass of Agent, and
that `actor` connects a BiteEvent to a Zombie.

**Note about OWL/RDFS semantics:** Domain/range statements can enable
*inferences* (for example, inferring a thing is a Zombie when it
appears as an actor), rather than automatically rejecting an invalid
record. Under RDF/OWL's open-world assumptions, missing information
is not necessarily false. **Therefore these declarations alone do
not stop bad generated code.** That is why the next layers exist.

### B. `shapes.ttl`: declarative SHACL constraints

SHACL is a way to express validation conditions on RDF graphs,
including required properties and value types.

For example, the bite shape expresses that a BiteEvent should have
exactly one `actor` of class Zombie and exactly one `target`
of class Human.

The conversion shape requires one `sourceHuman` and one
`createdZombie`. The `HumanConvertedAtMostOnceShape` limits
the number of incoming `sourceHuman` references in the
**single-tick demonstration graph**.

The repo's pipeline **parses and checks the presence of these
shapes** but it does **not** run a complete SHACL engine. This is
an explicit limitation. The relevant violations are actually
detected by the Python contract checks explained next.

If someone later combines events across multiple ticks, the
single-trace uniqueness rule must be scoped by tick: one human
cannot be converted twice *within a single tick*. The shape
here does not have a built-in universal time-scoping mechanism.

### C. `constraints.json`: executable acceptance manifest

A JSON file names the required classes, subclass edges,
object-property relationships, and six gate IDs.

The file is deliberately readable by both a human and a script.
The `ontology_gate()` reads those names and verifies that the
Turtle ontology contains the corresponding triples.

Five gates are applied to both candidate implementations:

| ID | Ontology idea | Executable interpretation |
| --- | --- | --- |
| G1 | ConversionEvent source should be unique in a tick | Exactly one source H1 conversion in the demonstration and no duplicate source IDs |
| G2 | BiteEvent.actor is Zombie; target is Human | Reject/omit invalid H2 → H2 bite |
| G3 | PopulationSnapshot count invariants | Nonnegative counts and positive HP for surviving humans; population within starting capacity |
| G4 | Prediction comes from an observer | Forecast doesn't mutate state and returns bounded value |
| G5 | Expected domain-specific event outcome | After two hits against H1, H2 remains untouched and only one new zombie exists |
| G6 | Group game's source/policy is protected | Optional check against the group game, not part of the 5-gate demo score |

G1 and G5 overlap deliberately: G1 is a **general uniqueness property**,
whereas G5 is an **exact regression scenario**. G3 is a separate population
conservation constraint that can catch other mistakes.

## 4. Ontology versus program classes

The `zg:Human` term describes a **concept**. It is not automatically
the same object as `Human` in `Zombie_Game.py`.

The simplified candidate uses `MiniGame.humans` as a
`dict[id, hit_points]` and `MiniGame.zombies` as a set of IDs.
The ontology tells us the role and type of these IDs, while the
Python gate decides membership in the actual original human/zombie
sets. The event-to-RDF translator records example triples.

This is an intentional separation: one can validate a small component
of a complicated simulation without copying the whole 1,000-agent
GUI, database, and learning system.

## 5. A complete example

Input state:

```text
H1: Human, health = 1
H2: Human, health = 2
Z0: Zombie
initial population capacity = 3
```

Queued events in one tick:

```text
Z0 -> H1   (valid bite, lethal)
Z0 -> H1   (duplicate source conversion attempt)
H2 -> H2   (invalid: a Human is not a Zombie actor)
```

The ontology says the third event has the wrong actor type.
The per-tick conversion invariant says H1 cannot convert twice.
The accepted interpretation is: H1 disappears; a single zombie
Z_H1 appears; H2 stays alive at two HP; zombie count increases
from one to two.

The machine-readable event trace records `BiteEvent` and
`ConversionEvent` triples; the Python gates check exact population
state and event validity.

## 6. What the ontology controls (and what it does not)

**It controls** terminology, expected event roles, conversion
uniqueness, population invariants, forecast purity, the semantics
of one chosen test scenario, and whether the AI-generated candidate
is accepted by the demo pipeline.

**It does not control** every possible GUI bug, all multi-agent
races, future game balancing, SQL privileges, or the mathematical
correctness of the full Adaptive Kalman Filter. These are outside
this deliberately scoped midterm demonstration.

## 7. How to explain it in one paragraph

> I used an ontology to describe the key objects and rules in the
> Zombie Game in a formal way. For example, it defines a Zombie and
> a Human as agents, and says a bite event should connect a zombie
> to a human. I then made those rules part of a verification pipeline.
> Instead of trusting AI-generated code just because it runs, I test
> whether it follows those domain rules, and reject the candidate
> if it violates them.

## 8. Files to point out during a defense

- [Ontology vocabulary](../ontology/zombie_ontology.ttl): examples of
  `owl:Class`, `rdfs:subClassOf`, and `owl:ObjectProperty`.
- [SHACL shapes](../ontology/shapes.ttl): examples of min/max counts
  and required event roles.
- [JSON gate manifest](../ontology/constraints.json): the list of
  things the checker must verify and the named acceptance gates.
- [Pipeline source](../tools/pipeline.py): `ontology_gate()`,
  `run_case()`, and `event_graph()`.
- [Comparison guide](DEMONSTRATION_AND_COMPARISON.md): the exact
  same test scenario and outputs for both implementations.
