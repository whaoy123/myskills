#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

from artifact_tool import Blob, SpreadsheetFile, Workbook

BOM_COLUMNS = [
    "Designator",
    "Nominal",
    "ResolvedDescription",
    "Footprint",
    "DesignModel",
    "FinalModel",
]
RULE_COLUMNS = [
    "MatchField",
    "MatchValue",
    "DisplayPackage",
    "MountType",
    "PinsPerPart",
    "FixedPinsPerPart",
    "Include",
    "Notes",
]
PROCUREMENT_COLUMNS = ["Model", "PurchasedQty", "ReceivedQty", "Source", "Notes"]
HEADERS = ["位号", "型号/规格", "封装/类型", "数量", "贴片焊点", "直插焊点", "备注", "补购状态"]


class ValidationError(RuntimeError):
    pass


def read_csv(path: Path, required: List[str]) -> List[dict]:
    if not path.exists():
        raise ValidationError(f"缺少输入文件: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        missing = [c for c in required if c not in fields]
        if missing:
            raise ValidationError(f"{path.name} 缺少列: {', '.join(missing)}")
        rows = []
        for lineno, row in enumerate(reader, start=2):
            clean = {k: (v or "").strip() for k, v in row.items()}
            if any(clean.get(c, "") for c in required):
                clean["_line"] = lineno
                rows.append(clean)
        return rows


def truthy(v: str) -> bool:
    return v.strip().lower() in {"1", "true", "yes", "y", "是", "include"}


def to_int(v: str, what: str, allow_blank: bool = False):
    if v == "" and allow_blank:
        return None
    try:
        n = int(v)
    except ValueError:
        raise ValidationError(f"{what} 必须为整数，实际为 {v!r}")
    if n < 0:
        raise ValidationError(f"{what} 不能为负数")
    return n


def natural_designator_key(s: str):
    m = re.fullmatch(r"([A-Za-z]+)(\d+)", s.strip())
    if m:
        return (m.group(1).upper(), int(m.group(2)))
    return (s.upper(), 0)


def build_rule_index(rule_rows: List[dict]):
    idx: Dict[Tuple[str, str], dict] = {}
    for r in rule_rows:
        field = r["MatchField"]
        if field not in {"Model", "Footprint"}:
            raise ValidationError(
                f"component_rules.csv:{r['_line']} MatchField 只能是 Model 或 Footprint"
            )
        if not r["MatchValue"]:
            raise ValidationError(f"component_rules.csv:{r['_line']} MatchValue 为空")
        key = (field, r["MatchValue"])
        if key in idx:
            raise ValidationError(
                f"component_rules.csv 规则重复: {field}={r['MatchValue']}"
            )
        mount = r["MountType"].upper()
        if mount not in {"SMD", "THT", "NONE"}:
            raise ValidationError(
                f"{field}={r['MatchValue']} 的 MountType 必须是 SMD/THT/NONE"
            )
        r["_pins"] = to_int(
            r["PinsPerPart"], f"{field}={r['MatchValue']} PinsPerPart"
        )
        r["_fixed"] = to_int(
            r["FixedPinsPerPart"], f"{field}={r['MatchValue']} FixedPinsPerPart"
        )
        r["_mount"] = mount
        idx[key] = r
    return idx


def find_rule(row: dict, idx: Dict[Tuple[str, str], dict]) -> dict:
    # Model 规则匹配的是最终实际型号，而不是原设计型号。
    for field, value in (
        ("Model", row["FinalModel"]),
        ("Footprint", row["Footprint"]),
    ):
        rule = idx.get((field, value))
        if rule:
            return rule
    raise ValidationError(
        f"bom.csv:{row['_line']} {row['Designator']} "
        f"({row['FinalModel']} / {row['Footprint']}) 没有匹配 component_rules.csv"
    )


def normalize_spec(nominal: str, description: str, final_model: str) -> str:
    """生成简洁的“型号/规格”，删除重复的容值/阻值/电感值开头。"""
    nominal = nominal.strip()
    final_model = final_model.strip()
    raw = (description or "").replace("；", ";")
    parts = [p.strip() for p in raw.split(";") if p.strip()]
    cleaned = []

    duplicate_value_keys = {"容值", "阻值", "电感值", "标称值/名称"}
    model_keys = {"具体型号", "型号", "料号", "LibRef"}

    for part in parts:
        if part == nominal:
            continue
        m = re.match(r"^([^:：]+)[:：]\s*(.*)$", part)
        if m:
            key, value = m.group(1).strip(), m.group(2).strip()
            if key in model_keys:
                continue
            if key in duplicate_value_keys and value == nominal:
                continue
        cleaned.append(part)

    out = []
    if nominal:
        out.append(nominal)
    out.extend(cleaned)
    if final_model:
        out.append(f"具体型号：{final_model}")
    return "；".join(out)


def read_procurement(rows: List[dict]):
    evidence = {}
    fallback_to_purchased = []
    for r in rows:
        model = r["Model"]
        if not model:
            raise ValidationError(f"procurement.csv:{r['_line']} Model 为空")
        if model in evidence:
            raise ValidationError(
                f"procurement.csv 型号重复: {model}。采购表与发票必须先去重后再写入。"
            )
        purchased = to_int(
            r["PurchasedQty"], f"procurement.csv:{r['_line']} PurchasedQty"
        )
        received = to_int(
            r["ReceivedQty"],
            f"procurement.csv:{r['_line']} ReceivedQty",
            allow_blank=True,
        )
        available = received if received is not None else purchased
        if received is None:
            fallback_to_purchased.append(model)
        evidence[model] = {
            "purchased": purchased,
            "received": received,
            "available": available,
            "source": r["Source"],
            "notes": r["Notes"],
        }
    return evidence, fallback_to_purchased


def normalize(bom_rows: List[dict], rule_rows: List[dict], procurement_rows: List[dict]):
    idx = build_rule_index(rule_rows)
    procurement, fallback_to_purchased = read_procurement(procurement_rows)

    seen = set()
    groups = defaultdict(lambda: {"designators": []})
    excluded = 0
    required_models = defaultdict(int)

    for r in bom_rows:
        d = r["Designator"]
        if not d:
            raise ValidationError(f"bom.csv:{r['_line']} Designator 为空")
        if d in seen:
            raise ValidationError(f"BOM 位号重复: {d}")
        seen.add(d)

        if not r["FinalModel"]:
            raise ValidationError(f"bom.csv:{r['_line']} {d} 的 FinalModel 为空")

        rule = find_rule(r, idx)
        if not truthy(rule["Include"]) or rule["_mount"] == "NONE":
            excluded += 1
            continue

        spec = normalize_spec(
            r["Nominal"], r["ResolvedDescription"], r["FinalModel"]
        )
        package = rule["DisplayPackage"] or r["Footprint"]
        key = (
            r["FinalModel"],
            spec,
            package,
            rule["_mount"],
            rule["_pins"],
            rule["_fixed"],
            rule["Notes"],
        )
        g = groups[key]
        g.update(
            {
                "model": r["FinalModel"],
                "spec": spec,
                "package": package,
                "mount": rule["_mount"],
                "pins": rule["_pins"],
                "fixed": rule["_fixed"],
                "notes": rule["Notes"],
            }
        )
        g["designators"].append(d)
        required_models[r["FinalModel"]] += 1

    rows = []
    for g in groups.values():
        ds = sorted(g["designators"], key=natural_designator_key)
        qty = len(ds)
        per_part = g["pins"] + g["fixed"]
        smd = qty * per_part if g["mount"] == "SMD" else 0
        tht = qty * per_part if g["mount"] == "THT" else 0
        notes = g["notes"]
        if g["fixed"] and "固定脚" not in notes:
            extra = f"每只含{g['fixed']}个固定脚"
            notes = f"{notes}；{extra}" if notes else extra
        rows.append(
            {
                "Designators": ", ".join(ds),
                "Model": g["model"],
                "Spec": g["spec"],
                "Package": g["package"],
                "Quantity": qty,
                "SMDPoints": smd,
                "THTPoints": tht,
                "Notes": notes,
                "PurchaseStatus": "",
                "ShortageQty": 0,
            }
        )

    rows.sort(key=lambda x: natural_designator_key(x["Designators"].split(",")[0]))

    # 对同一最终型号的采购数量只使用一次，并按清单顺序分配。
    remaining = {
        model: info["available"] for model, info in procurement.items()
    }
    shortages = defaultdict(int)
    for r in rows:
        available = remaining.get(r["Model"], 0)
        covered = min(available, r["Quantity"])
        shortage = r["Quantity"] - covered
        remaining[r["Model"]] = max(available - covered, 0)
        if shortage:
            r["ShortageQty"] = shortage
            r["PurchaseStatus"] = f"待补购 {shortage}只"
            shortages[r["Model"]] += shortage

    unmatched_procurement = sorted(set(procurement) - set(required_models))
    return (
        rows,
        excluded,
        shortages,
        unmatched_procurement,
        fallback_to_purchased,
    )


def style_sheet(ws, max_row: int):
    all_rng = ws.get_range(f"A1:H{max_row}")
    all_rng.format.wrap_text = True
    all_rng.format.vertical_alignment = "center"
    all_rng.format.font = {"color": "#000000", "size": 10}
    all_rng.format.borders = {
        "top": {"style": "thin", "color": "#808080"},
        "bottom": {"style": "thin", "color": "#808080"},
        "left": {"style": "thin", "color": "#808080"},
        "right": {"style": "thin", "color": "#808080"},
        "insideHorizontal": {"style": "thin", "color": "#BFBFBF"},
        "insideVertical": {"style": "thin", "color": "#BFBFBF"},
    }

    header = ws.get_range("A1:H1")
    header.format.fill = "#E7E6E6"
    header.format.font = {"bold": True, "color": "#000000", "size": 10}
    header.format.horizontal_alignment = "center"

    total = ws.get_range(f"A{max_row}:H{max_row}")
    total.format.fill = "#E7E6E6"
    total.format.font = {"bold": True, "color": "#000000", "size": 10}

    ws.get_range(f"D2:H{max_row}").format.horizontal_alignment = "center"
    ws.get_range("A:A").format.column_width = 30
    ws.get_range("B:B").format.column_width = 64
    ws.get_range("C:C").format.column_width = 26
    ws.get_range("D:F").format.column_width = 11
    ws.get_range("G:G").format.column_width = 24
    ws.get_range("H:H").format.column_width = 14
    ws.get_range(f"A1:H{max_row}").format.autofit_rows()
    ws.freeze_panes.freeze_rows(1)


def write_xlsx(rows: List[dict], path: Path):
    wb = Workbook.create()
    ws = wb.worksheets.add("焊接清单")
    ws.get_range("A1:H1").values = [HEADERS]

    body = [
        [
            r["Designators"],
            r["Spec"],
            r["Package"],
            r["Quantity"],
            r["SMDPoints"],
            r["THTPoints"],
            r["Notes"],
            r["PurchaseStatus"],
        ]
        for r in rows
    ]
    if body:
        ws.get_range(f"A2:H{len(body) + 1}").values = body

    total_row = len(body) + 2
    ws.merge_cells(f"A{total_row}:C{total_row}")
    ws.get_range(f"A{total_row}").values = [["合计"]]

    qty = sum(r["Quantity"] for r in rows)
    smd = sum(r["SMDPoints"] for r in rows)
    tht = sum(r["THTPoints"] for r in rows)
    ws.get_range(f"D{total_row}:H{total_row}").values = [
        [qty, smd, tht, f"总焊点：{smd + tht}", ""]
    ]

    style_sheet(ws, total_row)

    for i, r in enumerate(rows, start=2):
        if r["ShortageQty"] > 0:
            ws.get_range(f"A{i}:H{i}").format.fill = "#FFF2CC"

    SpreadsheetFile.export_xlsx(wb).save(str(path))


def verify_readback(rows: List[dict], path: Path):
    wb = SpreadsheetFile.import_xlsx(Blob.load(str(path)))
    max_row = len(rows) + 2
    inspected = wb.inspect(
        {
            "kind": "table",
            "range": f"焊接清单!A1:H{max_row}",
            "include": "values,formulas",
            "table_max_rows": max_row,
            "table_max_cols": 8,
        }
    )
    data = json.loads(inspected.ndjson)["values"]

    expected_body = [
        [
            r["Designators"],
            r["Spec"],
            r["Package"],
            r["Quantity"],
            r["SMDPoints"],
            r["THTPoints"],
            r["Notes"] or None,
            r["PurchaseStatus"] or None,
        ]
        for r in rows
    ]
    got_body = data[1 : 1 + len(rows)]
    if got_body != expected_body:
        raise ValidationError("生成后的 Excel 回读结果与脚本计算结果不一致")

    total = data[-1]
    expected = (
        sum(r["Quantity"] for r in rows),
        sum(r["SMDPoints"] for r in rows),
        sum(r["THTPoints"] for r in rows),
    )
    if (int(total[3]), int(total[4]), int(total[5])) != expected:
        raise ValidationError("Excel 合计行与脚本计算结果不一致")

    errors = wb.inspect(
        {
            "kind": "match",
            "search_term": "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
            "options": {"use_regex": True, "max_results": 100},
            "summary": "formula error scan",
        }
    )
    if "matched 0" not in errors.ndjson and "0 entries" not in errors.ndjson:
        raise ValidationError("Excel 中发现公式错误")


def write_report(
    path: Path,
    rows: List[dict],
    excluded: int,
    shortages: Dict[str, int],
    unmatched_procurement: List[str],
    fallback_to_purchased: List[str],
):
    qty = sum(r["Quantity"] for r in rows)
    smd = sum(r["SMDPoints"] for r in rows)
    tht = sum(r["THTPoints"] for r in rows)

    shortage_lines = (
        "\n".join(f"- {m}: 待补购 {n}只" for m, n in sorted(shortages.items()))
        if shortages
        else "- 无"
    )
    unmatched_lines = (
        "\n".join(f"- {m}" for m in unmatched_procurement)
        if unmatched_procurement
        else "- 无"
    )
    fallback_lines = (
        "\n".join(f"- {m}" for m in fallback_to_purchased)
        if fallback_to_purchased
        else "- 无"
    )

    path.write_text(
        f"""# Soldering Table Validation Report

## Result
PASS

## Summary
- Included component quantity: {qty}
- Excluded BOM items: {excluded}
- SMD solder joints: {smd}
- THT solder joints: {tht}
- Total solder joints: {smd + tht}
- Excel read-back match: PASS

## Shortages
{shortage_lines}

## Procurement models not used by this PCB
{unmatched_lines}

## Models using PurchasedQty because ReceivedQty was blank
{fallback_lines}
""",
        encoding="utf-8",
    )


def main():
    ap = argparse.ArgumentParser(
        description="Build and verify a PCB soldering table with procurement shortage status."
    )
    ap.add_argument("input_dir", type=Path)
    ap.add_argument("output_dir", type=Path)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    bom = read_csv(args.input_dir / "bom.csv", BOM_COLUMNS)
    rules = read_csv(args.input_dir / "component_rules.csv", RULE_COLUMNS)
    procurement = read_csv(
        args.input_dir / "procurement.csv", PROCUREMENT_COLUMNS
    )

    (
        rows,
        excluded,
        shortages,
        unmatched_procurement,
        fallback_to_purchased,
    ) = normalize(bom, rules, procurement)

    out = args.output_dir / "soldering_table.xlsx"
    write_xlsx(rows, out)
    verify_readback(rows, out)
    write_report(
        args.output_dir / "validation_report.md",
        rows,
        excluded,
        shortages,
        unmatched_procurement,
        fallback_to_purchased,
    )

    shortage_total = sum(shortages.values())
    print(
        f"PASS: {sum(r['Quantity'] for r in rows)} components, "
        f"{shortage_total} shortage(s) -> {out}"
    )


if __name__ == "__main__":
    main()
