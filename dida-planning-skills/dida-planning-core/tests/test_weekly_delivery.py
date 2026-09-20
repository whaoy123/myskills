from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'dida-planning-core' / 'scripts'))
from weekly_delivery import assess_acceptance, evaluate_plan, prepare_week_rollover, validate_contract
from planner_block import parse_block, patch_body, split_body, validate

WEEK = '2026-09-21'

def contract(slot='work', refs=None):
    return {'schema':1, 'slot':slot, 'outcome':'交付接口核对表', 'artifact':'接口约束核对表',
            'scope':'一个模块的一轮核对', 'criteria':['关键约束已记录','未决问题有归属'],
            'verification':'读取表并确认', 'support_task_ids':refs or [],
            'exclusions':['不画整板原理图'], 'target_date':'2026-09-27',
            'status':'planned', 'evidence':[]}

def task(tid='owner', minutes=120, slot='work', **kwargs):
    result = {'id':tid, 'role':'task', 'completed':False, 'remaining_minutes':minutes,
              'blocked':False, 'week_start':WEEK, 'weekly_commitment':'must',
              'weekly_delivery':contract(slot)}
    result.update(kwargs)
    return result

def plan(tasks=None, **kwargs):
    result={'week_start':WEEK,'inventory_complete':True,'tasks':tasks if tasks is not None else [task()],
            'effort_budget_minutes':240,'obligation_task_ids':[]}
    result.update(kwargs)
    return result

class ContractTests(unittest.TestCase):
    def test_valid_contract(self):
        self.assertEqual(validate_contract(contract(),WEEK),[])
    def test_fields_required(self):
        for key in ['outcome','artifact','scope','criteria','verification','support_task_ids','exclusions','target_date','status','evidence']:
            with self.subTest(key=key):
                c=contract();c.pop(key);self.assertTrue(validate_contract(c,WEEK))
    def test_empty_criteria_not_deliverable(self):
        c=contract();c['criteria']=[];self.assertTrue(validate_contract(c,WEEK))
    def test_future_extension_preserved(self):
        c=contract();c['future']={'method':'review','weight':0.5};self.assertEqual(validate_contract(c,WEEK),[])
    def test_wrong_week_or_non_monday(self):
        c=contract();c['target_date']='2026-09-28';self.assertTrue(validate_contract(c,WEEK))
        self.assertTrue(validate_contract(contract(),'2026-09-22'))
    def test_invalid_target_date(self):
        c=contract();c['target_date']='2026-02-30';self.assertTrue(validate_contract(c,WEEK))
    def test_duplicate_support_rejected(self):
        self.assertTrue(validate_contract(contract(refs=['same','same']),WEEK))
    def test_malformed_status_slot_and_schema(self):
        for key,value in [('status',[]),('slot',{}),('schema',True),('schema',2)]:
            c=contract();c[key]=value;self.assertTrue(validate_contract(c,WEEK))
    def test_delivered_requires_evidence(self):
        c=contract();c['status']='delivered';self.assertTrue(validate_contract(c,WEEK))
    def test_bad_evidence_kind(self):
        c=contract();c['evidence']=[{'kind':'guessed','detail':'probably done'}];self.assertTrue(validate_contract(c,WEEK))

