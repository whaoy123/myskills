#!/usr/bin/env python3
"""Deterministic multi-rail current/power budget calculator."""
from __future__ import annotations

import argparse, json, math, sys
from pathlib import Path


def _num(v, name, allow_none=False):
    if v is None and allow_none:
        return None
    if not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(float(v)):
        raise ValueError(f"{name} must be a finite number")
    return float(v)


def _nonneg(v, name):
    x = _num(v, name)
    if x < 0:
        raise ValueError(f"{name} must be >= 0")
    return x


def _sum_or_none(values):
    values = list(values)
    return None if any(v is None for v in values) else sum(values)


def _parse(data):
    rails = {}
    raw_rails = data.get("rails")
    if not isinstance(raw_rails, list) or not raw_rails:
        raise ValueError("rails must be a non-empty list")
    for i, r in enumerate(raw_rails):
        name = str(r.get("name", "")).strip()
        if not name or name in rails:
            raise ValueError(f"rails[{i}].name is missing or duplicated")
        v = _num(r.get("voltage_v"), f"rails[{i}].voltage_v")
        if v == 0:
            raise ValueError(f"{name}: voltage_v cannot be zero")
        rails[name] = {**r, "name": name, "voltage_v": v, "domain": str(r.get("domain", "unspecified"))}

    loads = []
    for i, x in enumerate(data.get("loads", [])):
        rail = str(x.get("rail", "")).strip()
        if rail not in rails:
            raise ValueError(f"loads[{i}]: unknown rail {rail!r}")
        q = x.get("quantity", 1)
        if not isinstance(q, int) or isinstance(q, bool) or q <= 0:
            raise ValueError(f"loads[{i}].quantity must be a positive integer")
        typ = _num(x.get("current_typ_a"), f"loads[{i}].current_typ_a", True)
        mx = _num(x.get("current_max_a"), f"loads[{i}].current_max_a", True)
        design = _num(x.get("current_design_a"), f"loads[{i}].current_design_a", True)
        peak = _num(x.get("peak_current_a"), f"loads[{i}].peak_current_a", True)
        for field, value in (("current_typ_a", typ), ("current_max_a", mx), ("current_design_a", design), ("peak_current_a", peak)):
            if value is not None and value < 0:
                raise ValueError(f"loads[{i}].{field} must be >= 0")
        budget = mx if mx is not None else design
        estimated = mx is None and design is not None
        loads.append({
            "rail": rail, "reference": str(x.get("reference", "unspecified")),
            "component": str(x.get("component", "unspecified")), "quantity": q,
            "current_typ_a_each": typ, "current_budget_a_each": budget,
            "current_peak_a_each": peak,
            "current_typ_a_total": None if typ is None else q * typ,
            "current_budget_a_total": None if budget is None else q * budget,
            "current_peak_a_total": None if peak is None else q * peak,
            "basis": str(x.get("basis", "unspecified")), "source": str(x.get("source", "")),
            "notes": str(x.get("notes", "")), "budget_is_estimated": estimated,
        })

    converters, produced = [], set()
    for i, c in enumerate(data.get("converters", [])):
        name = str(c.get("name", "")).strip() or f"converter_{i+1}"
        kind = str(c.get("kind", "dc_dc")).lower()
        inp = str(c.get("input_rail", "")).strip()
        outs = [str(v).strip() for v in c.get("output_rails", [])]
        if kind not in {"dc_dc", "linear"} or inp not in rails or not outs:
            raise ValueError(f"{name}: invalid converter definition")
        if kind == "linear" and len(outs) != 1:
            raise ValueError(f"{name}: linear converter supports one output rail")
        for out in outs:
            if out not in rails or out == inp or out in produced:
                raise ValueError(f"{name}: invalid/duplicate output rail {out!r}")
            produced.add(out)
        emin = _num(c.get("efficiency_min"), f"{name}.efficiency_min", True)
        etyp = _num(c.get("efficiency_typ"), f"{name}.efficiency_typ", True)
        for label, eff in (("efficiency_min", emin), ("efficiency_typ", etyp)):
            if eff is not None and not 0 < eff <= 1:
                raise ValueError(f"{name}.{label} must be in (0,1]")
        converters.append({**c, "name": name, "kind": kind, "input_rail": inp, "output_rails": outs,
                           "efficiency_min": emin, "efficiency_typ": etyp,
                           "input_quiescent_current_a": _nonneg(c.get("input_quiescent_current_a", 0), f"{name}.Iq")})
    return rails, loads, converters, produced


