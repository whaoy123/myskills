from pathlib import Path
from copy import deepcopy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'dida-planning-core/scripts'))
from weekly_delivery import evaluate_plan
from test_weekly_delivery import task, plan

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

class ReleaseTests(unittest.TestCase):
    def test_calendar_components_absent(self):
        for rel in ['dida-daily-planner','dida-planning-core/scripts/scheduling_engine.py','dida-planning-core/scripts/weekly_capacity.py']:
            self.assertFalse((ROOT/rel).exists(),rel)
    def test_active_skills_have_no_old_route(self):
        for p in ROOT.glob('dida-*/SKILL.md'):
            self.assertNotIn('dida-daily-planner',p.read_text(),str(p))
    def test_new_templates_do_not_emit_legacy_scheduling_metadata(self):
        roots=[ROOT/'dida-planning-profile/assets/config-notes', ROOT/'dida-planning-memory/assets/memory-categories']
        for folder in roots:
            for path in folder.glob('*.md'):
                text=path.read_text(encoding='utf-8')
                self.assertNotIn('mobility:', text, str(path))
                self.assertNotIn('date_semantics: execution_window', text, str(path))
        capture=(ROOT/'dida-task-capture/references/capture-protocol.md').read_text(encoding='utf-8')
        self.assertNotIn('`execution_window` on an executable task', capture)

    def test_user_context_does_not_route_calendar_capacity_to_dida_profile(self):
        schema=ROOT.parent/'user-context-profile/schemas/user-context.schema.yaml'
        if schema.exists():
            text=schema.read_text(encoding='utf-8')
            profile=text.split('dida_planning_profile:',1)[1].split('dida_planning_memory:',1)[0]
            for forbidden in ['schedule','energy','mobility','timezone','planning_capacity']:
                self.assertNotIn('- '+forbidden, profile)

    def test_research_handoff_routes(self):
        for rel in ['engineering-prestudy/SKILL.md','engineering-prestudy/references/dida-handoff-contract.md','research-design-planning/SKILL.md']:
            p=ROOT.parent/rel
            if p.exists():self.assertNotIn('dida-daily-planner',p.read_text())
    def test_bad_role_snapshot_reports_error(self):
        t=task(role=[]);self.assertFalse(evaluate_plan(plan([t]))['validation_passed'])
    def test_legacy_candidate_does_not_block_selected_work(self):
        t=task('candidate',999,weekly_commitment='candidate');t.pop('weekly_delivery')
        r=evaluate_plan(plan([task(),t]));self.assertEqual(r['feasibility'],'feasible')
    def test_no_asof_does_not_claim_current_overdue(self):
        t=task(date_semantics='hard_deadline',due_date='2026-09-20')
        r=evaluate_plan(plan([t]));self.assertNotIn('hard_deadline_overdue',[v['risk'] for v in r['risks']])
    def test_calendar_legacy_not_reinitialized(self):
        mod=load_module('legacy_classifier',ROOT/'dida-planning-core/scripts/migration/classify_legacy_memory.py')
        r=mod.classify_item({'text':'旧日程作息模板','section':'偏好'})
        self.assertEqual(r['decision'],'review');self.assertNotIn('owner',r)
    def test_installer_dry_run_does_not_write(self):
        mod=load_module('dida_installer_dry',ROOT/'install.py')
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/'skills'
            result=mod.install(target,dry_run=True)
            self.assertFalse(target.exists());self.assertIn('dida-weekly-delivery',result['install'])
    def test_installer_backups_old_skills_and_retires_scheduler(self):
        mod=load_module('dida_installer_live',ROOT/'install.py')
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/'skills';old=target/'dida-daily-planner';old.mkdir(parents=True)
            (old/'custom.txt').write_text('keep this user customization')
            unrelated=target/'unrelated';unrelated.mkdir();(unrelated/'keep.txt').write_text('unchanged')
            result=mod.install(target)
            backup=Path(result['backup'])
            self.assertFalse(old.exists());self.assertTrue((target/'dida-weekly-delivery/SKILL.md').exists())
            self.assertEqual((backup/'dida-daily-planner/custom.txt').read_text(),'keep this user customization')
            self.assertEqual((unrelated/'keep.txt').read_text(),'unchanged')
            self.assertFalse(str(backup).startswith(str(target)+str(Path('/'))))
    def test_installer_refuses_source_as_destination(self):
        mod=load_module('dida_installer_guard',ROOT/'install.py')
        with self.assertRaises(ValueError):mod.install(ROOT,dry_run=True)
    def test_bash_wrapper_dry_run(self):
        if sys.platform=='win32':self.skipTest('Bash wrapper test runs on Unix')
        with tempfile.TemporaryDirectory() as td:
            result=subprocess.run(['bash',str(ROOT/'install.sh'),str(Path(td)/'skills'),'--dry-run'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr);self.assertTrue(json.loads(result.stdout)['dry_run'])

if __name__=='__main__':unittest.main()