class PlannerCompatibilityTests(unittest.TestCase):
    def test_legacy_week_pair_roundtrip(self):
        txt=patch_body('旧任务正文',{'week_start':WEEK,'weekly_commitment':'should'})
        d=parse_block(split_body(txt)[1]);self.assertEqual(validate(d),[]);self.assertNotIn('weekly_delivery',d)
    def test_new_json_and_unknown_fields_roundtrip(self):
        c=contract();c['extension']={'future':['中文','line\nsecond'], 'bool':True}
        text=patch_body('保留原始背景',{'week_start':WEEK,'weekly_commitment':'must','weekly_delivery':c,'future_scalar':{'a':3}})
        text=patch_body(text,{'progress':25})
        natural, block=split_body(text);data=parse_block(block)
        self.assertEqual(natural,'保留原始背景');self.assertEqual(data['weekly_delivery'],c)
        self.assertEqual(data['future_scalar'],{'a':3})
    def test_string_types_survive(self):
        for value in ['true','null','123','0.5','[1,2]','{"x":1}','line\nsecond','  spaces  ','#hash','']:
            with self.subTest(value=value):
                text=patch_body('',{'custom':value});self.assertEqual(parse_block(split_body(text)[1])['custom'],value)
    def test_unknown_float_roundtrip(self):
        text=patch_body('',{'weight':0.5});self.assertEqual(parse_block(split_body(text)[1])['weight'],0.5)
    def test_invalid_contract_does_not_patch(self):
        original='original';c=contract();c['criteria']=[]
        with self.assertRaises(ValueError):patch_body(original,{'week_start':WEEK,'weekly_commitment':'must','weekly_delivery':c})
        self.assertEqual(original,'original')
    def test_config_and_block_contract_rejected(self):
        for role in ['config','memory','project','block']:
            self.assertTrue(validate({'role':role,'week_start':WEEK,'weekly_commitment':'must','weekly_delivery':contract()}))
    def test_invalid_role_handled(self):
        self.assertTrue(validate({'role':[], 'week_start':WEEK,'weekly_commitment':'must','weekly_delivery':contract()}))
    def test_bad_dependencies_handled(self):
        self.assertTrue(validate({'dependencies':[{'type':[],'strength':[]}]}))
    def test_no_nonfinite_scalar(self):
        with self.assertRaises(ValueError):patch_body('',{'cost':float('nan')})