def compute(data):
    rails, loads, converters, produced = _parse(data)
    margin_default = _nonneg(data.get("design_margin_percent", 30), "design_margin_percent")
    by_rail = {r: [] for r in rails}
    for x in loads:
        by_rail[x["rail"]].append(x)
    direct = {}
    for r, rows in by_rail.items():
        direct[r] = {
            "typ": _sum_or_none(x["current_typ_a_total"] for x in rows) if rows else 0.0,
            "budget": _sum_or_none(x["current_budget_a_total"] for x in rows) if rows else 0.0,
            "peak": sum(x["current_peak_a_total"] for x in rows if x["current_peak_a_total"] is not None) or None,
            "guaranteed": all(x["current_budget_a_total"] is not None and not x["budget_is_estimated"] for x in rows),
        }
    by_input = {r: [] for r in rails}
    for c in converters:
        by_input[c["input_rail"]].append(c)

    memo = {"typ": {}, "budget": {}}
    visiting = set()
    def rail_current(name, mode):
        if name in memo[mode]:
            return memo[mode][name]
        key = (name, mode)
        if key in visiting:
            raise ValueError(f"converter topology cycle at {name}")
        visiting.add(key)
        base = direct[name][mode]
        if base is None:
            value = None
        else:
            value = base
            for c in by_input[name]:
                outs = [rail_current(o, mode) for o in c["output_rails"]]
                if any(v is None for v in outs):
                    value = None; break
                pout = sum(abs(rails[o]["voltage_v"]) * cur for o, cur in zip(c["output_rails"], outs))
                if c["kind"] == "dc_dc":
                    eff = c["efficiency_min"] if mode == "budget" else (c["efficiency_typ"] or c["efficiency_min"])
                    if eff is None:
                        value = None; break
                    value += pout / eff / abs(rails[name]["voltage_v"]) + c["input_quiescent_current_a"]
                else:
                    value += outs[0] + c["input_quiescent_current_a"]
        visiting.remove(key)
        memo[mode][name] = value
        return value

    complete_memo = {}
    def rail_complete(name, stack=None):
        if name in complete_memo:
            return complete_memo[name]
        stack = set() if stack is None else set(stack)
        if name in stack:
            raise ValueError(f"converter topology cycle at {name}")
        stack.add(name)
        ok = direct[name]["guaranteed"]
        for c in by_input[name]:
            if c["kind"] == "dc_dc" and c["efficiency_min"] is None:
                ok = False
            if not all(rail_complete(o, stack) for o in c["output_rails"]):
                ok = False
        complete_memo[name] = ok
        return ok

    for r in rails:
        rail_current(r, "typ"); rail_current(r, "budget"); rail_complete(r)

    rail_results = []
    for name, r in rails.items():
        typ, budget = memo["typ"][name], memo["budget"][name]
        margin = _nonneg(r.get("design_margin_percent", margin_default), f"{name}.design_margin_percent")
        design_i = None if budget is None else budget * (1 + margin / 100)
        selected = _num(r.get("selected_rating_current_a"), f"{name}.selected_rating_current_a", True)
        if selected is not None and selected <= 0:
            raise ValueError(f"{name}.selected_rating_current_a must be > 0")
        rail_results.append({
            "name": name, "voltage_v": r["voltage_v"], "domain": r["domain"],
            "direct_typ_current_a": direct[name]["typ"], "direct_budget_current_a": direct[name]["budget"],
            "derived_converter_input_current_a": 0 if budget is None or direct[name]["budget"] is None else budget - direct[name]["budget"],
            "typ_current_a": typ, "budget_current_a": budget, "peak_current_a": direct[name]["peak"],
            "typ_power_w": None if typ is None else abs(r["voltage_v"]) * typ,
            "budget_power_w": None if budget is None else abs(r["voltage_v"]) * budget,
            "design_margin_percent": margin, "minimum_design_current_a": design_i,
            "minimum_design_power_w": None if design_i is None else abs(r["voltage_v"]) * design_i,
            "selected_rating_current_a": selected,
            "selected_rating_power_w": None if selected is None else abs(r["voltage_v"]) * selected,
            "utilization_of_selected_percent": None if selected is None or design_i is None else design_i / selected * 100,
            "complete_for_guarantee": budget is not None and rail_complete(name), "notes": str(r.get("notes", "")),
        })
    rr = {r["name"]: r for r in rail_results}

    converter_results = []
    for c in converters:
        outs = [memo["budget"][o] for o in c["output_rails"]]
        pout = None if any(v is None for v in outs) else sum(abs(rails[o]["voltage_v"]) * cur for o, cur in zip(c["output_rails"], outs))
        design_p = _sum_or_none(rr[o]["minimum_design_power_w"] for o in c["output_rails"])
        complete = all(rail_complete(o) for o in c["output_rails"])
        eff, iin, diss = None, None, None
        if pout is not None:
            vin = abs(rails[c["input_rail"]]["voltage_v"])
            if c["kind"] == "dc_dc":
                eff = c["efficiency_min"]
                if eff is None:
                    complete = False
                else:
                    iin = pout / eff / vin + c["input_quiescent_current_a"]
                    diss = vin * iin - pout
            else:
                iin = outs[0] + c["input_quiescent_current_a"]
                diss = vin * iin - pout
        rated = _num(c.get("rated_output_power_w"), f"{c['name']}.rated_output_power_w", True)
        if rated is not None and rated <= 0:
            raise ValueError(f"{c['name']}.rated_output_power_w must be > 0")
        converter_results.append({
            "name": c["name"], "kind": c["kind"], "input_rail": c["input_rail"], "output_rails": c["output_rails"],
            "output_budget_power_w": pout, "minimum_design_output_power_w": design_p,
            "rated_output_power_w": rated,
            "rated_output_power_utilization_percent": None if rated is None or design_p is None else design_p / rated * 100,
            "rating_pass": None if rated is None or design_p is None else rated >= design_p,
            "efficiency_used": eff, "derived_input_current_a": iin,
            "quiescent_current_a": c["input_quiescent_current_a"], "dissipation_w": diss,
            "complete_for_guarantee": complete, "source": str(c.get("source", "")), "notes": str(c.get("notes", "")),
        })

    roots = [r for r in rails if r not in produced]
    summary = {
        "root_typ_power_w": _sum_or_none(None if memo["typ"][r] is None else abs(rails[r]["voltage_v"]) * memo["typ"][r] for r in roots),
        "root_budget_power_w": _sum_or_none(None if memo["budget"][r] is None else abs(rails[r]["voltage_v"]) * memo["budget"][r] for r in roots),
        "guarantee_complete": all(r["complete_for_guarantee"] for r in rail_results),
    }
    warnings = []
    for x in loads:
        if x["current_budget_a_each"] is None:
            warnings.append(f"{x['reference']} {x['component']} on {x['rail']}: no max/design current; worst-case budget is incomplete.")
        elif x["budget_is_estimated"]:
            warnings.append(f"{x['reference']} {x['component']} on {x['rail']}: current_design_a is an engineering assumption, not a datasheet maximum.")
        if not x["source"]:
            warnings.append(f"{x['reference']} {x['component']} on {x['rail']}: missing source/page traceability.")
    for r in rail_results:
        if r["selected_rating_current_a"] is not None and r["minimum_design_current_a"] is not None and r["selected_rating_current_a"] < r["minimum_design_current_a"]:
            warnings.append(f"{r['name']}: selected current rating is below the design minimum.")
    for c in converter_results:
        if not c["complete_for_guarantee"]:
            warnings.append(f"{c['name']}: converter guarantee is incomplete; check downstream maxima and minimum efficiency.")
        if c["rating_pass"] is False:
            warnings.append(f"{c['name']}: rated output power is below the design minimum.")
    return {"design": data.get("design", {}), "root_rails": roots, "loads": loads, "rails": rail_results,
            "converters": converter_results, "summary": summary, "warnings": warnings}


