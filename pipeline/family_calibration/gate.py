#!/usr/bin/env python3
"""The family gate (Gemini, via the shared cross-vendor runner).

Successor to pipeline/work/gate_family_assignments.py (RULES #23). The gate is
blind: it receives the assignments and the definitions document, never the
corruption key, never which items were touched.

It also receives no proposer_confidence and no proposer reasons — the
population has neither, and an instrument's input carries only values that
exist in the data (RULES #15).

Provenance: the plant stamp on the gated file is copied into every chunk
output, so score.py can refuse a mismatched set of artifacts (RULES #13).

Run from the repo root:  python3 pipeline/family_calibration/gate.py
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pipeline"))
from crossvendor_run import MODEL, run_chunked  # noqa: E402

DEFS = (ROOT / "docs" / "FAMILY_DEFINITIONS.md").read_text(encoding="utf-8")

PROMPT = """You are the independent gate for a relation-FAMILY assignment pass on a verified knowledge graph of C.G. Jung's Collected Works. A proposer has assigned each edge to one family. Your job is to judge each assignment against the definitions document below, which is the governing standard.

The edge itself — subject, relation, object, quote — is already verified and is NOT on trial. Only the FAMILY ASSIGNMENT is. `relation` is the verbatim frozen string; `relation_effective` is the normalized form where one exists (identical otherwise). Judge with both in view — the quote decides, per the definitions.

For each item judge:
(1) Does the assigned family match the definition, read against this edge's context (subject, object, qualifiers, quote)?
(2) Do the document's BOUNDARY RULES place it elsewhere? Check especially: the direction test separating symbolization from manifestation; composition versus structural-position; the identity/correspondence rule on indistinguishability and equivalence; sequence versus dependence; psychic-effect as the LAST family to check.
(3) Is a refusal (unclassified / not-a-relation) justified, or is a family plainly available?

VERDICT per item:
- SUPPORTED — the assignment is right, or defensible against a close alternative.
- PARTIAL — usable but a better family exists under the rules; name it.
- WRONG — the assignment contradicts the definition or a boundary rule; name the family that should apply.

Be strict about boundaries and lenient about genuinely arguable calls. Say which family you would assign whenever you do not answer SUPPORTED.

Respond with ONLY a JSON array: [{"n": <id>, "verdict": "SUPPORTED|PARTIAL|WRONG", "should_be": "<family or empty>", "reason": "<one sentence>"}] covering every item given.

=== DEFINITIONS DOCUMENT ===
""" + DEFS + "\n=== END DEFINITIONS ==="

CARRY = ("subject", "relation", "object", "relation_effective", "qualifiers",
         "layer", "citation", "quote")


def main(work, chunk):
    gated = json.loads((work / "family_assignments_to_gate.json").read_text())
    stamp = {k: gated[k] for k in ("calibration_seed", "planted_at")}

    items = [{"n": a["id"], **{k: a[k] for k in CARRY if k in a},
              "assigned_family": a["family"]}
             for a in gated["assignments"]]

    print(f"{len(items)} assignments to gate against "
          f"{DEFS.splitlines()[0].strip('# ')}")
    prefix = str(work / "family_gate")
    run_chunked(items, PROMPT, prefix, chunk=chunk)

    for f in sorted(work.glob("family_gate_c*.json")):
        d = json.loads(f.read_text())
        if isinstance(d, list):
            f.write_text(json.dumps({**stamp, "gate_model": MODEL, "verdicts": d},
                                    indent=1, ensure_ascii=False))
    print(f"stamped every chunk with calibration_seed {stamp['calibration_seed']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default=str(ROOT / "pipeline" / "work"))
    ap.add_argument("--chunk", type=int, default=15)
    a = ap.parse_args()
    main(pathlib.Path(a.work), a.chunk)