class SelectionTests(unittest.TestCase):
    def test_one_commitment_is_valid_not_forced_to_two(self):
        r=evaluate_plan(plan());self.assertEqual(r['core_count'],1);self.assertEqual(r['feasibility'],'feasible')
    def test_zero_commitments_valid(self):
        self.assertEqual(evaluate_plan(plan([]))['feasibility'],'feasible')
    def test_no_growth_requires_explicit_deferral_metadata(self):
        r=evaluate_plan(plan())
        self.assertFalse(r["growth_tradeoff"]["has_growth"])
        self.assertTrue(any("growth_deferral_reason" in w for w in r["warnings"]))
        self.assertTrue(any("growth_resume_condition" in w for w in r["warnings"]))

    def test_busy_week_can_defer_growth_with_reason_and_resume_condition(self):
        r=evaluate_plan(plan(growth_deferral_reason="本周需求冻结存在外部确认节点",
                             growth_resume_condition="需求冻结完成后下周重新选择一个小型 IC 交付物"))
        self.assertFalse(r["growth_tradeoff"]["has_growth"])
        self.assertFalse(any("growth_deferral" in w or "growth_resume" in w for w in r["warnings"]))

    def test_two_slots_fit(self):
        r=evaluate_plan(plan([task(),task('growth',90,'growth')]));self.assertEqual(r['core_count'],2)
        self.assertEqual(r['known_remaining_minutes'],210);self.assertEqual(r['feasibility'],'feasible')
    def test_three_core_rejected(self):
        r=evaluate_plan(plan([task('first'),task('second'),task('third')],effort_budget_minutes=600))
        self.assertFalse(r['validation_passed']);self.assertTrue(any('core_commitment_limit' in e for e in r['errors']))
    def test_cap_override_needs_reason(self):
        r=evaluate_plan(plan([task('first'),task('second'),task('third')],core_limit=3,effort_budget_minutes=600))
        self.assertFalse(r['validation_passed'])
        r=evaluate_plan(plan([task('first'),task('second'),task('third')],core_limit=3,override_reason='User explicitly approved a one-week exception',effort_budget_minutes=600))
        self.assertTrue(r['validation_passed'])
    def test_candidate_not_committed_or_counted(self):
        c=task('candidate',999,weekly_commitment='candidate')
        r=evaluate_plan(plan([task(),c]));self.assertEqual(r['core_count'],1);self.assertEqual(r['known_remaining_minutes'],120)
    def test_obligation_is_not_free(self):
        o={'id':'trip','role':'task','completed':False,'remaining_minutes':240,'blocked':False}
        r=evaluate_plan(plan([task(),o],obligation_task_ids=['trip']))
        self.assertEqual(r['known_remaining_minutes'],360);self.assertEqual(r['feasibility'],'blocked')
    def test_shared_work_deduplicated(self):
        a=task('board-a',role='phase',weekly_delivery=contract(refs=['shared']))
        b=task('board-b',role='phase',weekly_delivery=contract(refs=['shared']))
        s={'id':'shared','role':'task','completed':False,'remaining_minutes':180,'blocked':False}
        r=evaluate_plan(plan([a,b,s],obligation_task_ids=['shared']))
        self.assertEqual(r['known_remaining_minutes'],180);self.assertEqual(r['shared_task_ids'],['shared'])
    def test_two_independent_boards_costs_add(self):
        r=evaluate_plan(plan([task('board-a',180),task('board-b',180)],effort_budget_minutes=300))
        self.assertEqual(r['known_remaining_minutes'],360);self.assertEqual(r['feasibility'],'blocked')
    def test_parent_rollup_not_leaf(self):
        owner=task();child={'id':'child','parent_id':'owner','role':'task','completed':False,'remaining_minutes':30,'blocked':False}
        r=evaluate_plan(plan([owner,child]));self.assertTrue(any('unfinished children' in e for e in r['errors']))
    def test_phase_requires_leaves(self):
        r=evaluate_plan(plan([task(role='phase')]));self.assertFalse(r['validation_passed'])
    def test_missing_reference(self):
        r=evaluate_plan(plan([task(weekly_delivery=contract(refs=['missing']))]));self.assertFalse(r['validation_passed'])
    def test_config_not_leaf(self):
        cfg={'id':'cfg','role':'config','completed':False}
        r=evaluate_plan(plan([task(weekly_delivery=contract(refs=['cfg'])),cfg]));self.assertFalse(r['validation_passed'])
    def test_self_reference_rejected(self):
        r=evaluate_plan(plan([task(weekly_delivery=contract(refs=['owner']))]));self.assertFalse(r['validation_passed'])
    def test_missing_estimate_is_unknown_not_zero(self):
        r=evaluate_plan(plan([task(minutes=None)]));self.assertEqual(r['feasibility'],'unknown')
    def test_missing_budget_is_unknown(self):
        r=evaluate_plan(plan(effort_budget_minutes=None));self.assertEqual(r['feasibility'],'unknown')
    def test_missing_dependency_scan_is_unknown(self):
        t=task();t.pop('blocked');self.assertEqual(evaluate_plan(plan([t]))['feasibility'],'unknown')
    def test_blocked_contract_and_task(self):
        t=task();t['weekly_delivery']['status']='blocked'
        self.assertEqual(evaluate_plan(plan([t]))['feasibility'],'blocked')
        self.assertEqual(evaluate_plan(plan([task(blocked=True)]))['feasibility'],'blocked')
    def test_incomplete_inventory_not_safe(self):
        self.assertEqual(evaluate_plan(plan(inventory_complete=False))['feasibility'],'unknown')
    def test_legacy_commitment_needs_definition(self):
        t=task();t.pop('weekly_delivery');r=evaluate_plan(plan([t]))
        self.assertEqual(r['core_count'],1);self.assertEqual(r['feasibility'],'unknown')
    def test_stale_and_future_not_active(self):
        old=task('old',week_start='2026-09-14');future=task('future',week_start='2026-09-28')
        r=evaluate_plan(plan([old,future]));self.assertEqual(r['core_count'],0);self.assertEqual(r['stale_owner_ids'],['old'])
    def test_invalid_and_duplicate_ids(self):
        r=evaluate_plan(plan([task(),task()]));self.assertFalse(r['validation_passed'])
    def test_zero_unfinished_effort_needs_confirmation(self):
        self.assertEqual(evaluate_plan(plan([task(minutes=0)]))['feasibility'],'unknown')
    def test_nonfinite_effort_rejected(self):
        for minutes in [float('nan'),float('inf'),-1,True,'120']:
            self.assertFalse(evaluate_plan(plan([task(minutes=minutes)]))['validation_passed'])
    def test_invalid_budget_rejected(self):
        for budget in [-1,True,'120',float('nan')]:
            with self.assertRaises(ValueError):evaluate_plan(plan(effort_budget_minutes=budget))
    def test_completed_effort_not_counted(self):
        t=task(completed=True);self.assertEqual(evaluate_plan(plan([t]))['known_remaining_minutes'],0)
    def test_delivered_slice_does_not_charge_whole_remaining_parent(self):
        t=task(minutes=999);t['weekly_delivery'].update(status='delivered',evidence=[{'kind':'user_report','detail':'本周约定已验收'}])
        r=evaluate_plan(plan([t]));self.assertEqual(r['known_remaining_minutes'],0)
        self.assertFalse(t['completed'])
    def test_inputs_are_not_mutated(self):
        data=plan();before=deepcopy(data);r=evaluate_plan(data)
        self.assertEqual(data,before);self.assertEqual(r['remote_mutations'],[])