def _f(v, scale=1, digits=4):
    return "—" if v is None else f"{v * scale:.{digits}g}"


def render_markdown(result):
    lines = [f"# {result.get('design', {}).get('name', 'Hardware power budget')}", "", "## 电源轨预算", "",
             "| 电源轨 | 电压 | 典型电流 | 预算/最坏电流 | 最坏功率 | 余量 | 设计最低电流 | 设计最低功率 | 已选额定电流 | 已选额定功率 | 完整性 |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in result["rails"]:
        lines.append(f"| {r['name']} | {r['voltage_v']:.6g} V | {_f(r['typ_current_a'],1000)} mA | {_f(r['budget_current_a'],1000)} mA | {_f(r['budget_power_w'])} W | {r['design_margin_percent']:.6g}% | {_f(r['minimum_design_current_a'],1000)} mA | {_f(r['minimum_design_power_w'])} W | {_f(r['selected_rating_current_a'],1000)} mA | {_f(r['selected_rating_power_w'])} W | {'PASS' if r['complete_for_guarantee'] else 'INCOMPLETE'} |")
    lines += ["", "## 负载明细", "", "| 电源轨 | 器件 | 数量 | Ityp/颗 | Ibudget/颗 | Ipeak/颗 | 依据 | 来源 |", "|---|---|---:|---:|---:|---:|---|---|"]
    for x in result["loads"]:
        lines.append(f"| {x['rail']} | {x['reference']} {x['component']} | {x['quantity']} | {_f(x['current_typ_a_each'],1000)} mA | {_f(x['current_budget_a_each'],1000)} mA | {_f(x['current_peak_a_each'],1000)} mA | {x['basis'].replace('|','/')} | {x['source'].replace('|','/')} |")
    if result["converters"]:
        lines += ["", "## 转换器回推", "", "| 转换器 | 类型 | 输入轨 | 输出轨 | 最坏输出功率 | 设计最低输出功率 | 已选额定功率 | 最低效率 | 最坏输入电流 | 转换器损耗 | 选型 |", "|---|---|---|---|---:|---:|---:|---:|---:|---:|---|"]
        for c in result["converters"]:
            status = ("PASS" if c["rating_pass"] else "FAIL") if c["rating_pass"] is not None else ("CHECK" if c["complete_for_guarantee"] else "INCOMPLETE")
            lines.append(f"| {c['name']} | {c['kind']} | {c['input_rail']} | {', '.join(c['output_rails'])} | {_f(c['output_budget_power_w'])} W | {_f(c['minimum_design_output_power_w'])} W | {_f(c['rated_output_power_w'])} W | {_f(c['efficiency_used'],100,3)}% | {_f(c['derived_input_current_a'],1000)} mA | {_f(c['dissipation_w'])} W | {status} |")
    s = result["summary"]
    lines += ["", "## 汇总", "", f"- 根电源轨：{', '.join(result['root_rails']) or '—'}", f"- 根电源典型功耗：{_f(s['root_typ_power_w'])} W", f"- 根电源预算/最坏功耗：{_f(s['root_budget_power_w'])} W", f"- 可用于保证：{'是' if s['guarantee_complete'] else '否'}"]
    if result["warnings"]:
        lines += ["", "## 警告", ""] + [f"- {w}" for w in result["warnings"]]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path); ap.add_argument("--format", choices=["markdown","json"], default="markdown"); ap.add_argument("-o","--output", type=Path)
    args = ap.parse_args()
    try:
        result = compute(json.loads(args.input.read_text(encoding="utf-8")))
        text = json.dumps(result, ensure_ascii=False, indent=2) + "\n" if args.format == "json" else render_markdown(result)
        args.output.write_text(text, encoding="utf-8") if args.output else sys.stdout.write(text)
        return 0
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr); return 2


if __name__ == "__main__":
    raise SystemExit(main())
