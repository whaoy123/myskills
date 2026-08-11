#!/usr/bin/env python3
"""Deterministic multi-rail hardware power-budget calculator.

The agent extracts topology and datasheet currents into a small JSON schema.
This script performs only arithmetic, completeness checks, rail aggregation,
optional converter back-propagation, and Markdown/JSON rendering.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set


def num(value: Any, field: str, *, allow_none: bool = False) -> Optional[float]:
    if value is None and allow_none:
        return None
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{field} must be a number")
    v = float(value)
    if not math.isfinite(v):
        raise ValueError(f"{field} must be finite")
    return v


def positive(value: Any, field: str, *, allow_zero: bool = True) -> float:
    v = float(num(value, field))
    if v < 0 or (not allow_zero and v == 0):
        raise ValueError(f"{field} must be {'> 0' if not allow_zero else '>= 0'}")
    return v


@dataclass
class LoadRow:
    rail: str
    reference: str
    component: str
    quantity: int
    current_typ_a_each: Optional[float]
    current_budget_a_each: Optional[float]
    current_peak_a_each: Optional[float]
    current_typ_a_total: Optional[float]
    current_budget_a_total: Optional[float]
    current_peak_a_total: Optional[float]
    basis: str
    source: str
    notes: str
    budget_is_estimated: bool


@dataclass
class RailResult:
    name: str
    voltage_v: float
    domain: str
    direct_typ_current_a: Optional[float]
    direct_budget_current_a: Optional[float]
    derived_converter_input_current_a: float
    typ_current_a: Optional[float]
    budget_current_a: Optional[float]
    peak_current_a: Optional[float]
    typ_power_w: Optional[float]
    budget_power_w: Optional[float]
    design_margin_percent: float
    minimum_design_current_a: Optional[float]
    minimum_design_power_w: Optional[float]
    selected_rating_current_a: Optional[float]
    selected_rating_power_w: Optional[float]
    utilization_of_selected_percent: Optional[float]
    complete_for_guarantee: bool
    notes: str


@dataclass
class ConverterResult:
    name: str
    kind: str
    input_rail: str
    output_rails: List[str]
    output_budget_power_w: Optional[float]
    minimum_design_output_power_w: Optional[float]
    rated_output_power_w: Optional[float]
    rated_output_power_utilization_percent: Optional[float]
    rating_pass: Optional[bool]
    efficiency_used: Optional[float]
    derived_input_current_a: Optional[float]
    quiescent_current_a: float
    dissipation_w: Optional[float]
    complete_for_guarantee: bool
    source: str
    notes: str


def parse_rails(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    rails_raw = data.get("rails")
    if not isinstance(rails_raw, list) or not rails_raw:
        raise ValueError("rails must be a non-empty list")
    rails: Dict[str, Dict[str, Any]] = {}
    for i, r in enumerate(rails_raw):
        if not isinstance(r, dict):
            raise ValueError(f"rails[{i}] must be an object")
        name = str(r.get("name", "")).strip()
        if not name:
            raise ValueError(f"rails[{i}].name is required")
        if name in rails:
            raise ValueError(f"duplicate rail {name!r}")
        voltage = float(num(r.get("voltage_v"), f"rails[{i}].voltage_v"))
        if voltage == 0:
            raise ValueError(f"rail {name}: voltage_v cannot be zero")
        rr = dict(r)
        rr["name"] = name
        rr["voltage_v"] = voltage
        rr.setdefault("domain", "unspecified")
        rr.setdefault("notes", "")
        rails[name] = rr
    return rails


def parse_loads(data: Dict[str, Any], rails: Dict[str, Dict[str, Any]]) -> List[LoadRow]:
    loads_raw = data.get("loads", [])
    if not isinstance(loads_raw, list):
        raise ValueError("loads must be a list")
    rows: List[LoadRow] = []
    for i, x in enumerate(loads_raw):
        if not isinstance(x, dict):
            raise ValueError(f"loads[{i}] must be an object")
        rail = str(x.get("rail", "")).strip()
        if rail not in rails:
            raise ValueError(f"loads[{i}]: unknown rail {rail!r}")
        q_raw = x.get("quantity", 1)
        if not isinstance(q_raw, int) or isinstance(q_raw, bool) or q_raw <= 0:
            raise ValueError(f"loads[{i}].quantity must be a positive integer")
        q = q_raw
        typ = num(x.get("current_typ_a"), f"loads[{i}].current_typ_a", allow_none=True)
        mx = num(x.get("current_max_a"), f"loads[{i}].current_max_a", allow_none=True)
        design = num(x.get("current_design_a"), f"loads[{i}].current_design_a", allow_none=True)
        peak = num(x.get("peak_current_a"), f"loads[{i}].peak_current_a", allow_none=True)
        for field, v in [("current_typ_a", typ), ("current_max_a", mx), ("current_design_a", design), ("peak_current_a", peak)]:
            if v is not None and v < 0:
                raise ValueError(f"loads[{i}].{field} must be >= 0")
        budget = mx if mx is not None else design
        estimated = mx is None and design is not None
        rows.append(
            LoadRow(
                rail=rail,
                reference=str(x.get("reference", "unspecified")),
                component=str(x.get("component", "unspecified")),
                quantity=q,
                current_typ_a_each=typ,
                current_budget_a_each=budget,
                current_peak_a_each=peak,
                current_typ_a_total=(typ * q if typ is not None else None),
                current_budget_a_total=(budget * q if budget is not None else None),
                current_peak_a_total=(peak * q if peak is not None else None),
                basis=str(x.get("basis", "unspecified")),
                source=str(x.get("source", "")),
                notes=str(x.get("notes", "")),
                budget_is_estimated=estimated,
            )
        )
    return rows


def optional_sum(values: Iterable[Optional[float]]) -> Optional[float]:
    vals = list(values)
    if any(v is None for v in vals):
        return None
    return sum(float(v) for v in vals)


def build_converter_map(data: Dict[str, Any], rails: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    convs = data.get("converters", [])
    if not isinstance(convs, list):
        raise ValueError("converters must be a list")
    seen_outputs: Set[str] = set()
    parsed: List[Dict[str, Any]] = []
    for i, c in enumerate(convs):
        if not isinstance(c, dict):
            raise ValueError(f"converters[{i}] must be an object")
        name = str(c.get("name", "")).strip() or f"converter_{i+1}"
        kind = str(c.get("kind", "dc_dc")).lower()
        if kind not in {"dc_dc", "linear"}:
            raise ValueError(f"{name}: kind must be dc_dc or linear")
        inp = str(c.get("input_rail", "")).strip()
        if inp not in rails:
            raise ValueError(f"{name}: unknown input_rail {inp!r}")
        outs_raw = c.get("output_rails")
        if not isinstance(outs_raw, list) or not outs_raw:
            raise ValueError(f"{name}: output_rails must be a non-empty list")
        outs = [str(v).strip() for v in outs_raw]
        for out in outs:
            if out not in rails:
                raise ValueError(f"{name}: unknown output rail {out!r}")
            if out == inp:
                raise ValueError(f"{name}: input rail cannot also be an output rail")
            if out in seen_outputs:
                raise ValueError(f"rail {out!r} is produced by more than one converter")
            seen_outputs.add(out)
        if kind == "linear" and len(outs) != 1:
            raise ValueError(f"{name}: linear converter supports exactly one output rail")
        eff_min = num(c.get("efficiency_min"), f"{name}.efficiency_min", allow_none=True)
        eff_typ = num(c.get("efficiency_typ"), f"{name}.efficiency_typ", allow_none=True)
        for label, eff in [("efficiency_min", eff_min), ("efficiency_typ", eff_typ)]:
            if eff is not None and not (0 < eff <= 1):
                raise ValueError(f"{name}.{label} must be in (0, 1]")
        iq = positive(c.get("input_quiescent_current_a", 0.0), f"{name}.input_quiescent_current_a")
        cc = dict(c)
        cc.update({"name": name, "kind": kind, "input_rail": inp, "output_rails": outs,
                   "efficiency_min": eff_min, "efficiency_typ": eff_typ,
                   "input_quiescent_current_a": iq})
        parsed.append(cc)
    return parsed


def compute(data: Dict[str, Any]) -> Dict[str, Any]:
    rails = parse_rails(data)
    loads = parse_loads(data, rails)
    converters = build_converter_map(data, rails)
    default_margin = positive(data.get("design_margin_percent", 30.0), "design_margin_percent")

    loads_by_rail: Dict[str, List[LoadRow]] = {name: [] for name in rails}
    for row in loads:
        loads_by_rail[row.rail].append(row)

    direct: Dict[str, Dict[str, Any]] = {}
    for name in rails:
        lr = loads_by_rail[name]
        typ = optional_sum(x.current_typ_a_total for x in lr) if lr else 0.0
        budget = optional_sum(x.current_budget_a_total for x in lr) if lr else 0.0
        peak_values = [x.current_peak_a_total for x in lr if x.current_peak_a_total is not None]
        peak = sum(float(v) for v in peak_values) if peak_values else None
        direct[name] = {
            "typ": typ,
            "budget": budget,
            "peak": peak,
            "complete": all(x.current_budget_a_total is not None for x in lr),
        }

    producer = {out: c for c in converters for out in c["output_rails"]}
    converters_by_input: Dict[str, List[Dict[str, Any]]] = {name: [] for name in rails}
    for c in converters:
        converters_by_input[c["input_rail"]].append(c)

    memo_budget_current: Dict[str, Optional[float]] = {}
    memo_typ_current: Dict[str, Optional[float]] = {}
    conv_results: Dict[str, ConverterResult] = {}
    visiting: Set[str] = set()

    def rail_current(name: str, mode: str) -> Optional[float]:
        memo = memo_budget_current if mode == "budget" else memo_typ_current
        if name in memo:
            return memo[name]
        if name in visiting:
            raise ValueError(f"converter topology cycle detected at rail {name}")
        visiting.add(name)
        base = direct[name][mode]
        derived_total = 0.0
        complete = base is not None
        for c in converters_by_input[name]:
            out_currents: List[Optional[float]] = [rail_current(out, mode) for out in c["output_rails"]]
            if any(v is None for v in out_currents):
                complete = False
                continue
            out_power = sum(abs(rails[out]["voltage_v"]) * float(cur)
                            for out, cur in zip(c["output_rails"], out_currents))
            vin = abs(rails[name]["voltage_v"])
            iq = c["input_quiescent_current_a"]
            if c["kind"] == "dc_dc":
                eff = c["efficiency_min"] if mode == "budget" else (c["efficiency_typ"] or c["efficiency_min"])
                if eff is None:
                    complete = False
                    continue
                input_current = out_power / eff / vin + iq
            else:
                out_current = float(out_currents[0])
                input_current = out_current + iq
            derived_total += input_current
        visiting.remove(name)
        result = None if base is None or not complete else float(base) + derived_total
        memo[name] = result
        return result

    for name in rails:
        rail_current(name, "typ")
        rail_current(name, "budget")

    for c in converters:
        out_currents = [memo_budget_current[out] for out in c["output_rails"]]
        complete = all(v is not None for v in out_currents)
        out_power = None
        input_current = None
        diss = None
        eff_used = None
        if complete:
            out_power = sum(abs(rails[out]["voltage_v"]) * float(cur)
                            for out, cur in zip(c["output_rails"], out_currents))
            vin = abs(rails[c["input_rail"]]["voltage_v"])
            iq = c["input_quiescent_current_a"]
            if c["kind"] == "dc_dc":
                eff_used = c["efficiency_min"]
                if eff_used is not None:
                    input_current = out_power / eff_used / vin + iq
                    diss = vin * input_current - out_power
                else:
                    complete = False
            else:
                out_current = float(out_currents[0])
                input_current = out_current + iq
                pout = abs(rails[c["output_rails"][0]]["voltage_v"]) * out_current
                diss = vin * input_current - pout
        conv_results[c["name"]] = ConverterResult(
            name=c["name"], kind=c["kind"], input_rail=c["input_rail"], output_rails=c["output_rails"],
            output_budget_power_w=out_power, minimum_design_output_power_w=None,
            rated_output_power_w=num(c.get("rated_output_power_w"), f"{c['name']}.rated_output_power_w", allow_none=True),
            rated_output_power_utilization_percent=None, rating_pass=None, efficiency_used=eff_used,
            derived_input_current_a=input_current, quiescent_current_a=c["input_quiescent_current_a"],
            dissipation_w=diss, complete_for_guarantee=complete,
            source=str(c.get("source", "")), notes=str(c.get("notes", ""))
        )

    rail_results: List[RailResult] = []
    for name, r in rails.items():
        typ = memo_typ_current[name]
        budget = memo_budget_current[name]
        direct_budget = direct[name]["budget"]
        derived = 0.0
        if budget is not None and direct_budget is not None:
            derived = budget - direct_budget
        margin = positive(r.get("design_margin_percent", default_margin), f"rail {name}.design_margin_percent")
        min_design_current = budget * (1.0 + margin / 100.0) if budget is not None else None
        selected = num(r.get("selected_rating_current_a"), f"rail {name}.selected_rating_current_a", allow_none=True)
        if selected is not None and selected <= 0:
            raise ValueError(f"rail {name}.selected_rating_current_a must be > 0")
        selected_power = abs(r["voltage_v"]) * selected if selected is not None else None
        util = (min_design_current / selected * 100.0) if selected and min_design_current is not None else None
        complete = budget is not None
        rail_results.append(RailResult(
            name=name, voltage_v=r["voltage_v"], domain=str(r.get("domain", "unspecified")),
            direct_typ_current_a=direct[name]["typ"], direct_budget_current_a=direct_budget,
            derived_converter_input_current_a=derived,
            typ_current_a=typ, budget_current_a=budget, peak_current_a=direct[name]["peak"],
            typ_power_w=(abs(r["voltage_v"]) * typ if typ is not None else None),
            budget_power_w=(abs(r["voltage_v"]) * budget if budget is not None else None),
            design_margin_percent=margin, minimum_design_current_a=min_design_current,
            minimum_design_power_w=(abs(r["voltage_v"]) * min_design_current if min_design_current is not None else None),
            selected_rating_current_a=selected, selected_rating_power_w=selected_power,
            utilization_of_selected_percent=util, complete_for_guarantee=complete,
            notes=str(r.get("notes", ""))
        ))

    rail_result_map = {r.name: r for r in rail_results}
    for c in converters:
        cr = conv_results[c["name"]]
        design_powers = [rail_result_map[out].minimum_design_power_w for out in c["output_rails"]]
        cr.minimum_design_output_power_w = optional_sum(design_powers)
        if cr.rated_output_power_w is not None and cr.rated_output_power_w <= 0:
            raise ValueError(f"{cr.name}.rated_output_power_w must be > 0")
        if cr.rated_output_power_w is not None and cr.minimum_design_output_power_w is not None:
            cr.rated_output_power_utilization_percent = cr.minimum_design_output_power_w / cr.rated_output_power_w * 100.0
            cr.rating_pass = cr.rated_output_power_w >= cr.minimum_design_output_power_w

    root_rails = [name for name in rails if name not in producer]
    root_budget_power = optional_sum(
        abs(rails[name]["voltage_v"]) * memo_budget_current[name] if memo_budget_current[name] is not None else None
        for name in root_rails
    )
    root_typ_power = optional_sum(
        abs(rails[name]["voltage_v"]) * memo_typ_current[name] if memo_typ_current[name] is not None else None
        for name in root_rails
    )

    warnings: List[str] = []
    for row in loads:
        if row.current_budget_a_each is None:
            warnings.append(f"{row.reference} {row.component} on {row.rail}: no max/design current; guarantee budget is incomplete.")
        elif row.budget_is_estimated:
            warnings.append(f"{row.reference} {row.component} on {row.rail}: current_design_a is an engineering assumption, not a datasheet maximum.")
        if not row.source:
            warnings.append(f"{row.reference} {row.component} on {row.rail}: missing source/page traceability.")
    for rr in rail_results:
        if rr.selected_rating_current_a is not None and rr.minimum_design_current_a is not None and rr.selected_rating_current_a < rr.minimum_design_current_a:
            warnings.append(f"{rr.name}: selected rating {rr.selected_rating_current_a:g} A is below required {rr.minimum_design_current_a:g} A.")
    for c in conv_results.values():
        if not c.complete_for_guarantee:
            warnings.append(f"{c.name}: converter input budget is incomplete; check output rail maxima and minimum efficiency.")
        if c.rating_pass is False:
            warnings.append(f"{c.name}: rated output power {c.rated_output_power_w:g} W is below required design power {c.minimum_design_output_power_w:g} W.")

    return {
        "design": data.get("design", {}),
        "root_rails": root_rails,
        "loads": [asdict(x) for x in loads],
        "rails": [asdict(x) for x in rail_results],
        "converters": [asdict(conv_results[c["name"]]) for c in converters],
        "summary": {
            "root_typ_power_w": root_typ_power,
            "root_budget_power_w": root_budget_power,
            "guarantee_complete": all(x.complete_for_guarantee for x in rail_results),
        },
        "warnings": warnings,
    }


def fnum(v: Optional[float], scale: float = 1.0, digits: int = 4) -> str:
    if v is None:
        return "—"
    return f"{v * scale:.{digits}g}"


def render_markdown(result: Dict[str, Any]) -> str:
    name = result.get("design", {}).get("name", "Hardware power budget")
    lines = [f"# {name}", "", "## 电源轨预算", "",
             "| 电源轨 | 电压 | 典型电流 | 预算/最坏电流 | 最坏功率 | 余量 | 设计最低电流 | 设计最低功率 | 已选额定电流 | 已选额定功率 | 完整性 |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in result["rails"]:
        lines.append(
            f"| {r['name']} | {r['voltage_v']:.6g} V | {fnum(r['typ_current_a'], 1000)} mA | "
            f"{fnum(r['budget_current_a'], 1000)} mA | {fnum(r['budget_power_w'])} W | "
            f"{r['design_margin_percent']:.6g}% | {fnum(r['minimum_design_current_a'], 1000)} mA | "
            f"{fnum(r['minimum_design_power_w'])} W | {fnum(r['selected_rating_current_a'], 1000)} mA | "
            f"{fnum(r['selected_rating_power_w'])} W | {'PASS' if r['complete_for_guarantee'] else 'INCOMPLETE'} |"
        )
    lines += ["", "## 负载明细", "",
              "| 电源轨 | 器件 | 数量 | Ityp/颗 | Ibudget/颗 | Ipeak/颗 | 依据 | 来源 |",
              "|---|---|---:|---:|---:|---:|---|---|"]
    for x in result["loads"]:
        source = str(x["source"]).replace("|", "\\|")
        basis = str(x["basis"]).replace("|", "\\|")
        lines.append(
            f"| {x['rail']} | {x['reference']} {x['component']} | {x['quantity']} | "
            f"{fnum(x['current_typ_a_each'], 1000)} mA | {fnum(x['current_budget_a_each'], 1000)} mA | "
            f"{fnum(x['current_peak_a_each'], 1000)} mA | {basis} | {source} |"
        )
    if result["converters"]:
        lines += ["", "## 转换器回推", "",
                  "| 转换器 | 类型 | 输入轨 | 输出轨 | 最坏输出功率 | 设计最低输出功率 | 已选额定功率 | 最低效率 | 最坏输入电流 | 转换器损耗 | 选型 |",
                  "|---|---|---|---|---:|---:|---:|---:|---:|---:|---|"]
        for c in result["converters"]:
            lines.append(
                f"| {c['name']} | {c['kind']} | {c['input_rail']} | {', '.join(c['output_rails'])} | "
                f"{fnum(c['output_budget_power_w'])} W | {fnum(c['minimum_design_output_power_w'])} W | "
                f"{fnum(c['rated_output_power_w'])} W | {fnum(c['efficiency_used'], 100, 3)}% | "
                f"{fnum(c['derived_input_current_a'], 1000)} mA | {fnum(c['dissipation_w'])} W | "
                f"{('PASS' if c['rating_pass'] else 'FAIL') if c['rating_pass'] is not None else ('CHECK' if c['complete_for_guarantee'] else 'INCOMPLETE')} |"
            )
    s = result["summary"]
    lines += ["", "## 汇总", "",
              f"- 根电源轨：{', '.join(result['root_rails']) if result['root_rails'] else '—'}",
              f"- 根电源典型功耗：{fnum(s['root_typ_power_w'])} W",
              f"- 根电源预算/最坏功耗：{fnum(s['root_budget_power_w'])} W",
              f"- 可用于保证：{'是' if s['guarantee_complete'] else '否'}"]
    if result["warnings"]:
        lines += ["", "## 警告", ""] + [f"- {w}" for w in result["warnings"]]
    return "\n".join(lines) + "\n"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path)
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p.add_argument("-o", "--output", type=Path)
    args = p.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        result = compute(data)
        text = json.dumps(result, ensure_ascii=False, indent=2) + "\n" if args.format == "json" else render_markdown(result)
        if args.output:
            args.output.write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text)
        return 0
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
