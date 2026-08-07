from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path
from typing import Any

from common import clamp, is_work_item, read_json, round_minutes, write_json

FEATURE_MULTIPLIERS = {
    "familiarity": {"familiar": 0.90, "partial": 1.05, "unfamiliar": 1.25},
    "clarity": {"clear": 0.95, "partial": 1.10, "unclear": 1.30},
    "validation": {"low": 0.95, "medium": 1.10, "high": 1.30},
    "ai_mode": {"none": 1.00, "assist": 0.90, "parallel": 0.85, "review_only": 0.70},
}
COVERAGE_Z = {0.70: 0.524, 0.85: 1.036, 0.90: 1.282}


def pert(o: float, m: float, p: float) -> float:
    if not (0 < o <= m <= p):
        raise ValueError("PERT requires 0 < optimistic <= most_likely <= pessimistic")
    return (o + 4 * m + p) / 6


def base_minutes(task: dict[str, Any]) -> float:
    if task.get("components"):
        total = 0.0
        for comp in task["components"]:
            if all(k in comp for k in ("optimistic", "most_likely", "pessimistic")):
                total += pert(float(comp["optimistic"]), float(comp["most_likely"]), float(comp["pessimistic"]))
            else:
                total += float(comp["minutes"])
        return total
    if all(k in task for k in ("optimistic", "most_likely", "pessimistic")):
        return pert(float(task["optimistic"]), float(task["most_likely"]), float(task["pessimistic"]))
    if task.get("base_minutes"):
        return float(task["base_minutes"])
    raise ValueError("provide base_minutes, PERT values, or components")


def feature_adjustment(task: dict[str, Any]) -> float:
    mult = 1.0
    for key, mapping in FEATURE_MULTIPLIERS.items():
        value = task.get(key)
        if value in mapping: mult *= mapping[value]
    # Output scale normally belongs in bottom-up components/Pert input. Apply a
    # generic scale multiplier only when the caller explicitly supplied a unit estimate.
    if task.get("base_is_unit_estimate"):
        scale = int(task.get("output_scale", 1))
        mult *= 1.0 + max(0, scale - 1) * 0.08
    switches = int(task.get("tool_switches", 0))
    mult *= 1.0 + min(switches, 5) * 0.04
    uncertainty = task.get("external_uncertainty", "low")
    mult *= {"low": 1.0, "medium": 1.08, "high": 1.20}.get(uncertainty, 1.0)
    return clamp(mult, 0.55, 2.5)


def similarity(task: dict[str, Any], sample: dict[str, Any]) -> float:
    if not sample.get("included", True): return 0.0
    score = 0.0
    weights = 0.0
    fields = {
        "category": 3.0, "mode": 2.0, "familiarity": 1.5, "clarity": 1.5,
        "validation": 1.0, "ai_mode": 1.0
    }
    for field, weight in fields.items():
        if field in task and field in sample:
            weights += weight
            score += weight if task[field] == sample[field] else 0.0
    if "output_scale" in task and "output_scale" in sample:
        weights += 1.0
        score += max(0.0, 1.0 - abs(float(task["output_scale"]) - float(sample["output_scale"])) / 4.0)
    return score / weights if weights else 0.0


def historical_correction(task: dict[str, Any], history: list[dict[str, Any]]) -> tuple[float, float, int, list[dict[str, Any]]]:
    candidates = []
    for sample in history:
        est = sample.get("estimated_minutes")
        actual = sample.get("calendar_minutes")
        sim = similarity(task, sample)
        if sim < 0.25 or not est or not actual or est <= 0 or actual <= 0: continue
        ratio_log = math.log(float(actual) / float(est))
        weight = sim ** 2
        candidates.append((weight, ratio_log, sample))
    candidates.sort(key=lambda x: x[0], reverse=True)
    candidates = candidates[:12]
    if not candidates: return 1.0, 0.45, 0, []
    sw = sum(w for w, _, _ in candidates)
    mean_log = sum(w * r for w, r, _ in candidates) / sw
    variance = sum(w * (r - mean_log) ** 2 for w, r, _ in candidates) / sw
    effective_n = sw
    shrink = effective_n / (effective_n + 4.0)
    shrunk_log = mean_log * shrink
    correction = math.exp(shrunk_log)
    sigma = max(0.18, math.sqrt(variance) if variance > 0 else 0.25)
    used = [{"task_id": s.get("task_id"), "similarity": round(w ** 0.5, 3), "ratio": round(math.exp(r), 3)} for w, r, s in candidates]
    return clamp(correction, 0.55, 2.2), sigma, len(candidates), used


def estimate(task: dict[str, Any], history: list[dict[str, Any]]) -> dict[str, Any]:
    if not is_work_item(task):
        raise ValueError("configuration and memory records must not be estimated")
    base = base_minutes(task)
    feature_mult = feature_adjustment(task)
    corrected_base = base * feature_mult
    hist_mult, sigma, n, used = historical_correction(task, history)
    median = corrected_base * hist_mult
    coverage = float(task.get("coverage", 0.70))
    z = COVERAGE_Z.get(coverage)
    if z is None:
        z = statistics.NormalDist().inv_cdf(coverage)
    uncertainty_penalty = 1.0
    if task.get("clarity") == "unclear": uncertainty_penalty *= 1.08
    if n == 0: uncertainty_penalty *= 1.10
    final = median * math.exp(z * sigma) * uncertainty_penalty
    rounded = round_minutes(final)
    confidence_score = 0
    confidence_score += 1 if task.get("clarity") == "clear" else 0
    confidence_score += 1 if task.get("familiarity") == "familiar" else 0
    confidence_score += 1 if n >= 3 else 0
    confidence = "high" if confidence_score >= 3 else "medium" if confidence_score >= 1 else "low"
    return {
        "base_minutes": round(base, 1),
        "feature_multiplier": round(feature_mult, 3),
        "history_multiplier": round(hist_mult, 3),
        "similar_samples": n,
        "target_coverage": coverage,
        "calendar_minutes": rounded,
        "confidence": confidence,
        "ai_parallel_minutes": task.get("ai_parallel_minutes"),
        "end_to_end_minutes": task.get("end_to_end_minutes"),
        "similar_sample_evidence": used,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, help="JSON file or -")
    ap.add_argument("--history", help="JSON list file")
    ap.add_argument("--output")
    args = ap.parse_args()
    task = read_json(args.task)
    history = read_json(args.history) if args.history else []
    write_json(estimate(task, history), args.output)

if __name__ == "__main__":
    main()
