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
from scheduling_engine import schedule
from conflict_merge import merge_task
from progress_engine import parent_progress, completion_gate
from rebuild_history import rebuild
from memory_policy import decide as memory_decide
from package_validator import validate as validate_package
from weekly_capacity import assess_capacity, stale_commitment_updates

ROOT = Path(__file__).resolve().parents[2]


class PlannerBlockTests(unittest.TestCase):
    def test_patch_preserves_natural(self):
        text = "背景。\n\n【Planner】\nschema: 1\nrole: task\nprogress: 0\ndate_semantics: none\nmobility: movable\nprivacy: normal\nestimate_confidence: low\ndependency_mode: all\ndependencies:\n【/Planner】\n"
        out = patch_body(text, {"progress": 50})
        natural, block = split_body(out)
        self.assertEqual(natural, "背景。")
        self.assertEqual(parse_block(block)["progress"], 50)
        self.assertEqual(validate(parse_block(block)), [])

    def test_dependency_parse(self):
        block = "schema: 1\nrole: task\nprogress: 0\ndate_semantics: none\nmobility: movable\nprivacy: normal\nestimate_confidence: low\ndependency_mode: all\ndependencies:\n  - type: finish_to_start\n    task_id: a\n    strength: hard"
        data = parse_block(block)
        self.assertEqual(data["dependencies"][0]["task_id"], "a")

    def test_external_wait_ref_valid(self):
        block = "schema: 1\nrole: task\nprogress: 0\ndate_semantics: none\nmobility: movable\nprivacy: normal\nestimate_confidence: low\ndependency_mode: all\ndependencies:\n  - type: external_wait\n    external_ref: reviewer_reply\n    strength: hard"
        self.assertEqual(validate(parse_block(block)), [])

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
        event = {"event": "completed", "calendar_minutes": 110, "included_in_estimation": True}
        parsed = parse_event(render_event(event))
        self.assertEqual(parsed["calendar_minutes"], 110)
        self.assertTrue(parsed["included_in_estimation"])


class EstimationTests(unittest.TestCase):
    def test_memory_not_estimable(self):
        with self.assertRaises(ValueError):
            estimate({"role":"memory","base_minutes":10}, [])

    def test_small_sample_shrinkage(self):
        task = {"base_minutes": 60, "category": "writing", "mode": "modify", "familiarity": "partial", "clarity": "clear", "validation": "medium", "ai_mode": "assist", "coverage": 0.70}
        history = [{"task_id": "x", "category": "writing", "mode": "modify", "estimated_minutes": 60, "calendar_minutes": 120, "included": True}]
        result = estimate(task, history)
        self.assertGreater(result["calendar_minutes"], 60)
        self.assertLess(result["history_multiplier"], 2.0)


class DependencyTests(unittest.TestCase):
    def test_cycle(self):
        self.assertFalse(cycle_check([{"source":"a","target":"b"},{"source":"b","target":"a"}])["acyclic"])

    def test_hard_dependency(self):
        task = {"id":"b","dependency_mode":"all","dependencies":[{"type":"finish_to_start","task_id":"a","strength":"hard"}]}
        result = evaluate(task, {"a":{"id":"a","completed":False}}, datetime.now().astimezone())
        self.assertFalse(result["ready"])


class SchedulerTests(unittest.TestCase):
    def test_memory_is_not_scheduled(self):
        data = {"date":"2026-08-06","utc_offset":"+08:00","availability":[{"start":"09:00","end":"12:00"}],"tasks":[{"id":"m","title":"Memory","role":"memory","duration_minutes":30,"mobility":"movable"}]}
        result = schedule(data)
        self.assertEqual(result["scheduled"], [])
        self.assertEqual(result["unscheduled"][0]["reason"], "non_work_record")

    def test_no_overlap(self):
        data = {"date":"2026-08-06","utc_offset":"+08:00","availability":[{"start":"09:00","end":"12:00"}],"fixed":[{"id":"f","start":"2026-08-06T10:00:00+08:00","end":"2026-08-06T10:30:00+08:00"}],"tasks":[{"id":"a","title":"A","duration_minutes":60,"mobility":"movable","dependencies_ready":True},{"id":"b","title":"B","duration_minutes":45,"mobility":"movable","dependencies_ready":True}],"buffer_minutes":10}
        result = schedule(data)
        self.assertEqual(result["overlaps"], [])


