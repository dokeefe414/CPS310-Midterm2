# CI Verification Protocol

**Student:** Daniel O'Keefe — CPS 310 Midterm #2.

This document is the checklist for independently validating the submission:

1. Install rdflib with `python -m pip install -r requirements.txt`.
2. Run `python -m unittest discover -s tests -v`.
3. Run `python tools/pipeline.py --output-dir evidence/replayed`.
4. Inspect `comparison.json`, `naive_trace.ttl`, and `controlled_trace.ttl`.
5. Confirm that a missing local group repository yields external audit status `not_checked`, not false success.
6. Verify that the unmodified group `models.py` is not included or written by this repository.

The GitHub Actions workflow runs steps 1–4 and saves the three reports as the `ontology-demo-evidence` artifact. If the workflow fails, investigate the failing check rather than asserting that the demo passed.
