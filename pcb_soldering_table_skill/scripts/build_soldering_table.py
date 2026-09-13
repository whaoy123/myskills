#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

BOM_COLUMNS = ["Designator", "Nominal", "ResolvedDescription", "Footprint", "DesignModel", "FinalModel"]
RULE_COLUMNS = ["MatchField", "MatchValue", "DisplayPackage", "MountType", "PinsPerPart", "FixedPinsPerPart", "Include", "CompatibleFootprints", "DNPReason", "ConfirmedBy", "ConfirmedDate", "Notes"]
PROCUREMENT_COLUMNS = ["Model", "StockQty", "PurchasedQty", "ReceivedQty", "ReservedQty", "TargetMultiplier", "Source", "Notes"]
HEADERS = ["位号", "型号/规格", "封装/类型", "数量", "贴片焊点", "直插焊点", "备注", "补购状态"]
AUDIT_HEADERS = ["型号", "板上数量", "目标倍率", "目标数量", "原库存", "本次采购", "已到货", "预留数量", "采购口径可用", "实物口径可用", "补购缺口", "状态", "来源/备注"]
DNP_HEADERS = ["位号", "型号", "设计封装", "不焊接原因", "确认人", "确认日期"]


class ValidationError(RuntimeError):
    pass


def read_csv(path: Path, required: List[str]) -> List[dict]:
    if not path.exists():
        raise ValidationError(f"缺少输入文件: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in required if c not in (reader.fieldnames or [])]
        if missing:
            raise ValidationError(f"{path.name} 缺少列: {', '.join(missing)}")
        rows = []
        for lineno, row in enumerate(reader, 2):
            clean = {k: (v or "").strip() for k, v in row.items()}
            if any(clean.get(c, "") for c in required):
                clean["_line"] = lineno; rows.append(clean)
        return rows


def truthy(v: str) -> bool:
    return v.strip().lower() in {"1", "true", "yes", "y", "是", "include"}


def to_int(v: str, what: str, blank=0):
    if v == "": return blank
    try: n = int(v)
    except ValueError: raise ValidationError(f"{what} 必须为整数，实际为 {v!r}")
    if n < 0: raise ValidationError(f"{what} 不能为负数")
    return n


def to_multiplier(v: str, what: str):
    try: n = float(v)
    except ValueError: raise ValidationError(f"{what} 必须为数字")
    if n < 1: raise ValidationError(f"{what} 不能小于 1")
    return n


def natural_key(s: str):
    m = re.fullmatch(r"([A-Za-z]+)(\d+)", s.strip())
    return (m.group(1).upper(), int(m.group(2))) if m else (s.upper(), 0)


def normalize_spec(nominal: str, description: str, final_model: str) -> str:
    parts = [p.strip() for p in (description or "").replace("；", ";").split(";") if p.strip()]
    cleaned = []
    for part in parts:
        if part == nominal: continue
        m = re.match(r"^([^:：]+)[:：]\s*(.*)$", part)
        if m and m.group(1).strip() in {"具体型号", "型号", "料号", "LibRef"}: continue
        if m and m.group(1).strip() in {"容值", "阻值", "电感值", "标称值/名称"} and m.group(2).strip() == nominal: continue
        cleaned.append(part)
    return "；".join(([nominal] if nominal else []) + cleaned + ([f"具体型号：{final_model}"] if final_model else []))


def build_rule_index(rows):
    idx = {}
    for r in rows:
        field, value = r["MatchField"], r["MatchValue"]
        if field not in {"Model", "Footprint"} or not value:
            raise ValidationError(f"component_rules.csv:{r['_line']} MatchField/MatchValue 非法")
        if (field, value) in idx:
            raise ValidationError(f"component_rules.csv 规则重复: {field}={value}")
        mount = r["MountType"].upper()
        if mount not in {"SMD", "THT", "NONE"}:
            raise ValidationError(f"{field}={value} 的 MountType 必须是 SMD/THT/NONE")
        r["_mount"] = mount
        r["_pins"] = to_int(r["PinsPerPart"], f"{field}={value} PinsPerPart")
        r["_fixed"] = to_int(r["FixedPinsPerPart"], f"{field}={value} FixedPinsPerPart")
        include = truthy(r["Include"]) and mount != "NONE"
        if not include and not all((r["DNPReason"], r["ConfirmedBy"], r["ConfirmedDate"])):
            raise ValidationError(f"{field}={value} 不焊接规则必须填写 DNPReason/ConfirmedBy/ConfirmedDate")
        idx[(field, value)] = r
    return idx


def find_rule(row, idx):
    model_rule = idx.get(("Model", row["FinalModel"]))
    if model_rule:
        return model_rule
    if row["FinalModel"] != row["DesignModel"]:
        raise ValidationError(f"bom.csv:{row['_line']} {row['Designator']} 发生型号替换，必须增加 FinalModel 精确规则并验证 CompatibleFootprints")
    footprint_rule = idx.get(("Footprint", row["Footprint"]))
    if footprint_rule:
        return footprint_rule
    raise ValidationError(f"bom.csv:{row['_line']} {row['Designator']} ({row['FinalModel']} / {row['Footprint']}) 没有匹配规则")


def check_package(row, rule):
    if rule["MatchField"] == "Footprint": return
    compatible = {x.strip() for x in re.split(r"[;,；]", rule["CompatibleFootprints"]) if x.strip()}
    if not compatible:
        raise ValidationError(f"Model={rule['MatchValue']} 必须填写 CompatibleFootprints")
    if row["Footprint"] not in compatible:
        raise ValidationError(f"{row['Designator']} 最终型号 {row['FinalModel']} 与设计封装 {row['Footprint']} 不兼容，允许={sorted(compatible)}")


def read_procurement(rows):
    result = {}
    for r in rows:
        model = r["Model"]
        if not model or model in result:
            raise ValidationError(f"procurement.csv:{r['_line']} Model 为空或重复: {model}")
        received = None if r["ReceivedQty"] == "" else to_int(r["ReceivedQty"], f"{model} ReceivedQty")
        purchased = to_int(r["PurchasedQty"], f"{model} PurchasedQty")
        if received is not None and received > purchased:
            raise ValidationError(f"{model} ReceivedQty 不能大于 PurchasedQty")
        result[model] = {"stock": to_int(r["StockQty"], f"{model} StockQty"), "purchased": purchased, "received": received, "reserved": to_int(r["ReservedQty"], f"{model} ReservedQty"), "multiplier": to_multiplier(r["TargetMultiplier"], f"{model} TargetMultiplier"), "source": r["Source"], "notes": r["Notes"]}
    return result


def normalize(bom_rows, rule_rows, procurement_rows):
    idx, procurement, seen = build_rule_index(rule_rows), read_procurement(procurement_rows), set()
    groups, required, excluded = defaultdict(lambda: {"designators": []}), defaultdict(int), []
    for r in bom_rows:
        d = r["Designator"]
        if not d or d in seen: raise ValidationError(f"BOM 位号为空或重复: {d}")
        seen.add(d)
        if not r["FinalModel"]: raise ValidationError(f"{d} 的 FinalModel 为空")
        rule = find_rule(r, idx); check_package(r, rule)
        if not truthy(rule["Include"]) or rule["_mount"] == "NONE":
            excluded.append({"Designator": d, "Model": r["FinalModel"], "Footprint": r["Footprint"], "Reason": rule["DNPReason"], "ConfirmedBy": rule["ConfirmedBy"], "ConfirmedDate": rule["ConfirmedDate"]})
            continue
        spec, package = normalize_spec(r["Nominal"], r["ResolvedDescription"], r["FinalModel"]), rule["DisplayPackage"] or r["Footprint"]
        key = (r["FinalModel"], spec, package, rule["_mount"], rule["_pins"], rule["_fixed"], rule["Notes"])
        g = groups[key]; g.update({"model": r["FinalModel"], "spec": spec, "package": package, "mount": rule["_mount"], "pins": rule["_pins"], "fixed": rule["_fixed"], "notes": rule["Notes"]}); g["designators"].append(d)
        required[r["FinalModel"]] += 1
    audit, status_by_model, shortages = [], {}, {}
    missing_procurement = sorted(set(required) - set(procurement))
    if missing_procurement:
        raise ValidationError(f"procurement.csv 缺少所需型号，无法确定备料倍率和库存口径: {missing_procurement}")
    for model, qty in sorted(required.items()):
        p = procurement[model]
        target = math.ceil(qty * p["multiplier"])
        purchased_available = max(p["stock"] + p["purchased"] - p["reserved"], 0)
        physical_available = max(p["stock"] + (p["received"] or 0) - p["reserved"], 0)
        gap = max(target - purchased_available, 0)
        if gap:
            status = f"待补购 {gap}只"; shortages[model] = gap
        elif physical_available < target:
            status = "采购数量覆盖，待到货清点"
        else:
            status = "实物数量覆盖"
        status_by_model[model] = status
        audit.append({"Model": model, "Required": qty, "Multiplier": p["multiplier"], "Target": target, "Stock": p["stock"], "Purchased": p["purchased"], "Received": p["received"], "Reserved": p["reserved"], "PurchasedAvailable": purchased_available, "PhysicalAvailable": physical_available, "Gap": gap, "Status": status, "SourceNotes": "；".join(x for x in (p["source"], p["notes"]) if x)})
    rows = []
    for g in groups.values():
        ds = sorted(g["designators"], key=natural_key); qty = len(ds); joints = qty * (g["pins"] + g["fixed"])
        notes = g["notes"]
        if g["fixed"] and "固定脚" not in notes: notes = "；".join(x for x in (notes, f"每只含{g['fixed']}个固定脚") if x)
        status = status_by_model[g["model"]]
        rows.append({"Designators": ", ".join(ds), "Model": g["model"], "Spec": g["spec"], "Package": g["package"], "Quantity": qty, "SMDPoints": joints if g["mount"] == "SMD" else 0, "THTPoints": joints if g["mount"] == "THT" else 0, "Notes": notes, "PurchaseStatus": "" if status == "实物数量覆盖" else status, "ShortageQty": shortages.get(g["model"], 0)})
    rows.sort(key=lambda x: natural_key(x["Designators"].split(",")[0]))
    unmatched = sorted(set(procurement) - set(required))
    return rows, audit, excluded, shortages, unmatched


def style_range(ws, min_row, max_row, max_col):
    side, white = Side(style="thin", color="000000"), PatternFill("solid", fgColor="FFFFFF")
    for row in ws.iter_rows(min_row=min_row, max_row=max_row, min_col=1, max_col=max_col):
        for cell in row:
            cell.fill = white; cell.font = Font(name="Arial", size=10, color="000000", bold=cell.row == min_row)
            cell.alignment = Alignment(horizontal="center" if cell.column >= 4 else "left", vertical="center", wrap_text=True)
            cell.border = Border(left=side, right=side, top=side, bottom=side)
    for r in range(min_row, max_row + 1):
        max_len = max(len(str(ws.cell(r, c).value or "")) for c in range(1, max_col + 1))
        ws.row_dimensions[r].height = max(22, 15 * ((max_len // 48) + 1))


def write_xlsx(rows, audit, excluded, path: Path):
    wb = Workbook(); ws = wb.active; ws.title = "焊接清单"; ws.append(HEADERS)
    for r in rows: ws.append([r["Designators"], r["Spec"], r["Package"], r["Quantity"], r["SMDPoints"], r["THTPoints"], r["Notes"], r["PurchaseStatus"]])
    total = ws.max_row + 1; ws.merge_cells(start_row=total, start_column=1, end_row=total, end_column=3)
    ws.cell(total, 1, "合计"); smd = sum(r["SMDPoints"] for r in rows); tht = sum(r["THTPoints"] for r in rows)
    for col, value in enumerate([sum(r["Quantity"] for r in rows), smd, tht, f"总焊点：{smd + tht}", ""], 4): ws.cell(total, col, value)
    for c, w in enumerate([30, 64, 26, 11, 11, 11, 24, 22], 1): ws.column_dimensions[get_column_letter(c)].width = w
    style_range(ws, 1, total, 8)
    for cell in ws[total]: cell.font = Font(name="Arial", size=10, color="000000", bold=True)
    ws.freeze_panes = "A2"
    for i, r in enumerate(rows, 2):
        if r["ShortageQty"]:
            for cell in ws[i]: cell.fill = PatternFill("solid", fgColor="FFF2CC")
        elif r["PurchaseStatus"]:
            for cell in ws[i]: cell.fill = PatternFill("solid", fgColor="FCE4D6")

    inv = wb.create_sheet("备料核对"); inv.append(AUDIT_HEADERS)
    for a in audit: inv.append([a[k] for k in ("Model", "Required", "Multiplier", "Target", "Stock", "Purchased", "Received", "Reserved", "PurchasedAvailable", "PhysicalAvailable", "Gap", "Status", "SourceNotes")])
    end_audit = inv.max_row
    if excluded:
        inv.append([]); inv.append(["不焊接核对"]); inv.append(DNP_HEADERS)
        for x in excluded: inv.append([x[k] for k in ("Designator", "Model", "Footprint", "Reason", "ConfirmedBy", "ConfirmedDate")])
    for c, w in enumerate([24, 12, 10, 12, 10, 12, 10, 10, 14, 14, 10, 24, 40], 1): inv.column_dimensions[get_column_letter(c)].width = w
    style_range(inv, 1, end_audit, 13)
    if excluded: style_range(inv, end_audit + 3, inv.max_row, 6)
    inv.freeze_panes = "A2"
    wb.save(path)


def verify_readback(rows, audit, excluded, path: Path):
    wb = load_workbook(path, data_only=False)
    if wb.sheetnames != ["焊接清单", "备料核对"]: raise ValidationError("工作表不符合固定输出")
    ws = wb["焊接清单"]
    if [c.value for c in ws[1]] != HEADERS: raise ValidationError("焊接清单表头错误")
    for i, r in enumerate(rows, 2):
        expected = [r["Designators"], r["Spec"], r["Package"], r["Quantity"], r["SMDPoints"], r["THTPoints"], r["Notes"] or None, r["PurchaseStatus"] or None]
        if [ws.cell(i, c).value for c in range(1, 9)] != expected: raise ValidationError(f"焊接清单第 {i} 行回读不一致")
    inv = wb["备料核对"]
    if [inv.cell(1, c).value for c in range(1, 14)] != AUDIT_HEADERS: raise ValidationError("备料核对表头错误")
    if inv.max_row < len(audit) + 1: raise ValidationError("备料核对行数不足")
    for sheet, cells in ((ws, [ws["A1"], ws.cell(ws.max_row, 1)]), (inv, [inv["A1"]])):
        for cell in cells:
            if cell.fill.fill_type != "solid" or cell.fill.fgColor.rgb not in {"00FFFFFF", "FFFFFFFF"}:
                raise ValidationError(f"{sheet.title} {cell.coordinate} 未保持白底")
            if cell.font.color and cell.font.color.type == "rgb" and cell.font.color.rgb not in {"00000000", "FF000000"}:
                raise ValidationError(f"{sheet.title} {cell.coordinate} 未保持黑字")
            if not cell.alignment.wrap_text:
                raise ValidationError(f"{sheet.title} {cell.coordinate} 未启用自动换行")


def write_report(path, rows, audit, excluded, shortages, unmatched):
    smd, tht = sum(r["SMDPoints"] for r in rows), sum(r["THTPoints"] for r in rows)
    lines = ["# Soldering Table Validation Report", "", "## Result", "PASS", "", "## Summary", f"- Included component quantity: {sum(r['Quantity'] for r in rows)}", f"- Excluded BOM items with DNP evidence: {len(excluded)}", f"- SMD solder joints: {smd}", f"- THT solder joints: {tht}", f"- Total solder joints: {smd + tht}", "- Package compatibility: PASS", "- Excel read-back and fixed sheets: PASS", "", "## Shortages"]
    lines += [f"- {m}: {n}" for m, n in shortages.items()] or ["- None"]
    lines += ["", "## Procurement models not used"] + ([f"- {m}" for m in unmatched] or ["- None"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Build and verify a PCB soldering and material-preparation workbook.")
    ap.add_argument("input_dir", type=Path); ap.add_argument("output_dir", type=Path)
    args = ap.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    rows, audit, excluded, shortages, unmatched = normalize(read_csv(args.input_dir / "bom.csv", BOM_COLUMNS), read_csv(args.input_dir / "component_rules.csv", RULE_COLUMNS), read_csv(args.input_dir / "procurement.csv", PROCUREMENT_COLUMNS))
    out = args.output_dir / "soldering_table.xlsx"; write_xlsx(rows, audit, excluded, out); verify_readback(rows, audit, excluded, out)
    write_report(args.output_dir / "validation_report.md", rows, audit, excluded, shortages, unmatched)
    print(f"PASS: {sum(r['Quantity'] for r in rows)} components, {sum(shortages.values())} shortage(s) -> {out}")


if __name__ == "__main__": main()