class RiskTests(unittest.TestCase):
    def test_target_does_not_become_hard_deadline(self):
        r=evaluate_plan(plan([task(date_semantics='target_date',due_date='2026-09-22')]))
        self.assertEqual(r['risks'],[])
    def test_deadline_without_elapsed_basis_stays_unknown(self):
        t=task(date_semantics='hard_deadline',due_date='2026-10-31',latest_safe_start='2026-09-25')
        r=evaluate_plan(plan([t]));self.assertEqual(r['feasibility'],'unknown')
    def test_late_start_and_far_deadline_detected(self):
        t=task(date_semantics='hard_deadline',due_date='2026-10-31',latest_safe_start='2026-09-25',latest_start_basis='User confirmed elapsed-duration chain and buffer')
        r=evaluate_plan(plan([t]));self.assertIn('must_start_by_week_end',[x['risk'] for x in r['risks']])
    def test_unselected_urgent_risk_needs_decision(self):
        t={'id':'unselected','role':'task','completed':False,'date_semantics':'hard_deadline','due_date':'2026-09-22','latest_safe_start':'2026-09-21','latest_start_basis':'Confirmed one-day lead time'}
        self.assertEqual(evaluate_plan(plan([task(),t]))['feasibility'],'unknown')
    def test_start_after_deadline_invalid(self):
        t=task(date_semantics='hard_deadline',due_date='2026-09-23',latest_safe_start='2026-09-25',latest_start_basis='bad basis')
        self.assertFalse(evaluate_plan(plan([t]))['validation_passed'])
    def test_explicit_as_of_for_overdue(self):
        t=task(date_semantics='hard_deadline',due_date='2026-09-22')
        r=evaluate_plan(plan([t],as_of='2026-09-23'));self.assertIn('hard_deadline_overdue',[x['risk'] for x in r['risks']])

