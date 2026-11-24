# Reproducible Demo Evidence

**Student:** Daniel O'Keefe · CPS 310 Midterm #2

The actual evidence files are generated from the committed source when the
pipeline runs. This makes the evidence **repeatable rather than manually
manufactured**.

Run:

```powershell
py -m pip install -r requirements.txt
py -m unittest discover -s tests -v
py tools/pipeline.py
```

The command creates:

```text
evidence/replayed/comparison.json
evidence/replayed/naive_trace.ttl
evidence/replayed/controlled_trace.ttl
```

- **comparison.json:** required ontology declarations present/missing,
  optional group audit status, and G1–G5 booleans and observed final
  states for naive and controlled candidates.
- **naive_trace.ttl:** the event graph revealing duplicate
  ConversionEvent source H1 and invalid BiteEvent actor H2.
- **controlled_trace.ttl:** the event graph where H1 is converted
  once and only valid zombie bite events are accepted.

The `evidence/replayed` directory is intentionally Git-ignored to avoid
check-in churn. The
[GitHub Actions workflow](../.github/workflows/ontology-validation.yml)
generates these files as a CI job and uploads them under an artifact named
`ontology-demo-evidence` on each successful run. Check the Actions tab
of the repo to see the exact run status and downloadable artifacts.
Artifacts are subject to GitHub's retention policy.

The expected standalone demo scores are **0/5** for the naive reference
and **5/5** for the controlled reference. Do not treat these numbers as
a measured pass rate over independent AI generations.

**Optional G6:** Run
`py tools/pipeline.py --group-repo ..\CPS310-Zombie-Game`
if the original repository is cloned as a sibling directory.
Without that input the external audit status is `not_checked`,
not silently passed.
