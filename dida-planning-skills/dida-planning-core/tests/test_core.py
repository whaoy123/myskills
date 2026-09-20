from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from planner_block import parse_block, patch_body, split_body, validate
from planner_event import parse_event, render_event
from estimation_engine import estimate
from dependency_engine import cycle_check, evaluate
from conflict_merge import merge_task
from progress_engine import parent_progress, completion_gate
from rebuild_history import rebuild
from memory_policy import decide as memory_decide
from package_validator import validate as validate_package

ROOT = Path(__file__).resolve().parents[2]


class PlannerBlockTests(unittest.TestCase):
    def test_patch_preserves_natural(self):
        text = "背景。\n\n【Planner】\nschema: 1\nrole: task\nprogress: 0\ndate_semantics: none\nprivacy: normal\nestimate_confidence: low\ndependency_mode: all\ndependencies:\n【/Planner】\n"
        out = patch_body(text, {"progress": 50})
        natural, block = split_body(out)
        self.assertEqual(natural, "背景。")
        self.assertEqual(parse_block(block)["progress"], 50)
        self.assertEqual(validate(parse_block(block)), [])

    def test_dependency_parse(self):
        block = "schema: 1\nrole: task\nprogress: 0\ndate_semantics: none\nprivacy: normal\nestimate_confidence: low\ndependency_mode: all\ndependencies:\n  - type: finish_to_start\n    task_id: a\n    strength: hard"
        data = parse_block(block)
        self.assertEqual(data["dependencies"][0]["task_id"], "a")

    def test_external_wait_ref_valid(self):
        block = "schema: 1\nrole: task\nprogress: 0\ndate_semantics: none\nprivacy: normal\nestimate_confidence: low\ndependency_mode: all\ndependencies:\n  - type: external_wait\n    external_ref: reviewer_reply\n    strength: hard"
        self.assertEqual(validate(parse_block(block)), [])

    def test_new_block_omits_scheduling_fields(self):
        out = patch_body("背景。", {"progress": 25})
        data = parse_block(split_body(out)[1])
        self.assertNotIn("mobility", data)
        self.assertNotEqual(data.get("date_semantics"), "execution_window")
        self.assertNotEqual(data.get("role"), "block")

    def test_new_writes_reject_legacy_scheduling_fields(self):
        with self.assertRaises(ValueError):
            patch_body("", {"mobility": "movable"})
        with self.assertRaises(ValueError):
            patch_body("", {"date_semantics": "execution_window"})
        with self.assertRaises(ValueError):
            patch_body("", {"role": "block"})

    def test_legacy_scheduling_fields_remain_readable_and_preserved(self):
        text = "背景。\n\n【Planner】\nschema: 1\nrole: task\nprogress: 0\ndate_semantics: execution_window\nmobility: movable\nprivacy: normal\nestimate_confidence: low\ndependency_mode: all\ndependencies:\n【/Planner】\n"
        out = patch_body(text, {"progress": 50})
        data = parse_block(split_body(out)[1])
        self.assertEqual(data["date_semantics"], "execution_window")
        self.assertEqual(data["mobility"], "movable")
        self.assertEqual(data["progress"], 50)

    def test_weekly_commitment_round_trip(self):
        out = patch_body("背景。", {"week_start": "2026-08-03", "weekly_commitment": "must"})
        _, block = split_body(out)
        data = parse_block(block)
        self.assertEqual(data["week_start"], "2026-08-03")
        self.assertEqual(data["weekly_commitment"], "must")
        self.assertEqual(validate(data), [])

    def test_weekly_commitment_is_a_pair(self):
        with self.assertRaises(ValueError):
            patch_body("背景。", {"week_start": "2026-08-03"})

    def test_weekly_commitment_requires_work_role_and_monday(self):
        with self.assertRaises(ValueError):
            patch_body("背景。", {"role": "memory", "week_start": "2026-08-03", "weekly_commitment": "must"})
        with self.assertRaises(ValueError):
            patch_body("背景。", {"week_start": "2026-08-04", "weekly_commitment": "must"})


class EventTests(unittest.TestCase):
    def test_round_trip(self):
        event = {"event": "completed", "actual_effort_minutes": 110, "included_in_estimation": True}
        parsed = parse_event(render_event(event))
        self.assertEqual(parsed["actual_effort_minutes"], 110)
        self.assertTrue(parsed["included_in_estimation"])

    def test_legacy_calendar_minutes_parse_but_not_write(self):
        legacy = "[planner-event:v1]\nevent: completed\ncalendar_minutes: 110\nincluded_in_estimation: true"
        self.assertEqual(parse_event(legacy)["calendar_minutes"], 110)
        with self.assertRaises(ValueError):
            render_event({"event": "completed", "calendar_minutes": 110})


class EstimationTests(unittest.TestCase):
    def test_memory_not_estimable(self):
        with self.assertRaises(ValueError):
            estimate({"role":"memory","base_minutes":10}, [])

    def test_small_sample_shrinkage(self):
        task = {"base_minutes": 60, "category": "writing", "mode": "modify", "familiarity": "partial", "clarity": "clear", "validation": "medium", "ai_mode": "assist", "coverage": 0.70}
        history = [{"task_id": "x", "category": "writing", "mode": "modify", "estimated_minutes": 60, "actual_effort_minutes": 120, "included": True}]
        result = estimate(task, history)
        self.assertGreater(result["estimated_effort_minutes"], 60)
        self.assertLess(result["history_multiplier"], 2.0)
        self.assertNotIn("calendar_minutes", result)

    def test_legacy_history_calendar_minutes_is_read_compatibility(self):
        task = {"base_minutes": 60, "category": "writing", "mode": "modify", "clarity": "clear", "coverage": 0.70}
        history = [{"task_id": "legacy", "category": "writing", "mode": "modify", "estimated_minutes": 60, "calendar_minutes": 120, "included": True}]
        result = estimate(task, history)
        self.assertGreater(result["estimated_effort_minutes"], 60)