class AcceptanceTests(unittest.TestCase):
    def test_partial_is_not_delivered(self):
        r=assess_acceptance(contract(),week_start=WEEK,criterion_results=[True,False])
        self.assertEqual(r['status'],'not_delivered')
    def test_no_evidence_is_unverified(self):
        self.assertEqual(assess_acceptance(contract(),week_start=WEEK,criterion_results=[True,True])['status'],'unverified')
    def test_user_attestation_accepted_with_source(self):
        evidence=[{'kind':'user_report','detail':'两项验收条件都完成了'}]
        r=assess_acceptance(contract(),week_start=WEEK,user_attested=True,evidence=evidence)
        self.assertEqual(r['status'],'delivered');self.assertFalse(r['native_owner_completion'])
        self.assertEqual(r['evidence'][0]['kind'],'user_report')
    def test_hours_worked_does_not_accept(self):
        r=assess_acceptance(contract(),week_start=WEEK,evidence=[{'kind':'user_report','detail':'做了三小时'}])
        self.assertEqual(r['status'],'unverified')
    def test_all_checked_with_observed_evidence(self):
        r=assess_acceptance(contract(),week_start=WEEK,criterion_results=[True,True],evidence=[{'kind':'test_log','detail':'two checks passed'}])
        self.assertEqual(r['status'],'delivered')
    def test_failed_criterion_overrides_general_claim(self):
        r=assess_acceptance(contract(),week_start=WEEK,user_attested=True,criterion_results=[True,False],evidence=[{'kind':'user_report','detail':'都完成了'}])
        self.assertEqual(r['status'],'not_delivered')
    def test_blocked_keeps_reason(self):
        r=assess_acceptance(contract(),week_start=WEEK,blocked_reason='板子未到')
        self.assertEqual(r['status'],'blocked');self.assertEqual(r['reason'],'板子未到')
    def test_result_count_mismatch_rejected(self):
        with self.assertRaises(ValueError):assess_acceptance(contract(),week_start=WEEK,criterion_results=[True])

class RolloverTests(unittest.TestCase):
    def test_archive_before_clear_no_native_changes(self):
        t=task();t.update(due_date='2026-12-31',parent_id='project',extra={'untouched':True})
        before=deepcopy(t);r=prepare_week_rollover(t,'2026-09-28')
        self.assertEqual(t,before);self.assertTrue(r['requires_archive_readback'])
        self.assertEqual(r['native_field_updates'],{});self.assertEqual(r['remote_mutations'],[])
        self.assertEqual(set(r['conditional_clear_patch']),{'week_start','weekly_commitment','weekly_delivery'})
    def test_idempotent_archive_id(self):
        self.assertEqual(prepare_week_rollover(task(),'2026-09-28'),prepare_week_rollover(task(),'2026-09-28'))
    def test_current_or_future_not_cleared(self):
        self.assertIsNone(prepare_week_rollover(task(),WEEK))
        self.assertIsNone(prepare_week_rollover(task(),'2026-09-14'))
    def test_legacy_pair_archived_without_contract(self):
        t=task();t.pop('weekly_delivery');r=prepare_week_rollover(t,'2026-09-28')
        self.assertNotIn('weekly_delivery',r['conditional_clear_patch'])
    def test_malformed_not_blindly_cleared(self):
        t=task();t.pop('weekly_commitment')
        with self.assertRaises(ValueError):prepare_week_rollover(t,'2026-09-28')
        t=task();t['weekly_delivery']['criteria']=[]
        with self.assertRaises(ValueError):prepare_week_rollover(t,'2026-09-28')
    def test_history_snapshot_independent(self):
        t=task();r=prepare_week_rollover(t,'2026-09-28');t['weekly_delivery']['scope']='changed'
        self.assertNotEqual(r['archive_event']['snapshot']['weekly_delivery']['scope'],'changed')
    def test_clear_week_does_not_modify_other_metadata(self):
        text=patch_body('natural',{'week_start':WEEK,'weekly_commitment':'must','weekly_delivery':contract(),'future':'keep'})
        r=prepare_week_rollover(task(),'2026-09-28')
        cleared=patch_body(text,r['conditional_clear_patch']);data=parse_block(split_body(cleared)[1])
        self.assertEqual(data['future'],'keep');self.assertNotIn('week_start',data)

class CommandTests(unittest.TestCase):
    def test_example_cli(self):
        result=subprocess.run([sys.executable,str(ROOT/'dida-planning-core/scripts/weekly_delivery.py'),'--input',str(ROOT/'dida-weekly-delivery/assets/example-plan.json')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(json.loads(result.stdout)['core_count'],2)
    def test_bad_json_nonzero(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'bad.json';p.write_text('{broken')
            result=subprocess.run([sys.executable,str(ROOT/'dida-planning-core/scripts/weekly_delivery.py'),'--input',str(p)],capture_output=True,text=True)
            self.assertEqual(result.returncode,2);self.assertIn('Input error',result.stderr)

if __name__=='__main__':unittest.main()