class WeeklyCapacityTests(unittest.TestCase):
    def test_committed_capacity_and_stale_roll(self):
        result = assess_capacity({
            "week_start": "2026-08-03",
            "weekly_capacity_minutes": 1000,
            "mainlines": [
                {"id": "must", "weekly_commitment": "must", "remaining_minutes": 300},
                {"id": "should", "weekly_commitment": "should", "estimated_minutes": 200},
                {"id": "candidate", "weekly_commitment": "candidate", "estimated_minutes": 400},
            ],
            "tasks": [
                {"id": "old", "title": "旧主线", "week_start": "2026-07-27", "weekly_commitment": "should"},
                {"id": "current", "week_start": "2026-08-03", "weekly_commitment": "must"},
            ],
        })
        self.assertEqual(result["reserved_minutes"], 350)
        self.assertEqual(result["usable_capacity_minutes"], 650)
        self.assertEqual(result["committed_minutes"], 500)
        self.assertEqual(result["candidate_minutes"], 400)
        self.assertTrue(result["fits"])
        self.assertEqual([x["id"] for x in result["stale_commitments"]], ["old"])
        self.assertEqual(result["stale_commitments"][0]["clear_patch"]["week_start"], "__DELETE__")

    def test_missing_estimate_dependency_and_deadline_risks(self):
        result = assess_capacity({
            "week_start": "2026-08-03",
            "weekly_capacity_minutes": 600,
            "reserve_ratio": 0.30,
            "mainlines": [{
                "id": "risk",
                "weekly_commitment": "must",
                "dependencies_ready": False,
                "date_semantics": "hard_deadline",
                "deadline": "2026-08-07",
            }],
        })
        self.assertFalse(result["fits"])
        self.assertEqual(result["missing_estimates"][0]["id"], "risk")
        self.assertEqual(result["dependency_risks"][0]["reason"], "dependency_not_ready")
        self.assertEqual(result["deadline_risks"][0]["reason"], "hard_deadline_this_week")

    def test_target_date_is_not_hard_deadline_risk(self):
        result = assess_capacity({
            "week_start": "2026-08-03",
            "weekly_capacity_minutes": 600,
            "mainlines": [{
                "id": "target",
                "weekly_commitment": "should",
                "estimated_minutes": 60,
                "date_semantics": "target_date",
                "deadline": "2026-08-07",
            }],
        })
        self.assertEqual(result["deadline_risks"], [])

    def test_invalid_count_zero_estimate_and_blocked_dependency_do_not_fit(self):
        result = assess_capacity({
            "week_start": "2026-08-03",
            "weekly_capacity_minutes": 600,
            "mainlines": [{
                "id": "blocked",
                "weekly_commitment": "must",
                "estimated_minutes": 0,
                "dependencies_ready": False,
            }],
        })
        self.assertFalse(result["selection_count_ok"])
        self.assertFalse(result["fits"])
        self.assertEqual(result["missing_estimates"][0]["id"], "blocked")
        self.assertTrue(result["dependency_risks"][0]["blocking"])

    def test_non_work_mainline_is_rejected(self):
        with self.assertRaises(ValueError):
            assess_capacity({
                "week_start": "2026-08-03",
                "weekly_capacity_minutes": 600,
                "mainlines": [
                    {"id": "memory", "role": "memory", "weekly_commitment": "must", "estimated_minutes": 60},
                    {"id": "task", "role": "task", "weekly_commitment": "should", "estimated_minutes": 60},
                ],
            })

    def test_malformed_current_pair_is_cleared_but_memory_is_ignored(self):
        updates = stale_commitment_updates([
            {"id": "missing-tier", "role": "task", "week_start": "2026-08-03"},
            {"id": "bad-tier", "role": "task", "week_start": "2026-08-03", "weekly_commitment": "urgent"},
            {"id": "memory", "role": "memory", "week_start": "2026-07-27", "weekly_commitment": "must"},
        ], "2026-08-03")
        self.assertEqual([item["id"] for item in updates], ["missing-tier", "bad-tier"])
        self.assertTrue(all(item["reason"] == "malformed_weekly_commitment" for item in updates))

    def test_future_hard_deadline_needs_capacity_evidence(self):
        result = assess_capacity({
            "week_start": "2026-08-03",
            "weekly_capacity_minutes": 600,
            "mainlines": [
                {"id": "deadline", "weekly_commitment": "must", "estimated_minutes": 300,
                 "date_semantics": "hard_deadline", "deadline": "2026-08-14"},
                {"id": "other", "weekly_commitment": "should", "estimated_minutes": 60},
            ],
        })
        self.assertFalse(result["fits"])
        self.assertEqual(result["deadline_risks"][0]["reason"], "deadline_capacity_unknown")

    def test_five_mainlines_do_not_form_a_valid_plan(self):
        result = assess_capacity({
            "week_start": "2026-08-03",
            "weekly_capacity_minutes": 1000,
            "mainlines": [
                {"id": str(index), "weekly_commitment": "candidate", "estimated_minutes": 30}
                for index in range(5)
            ],
        })
        self.assertFalse(result["selection_count_ok"])
        self.assertFalse(result["fits"])


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
        comment=render_event({"event":"completed","operation_id":"op1","prior_estimate_minutes":90,"calendar_minutes":110,"included_in_estimation":True,"category":"writing"})
        result=rebuild([{"id":"t1","comments":[{"id":"c1","title":comment}]}])
        self.assertEqual(len(result["samples"]),1)
        self.assertEqual(result["samples"][0]["calendar_minutes"],110)


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