class DependencyTests(unittest.TestCase):
    def test_cycle(self):
        self.assertFalse(cycle_check([{"source":"a","target":"b"},{"source":"b","target":"a"}])["acyclic"])

    def test_hard_dependency(self):
        task = {"id":"b","dependency_mode":"all","dependencies":[{"type":"finish_to_start","task_id":"a","strength":"hard"}]}
        result = evaluate(task, {"a":{"id":"a","completed":False}}, datetime.now().astimezone())
        self.assertFalse(result["ready"])


class PackageValidatorTests(unittest.TestCase):
    def test_package_and_manifest_are_current(self):
        if not (ROOT / "MANIFEST.sha256").exists():
            self.skipTest("repository manifest is not part of an installed core copy")
        errors, _ = validate_package(ROOT)
        self.assertEqual(errors, [])


class MergeTests(unittest.TestCase):
    def test_different_fields_merge(self):
        base = {"title":"A","priority":0,"tags":[],"content":"x"}
        latest = {"title":"A","priority":3,"tags":[],"content":"x"}
        proposed = {"title":"B","priority":0,"tags":[],"content":"x"}
        result = merge_task(base, latest, proposed)
        self.assertTrue(result["safe_to_write"])
        self.assertEqual(result["merged"]["title"], "B")
        self.assertEqual(result["merged"]["priority"], 3)

    def test_same_field_conflict(self):
        base = {"title":"A","tags":[],"content":"x"}
        latest = {"title":"U","tags":[],"content":"x"}
        proposed = {"title":"AI","tags":[],"content":"x"}
        self.assertIn("title", merge_task(base, latest, proposed)["conflicts"])


class ProgressTests(unittest.TestCase):
    def test_memory_child_does_not_block_or_reduce_progress(self):
        children=[{"id":"work","role":"task","completed":True,"progress":100,"estimated_minutes":60,"required_for_parent":True},{"id":"mem","role":"memory","completed":False,"progress":0,"required_for_parent":False}]
        self.assertTrue(completion_gate(children)["can_complete_without_question"])
        self.assertEqual(parent_progress(children)["progress"],100)

    def test_optional_child_does_not_block(self):
        children=[{"id":"a","completed":True,"progress":100,"estimated_minutes":60,"required_for_parent":True},{"id":"b","completed":False,"progress":0,"estimated_minutes":30,"required_for_parent":False}]
        self.assertTrue(completion_gate(children)["ask_about_optional"])
        self.assertEqual(parent_progress(children)["progress"],100)


class HistoryTests(unittest.TestCase):
    def test_rebuild_from_comment(self):
        comment=render_event({"event":"completed","operation_id":"op1","prior_estimate_minutes":90,"actual_effort_minutes":110,"included_in_estimation":True,"category":"writing"})
        result=rebuild([{"id":"t1","comments":[{"id":"c1","title":comment}]}])
        self.assertEqual(len(result["samples"]),1)
        self.assertEqual(result["samples"][0]["actual_effort_minutes"],110)
        self.assertEqual(result["samples"][0]["actual_effort_source"],"actual_effort_minutes")

    def test_rebuild_legacy_calendar_minutes_comment(self):
        comment="[planner-event:v1]\nevent: completed\noperation_id: old1\nprior_estimate_minutes: 90\ncalendar_minutes: 110\nincluded_in_estimation: true\ncategory: writing"
        result=rebuild([{"id":"t1","comments":[{"id":"c1","title":comment}]}])
        self.assertEqual(result["samples"][0]["actual_effort_minutes"],110)
        self.assertEqual(result["samples"][0]["actual_effort_source"],"legacy_calendar_minutes")


class MemoryPolicyTests(unittest.TestCase):
    def test_explicit_sensitive_save_is_minimized(self):
        result = memory_decide({"owner":"memory","explicit_save":True,"sensitive":True})
        self.assertEqual(result["decision"], "save")
        self.assertTrue(result["minimize"])

    def test_stable_useful_fact_auto_saves(self):
        result = memory_decide({"owner":"memory","stable":True,"future_useful":True,"directly_stated":True})
        self.assertEqual(result["decision"], "save")

    def test_inferred_pattern_asks(self):
        result = memory_decide({"owner":"memory","stable":True,"future_useful":True,"inferred":True})
        self.assertEqual(result["decision"], "ask")

    def test_missing_direct_statement_does_not_auto_save(self):
        result = memory_decide({"owner":"memory","stable":True,"future_useful":True})
        self.assertEqual(result["decision"], "skip")

    def test_preference_routes_to_profile(self):
        result = memory_decide({"owner":"profile","stable":True,"future_useful":True})
        self.assertEqual(result["decision"], "route")
        self.assertEqual(result["owner"], "profile")

    def test_transform_text_skips(self):
        result = memory_decide({"owner":"memory","from_transform":True,"stable":True,"future_useful":True})
        self.assertEqual(result["decision"], "skip")


if __name__ == "__main__":
    unittest.main()
