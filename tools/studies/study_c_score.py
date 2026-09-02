#!/usr/bin/env python3
"""Study C — the scorer. Pre-set rules only; written before any result was seen.

    python3 tools/studies/study_c_score.py

Reads
  docs/experiments/study_c/c1_mechanical.json          (arm comparison)
  docs/experiments/study_c/c1_remainder_verdicts.jsonl (Fable, same-relation?)
  docs/experiments/study_c/c2_verdicts.jsonl           (Fable, entailment)
  pipeline/work/study_c/c2_truth.json                  (the plant key)

Writes docs/experiments/study_c/RESULT.json and RESULTS.md. Writing RESULT.json
stands the study down: the scheduled task stops when that file exists.

C1 has no pass bar by design — disagreement is the finding. C2 scores a catch
only when the gate flags the item AND names the corrupted element (RULES #14);
a flag with the wrong element is reported separately and never as a catch.
"""
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from study_c_lib import DOCS, WORK, read_jsonl  # noqa: E402

# The corrupted element each class expects the gate to name. Fixed here, before
# the run, so no verdict can be re-read as a catch after the fact.
EXPECTED_ELEMENT = {
    'modality_dropped': 'modality',
    'scope_dropped': 'scope',
    'direction_reversed': 'direction',
    'verb_strengthened': 'verb',
}


def rate(hit, total):
    return round(hit / total, 4) if total else None


def score_c1(mechanical, remainder_verdicts):
    rows = mechanical['rows']
    by_idx = {v['n']: v for v in remainder_verdicts}
    counts = Counter(r['verb_agreement'] for r in rows)

    judged_same = judged_diff = unjudged = 0
    disagreements = []
    for row in rows:
        if row['verb_agreement'] != 'REMAINDER':
            continue
        verdict = by_idx.get(row['idx'])
        if not verdict:
            unjudged += 1
            continue
        same = str(verdict.get('judgment', '')).lower().startswith('same')
        judged_same += same
        judged_diff += not same
        if not same:
            disagreements.append({
                'idx': row['idx'],
                'key': row['key'],
                'relation_verbatim': row['relation_verbatim'],
                'arm1_relation': row['arm1_relation'],
                'arm2_relation': row['arm2_relation'],
                'reason': verdict.get('reason'),
            })

    total = len(rows)
    mechanical_hits = counts.get('EXACT', 0) + counts.get('INFLECTION', 0)
    return {
        'items_compared': total,
        'verb_agreement_counts': dict(counts),
        'mechanical_verb_agreement': rate(mechanical_hits, total),
        'remainder_judged_same': judged_same,
        'remainder_judged_different': judged_diff,
        'remainder_unjudged': unjudged,
        'same_relation_rate': rate(mechanical_hits + judged_same, total),
        'qualifier_presence_counts': mechanical['summary']['qualifier_presence_counts'],
        'dropped_material_coverage_mean':
            mechanical['summary']['dropped_material_coverage_mean'],
        'arm2_verdicts': mechanical['summary']['arm2_verdicts'],
    }, disagreements


def score_c2(truth, verdicts):
    by_n = {v['n']: v for v in verdicts}
    per_class, misses = {}, []
    clean_total = clean_pass = 0
    clean_false_flags = []

    for row in truth['truth']:
        verdict = by_n.get(row['n'])
        cls = row['corruption']
        if cls == 'clean':
            clean_total += 1
            if verdict is None:
                continue
            entailed = str(verdict.get('entailed', '')).lower() == 'yes'
            clean_pass += entailed
            if not entailed:
                clean_false_flags.append({
                    'n': row['n'], 'idx': row['idx'], 'key': row['key'],
                    'element': verdict.get('element'), 'reason': verdict.get('reason')})
            continue

        bucket = per_class.setdefault(
            cls, {'planted': 0, 'caught': 0, 'flagged_wrong_element': 0, 'missed': 0})
        bucket['planted'] += 1
        if verdict is None:
            bucket['missed'] += 1
            misses.append({'n': row['n'], 'idx': row['idx'], 'key': row['key'],
                           'corruption': cls, 'outcome': 'no verdict'})
            continue
        flagged = str(verdict.get('entailed', '')).lower() != 'yes'
        element = str(verdict.get('element', '')).lower()
        if flagged and element == EXPECTED_ELEMENT[cls]:
            bucket['caught'] += 1
        elif flagged:
            bucket['flagged_wrong_element'] += 1
            misses.append({'n': row['n'], 'idx': row['idx'], 'key': row['key'],
                           'corruption': cls, 'outcome': f"flagged, named '{element}'",
                           'reason': verdict.get('reason')})
        else:
            bucket['missed'] += 1
            misses.append({'n': row['n'], 'idx': row['idx'], 'key': row['key'],
                           'corruption': cls, 'outcome': 'not flagged',
                           'reason': verdict.get('reason')})

    for cls, bucket in per_class.items():
        bucket['catch_rate'] = rate(bucket['caught'], bucket['planted'])

    planted = sum(b['planted'] for b in per_class.values())
    caught = sum(b['caught'] for b in per_class.values())
    return {
        'planted': planted,
        'caught': caught,
        'overall_catch_rate': rate(caught, planted),
        'flagged_wrong_element': sum(b['flagged_wrong_element'] for b in per_class.values()),
        'per_class': per_class,
        'clean_items': clean_total,
        'clean_judged_entailed': clean_pass,
        'specificity_on_clean': rate(clean_pass, clean_total),
    }, misses, clean_false_flags


def markdown(result, c1_disagreements, c2_misses, clean_false_flags):
    c1, c2 = result['C1'], result['C2']
    lines = [
        "# Study C — results",
        "",
        f"Run {result['run_date']}. Design: `DESIGN.md`, pre-registered 2026-08-28,",
        "unchanged since. One run, no redraws. No arm is ground truth in C1;",
        "disagreement is the finding.",
        "",
        "## C1 — the second normalization arm",
        "",
        f"- items compared: **{c1['items_compared']}**",
        f"- mechanical verb agreement: **{c1['mechanical_verb_agreement']}** "
        f"({c1['verb_agreement_counts'].get('EXACT', 0)} exact, "
        f"{c1['verb_agreement_counts'].get('INFLECTION', 0)} inflection)",
        f"- remainder judged same-relation: {c1['remainder_judged_same']}, "
        f"different: {c1['remainder_judged_different']}, "
        f"unjudged: {c1['remainder_unjudged']}",
        f"- same-relation rate overall: **{c1['same_relation_rate']}**",
        "",
        "Qualifier presence, by kind (count of items where the arm filled the key):",
        "",
        "| kind | arm 1 (stored) | arm 2 (Gemini) |",
        "|---|---|---|",
    ]
    presence = c1['qualifier_presence_counts']
    for kind in presence['arm1']:
        lines.append(f"| {kind} | {presence['arm1'][kind]} | {presence['arm2'][kind]} |")
    cov = c1['dropped_material_coverage_mean']
    lines += [
        "",
        f"Dropped-material coverage (token-overlap proxy, not a judgment): "
        f"arm 1 {cov['arm1'][0]} over {cov['arm1'][1]} items, "
        f"arm 2 {cov['arm2'][0]} over {cov['arm2'][1]}.",
        "",
        f"### Every same-relation disagreement ({len(c1_disagreements)})",
        "",
    ]
    if c1_disagreements:
        lines += ["| # | verbatim relation | arm 1 | arm 2 | reason |", "|---|---|---|---|---|"]
        for d in c1_disagreements:
            lines.append(f"| {d['idx']} | `{d['relation_verbatim']}` | "
                         f"`{d['arm1_relation']}` | `{d['arm2_relation']}` | "
                         f"{(d['reason'] or '').replace('|', '/')} |")
    else:
        lines.append("None.")

    lines += [
        "",
        "## C2 — seeded normalization corruptions",
        "",
        f"- planted: {c2['planted']}, caught (flagged **and** element named): "
        f"**{c2['caught']}** ({c2['overall_catch_rate']})",
        f"- flagged but the wrong element named: {c2['flagged_wrong_element']} "
        "— scored separately, never as catches (RULES #14)",
        f"- specificity on the {c2['clean_items']} clean items: "
        f"**{c2['specificity_on_clean']}** "
        f"({c2['clean_judged_entailed']} judged entailed)",
        "",
        "| class | planted | caught | flagged, wrong element | missed | catch rate |",
        "|---|---|---|---|---|---|",
    ]
    for cls, b in c2['per_class'].items():
        lines.append(f"| {cls} | {b['planted']} | {b['caught']} | "
                     f"{b['flagged_wrong_element']} | {b['missed']} | {b['catch_rate']} |")

    lines += ["", f"### Every corruption not caught ({len(c2_misses)})", ""]
    if c2_misses:
        lines += ["| # | class | outcome | reason |", "|---|---|---|---|"]
        for m in c2_misses:
            lines.append(f"| {m['idx']} | {m['corruption']} | {m['outcome']} | "
                         f"{(m.get('reason') or '').replace('|', '/')} |")
    else:
        lines.append("None.")

    lines += ["", f"### Clean items the gate flagged ({len(clean_false_flags)})", ""]
    if clean_false_flags:
        lines += ["| # | element named | reason |", "|---|---|---|"]
        for f in clean_false_flags:
            lines.append(f"| {f['idx']} | {f['element']} | "
                         f"{(f.get('reason') or '').replace('|', '/')} |")
    else:
        lines.append("None.")
    return "\n".join(lines) + "\n"


def main():
    mechanical = json.load(open(DOCS / 'c1_mechanical.json'))
    remainder = read_jsonl(DOCS / 'c1_remainder_verdicts.jsonl')
    c2_verdicts = read_jsonl(DOCS / 'c2_verdicts.jsonl')
    truth = json.load(open(WORK / 'c2_truth.json'))

    c1, c1_disagreements = score_c1(mechanical, remainder)
    c2, c2_misses, clean_false_flags = score_c2(truth, c2_verdicts)

    result = {
        'study': 'C — normalization validation',
        'design': 'docs/experiments/study_c/DESIGN.md (pre-registered 2026-08-28)',
        'run_date': '2026-08-30',
        'plant_seed': truth['plant_seed'],
        'C1': c1,
        'C2': c2,
    }
    json.dump(result, open(DOCS / 'RESULT.json', 'w'), indent=1, ensure_ascii=False)
    open(DOCS / 'RESULTS.md', 'w').write(
        markdown(result, c1_disagreements, c2_misses, clean_false_flags))
    print(json.dumps({'C1': c1, 'C2': c2}, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
