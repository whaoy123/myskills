#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

AD_COLUMNS = ["BoardConnector", "BoardPin", "NetName"]
PLAN_COLUMNS = ["SheetName", "Order", "Topology", "Point1Code", "Point1Node", "Point2Code", "Point2Node", "BoardEndpoint", "BoardConnector", "BoardPinHint", "NetName", "PairGroup", "CoreRole", "FanoutId", "WireType", "LabelText", "Include", "Notes"]
SIGNAL_COLUMNS = ["NetName", "SignalDefinition", "WireType", "ElectricalAttribute"]
INTERFACE_COLUMNS = ["SheetName", "BoardConnector", "BoardConnectorModel", "BoardGender", "MatingConnectorModel", "MatingGender", "TerminalModel", "MatesTo", "Point2NodeHeader", "Title", "Description"]
NORMALIZED_FIELDS = ["SheetName", "Order", "Topology", "Point1Code", "Point1Node", "Point2Code", "Point2Node", "BoardConnector", "BoardPin", "NetName", "PairGroup", "CoreRole", "FanoutId", "WireType", "SignalDefinition", "ElectricalAttribute", "LabelText", "Notes"]


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


def truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "是", "include"}


def opposite_gender(a: str, b: str) -> bool:
    aliases = {"公": "M", "公头": "M", "male": "M", "m": "M", "母": "F", "母头": "F", "female": "F", "f": "F"}
    av, bv = aliases.get(a.strip().lower()), aliases.get(b.strip().lower())
    return av in {"M", "F"} and bv in {"M", "F"} and av != bv


def build_ad_index(ad_rows: List[dict]):
    errors, by_pin = [], {}
    by_connector_net: Dict[Tuple[str, str], List[str]] = defaultdict(list)
    for r in ad_rows:
        ref, pin, net = r["BoardConnector"], r["BoardPin"], r["NetName"]
        if not all((ref, pin, net)):
            errors.append(f"ad_pin_net.csv:{r['_line']} 存在空字段")
            continue
        if (ref, pin) in by_pin and by_pin[(ref, pin)] != net:
            errors.append(f"AD 引脚 {ref}.{pin} 同时属于 {by_pin[(ref, pin)]} 与 {net}")
        by_pin[(ref, pin)] = net
        if pin not in by_connector_net[(ref, net)]:
            by_connector_net[(ref, net)].append(pin)
    if errors:
        raise ValidationError("\n".join(errors))
    return by_connector_net


def resolve_board_pin(r: dict, index) -> str:
    endpoint = r["BoardEndpoint"]
    if endpoint not in {"", "0", "1", "2"}:
        raise ValidationError(f"connection_plan.csv:{r['_line']} BoardEndpoint 只能是 0/1/2")
    if endpoint in {"", "0"}:
        if r["BoardConnector"] or r["BoardPinHint"]:
            raise ValidationError(f"connection_plan.csv:{r['_line']} 非板端行不得填写 BoardConnector/BoardPinHint")
        return ""
    if not r["BoardConnector"] or not r["NetName"]:
        raise ValidationError(f"connection_plan.csv:{r['_line']} 板端行必须填写 BoardConnector 和 NetName")
    candidates = index.get((r["BoardConnector"], r["NetName"]), [])
    hint = r["BoardPinHint"]
    if hint:
        if hint not in candidates:
            raise ValidationError(f"connection_plan.csv:{r['_line']} BoardPinHint={hint} 与 AD 候选 {candidates} 不一致")
        pin = hint
    elif len(candidates) == 1:
        pin = candidates[0]
    elif not candidates:
        raise ValidationError(f"connection_plan.csv:{r['_line']} 无法在 AD 中找到 {r['BoardConnector']}/{r['NetName']}")
    else:
        raise ValidationError(f"connection_plan.csv:{r['_line']} {r['BoardConnector']}/{r['NetName']} 对应多个 pin {candidates}，必须填写 BoardPinHint")
    node_field = f"Point{endpoint}Node"
    if r[node_field] and r[node_field] != pin:
        raise ValidationError(f"connection_plan.csv:{r['_line']} {node_field}={r[node_field]} 与 AD 求得 pin={pin} 不一致")
    r[node_field] = pin
    return pin


def validate_topology(rows: List[dict]) -> None:
    errors, endpoints, pairs = [], defaultdict(list), defaultdict(list)
    for r in rows:
        endpoints[(r["Point1Code"], r["Point1Node"])].append(r)
        endpoints[(r["Point2Code"], r["Point2Node"])].append(r)
        if r["Topology"] == "twisted_pair":
            if not r["PairGroup"]:
                errors.append(f"{r['SheetName']} Order={r['Order']} 双绞线缺少 PairGroup")
            pairs[(r["SheetName"], r["PairGroup"])].append(r)
        elif r["PairGroup"]:
            errors.append(f"{r['SheetName']} Order={r['Order']} direct 不应填写 PairGroup")
    for endpoint, uses in endpoints.items():
        if len(uses) > 1:
            ids = {r["FanoutId"] for r in uses}
            if "" in ids or len(ids) != 1:
                errors.append(f"端点 {endpoint[0]}.{endpoint[1]} 重复使用，必须用同一个 FanoutId 显式声明多对一/一对多")
    for (sheet, group), members in pairs.items():
        roles = Counter(r["CoreRole"] for r in members)
        if len(members) != 2 or roles != Counter({"signal": 1, "return": 1}):
            errors.append(f"{sheet} 双绞组 {group} 必须恰好包含一根 signal 和一根 return")
            continue
        orders = sorted(r["Order"] for r in members)
        if orders[1] != orders[0] + 1:
            errors.append(f"{sheet} 双绞组 {group} 的两根线必须相邻排列")
        signal = next(r for r in members if r["CoreRole"] == "signal")
        ret = next(r for r in members if r["CoreRole"] == "return")
        signal["LabelText"] = signal["LabelText"] or signal["NetName"]
        ret["LabelText"] = ret["LabelText"] or f"{signal['NetName']}-GND"
        ret["Notes"] = "；".join(x for x in (ret["Notes"], f"与 {signal['NetName']} 配对") if x)
    for r in rows:
        r["LabelText"] = r["LabelText"] or r["NetName"]
    if errors:
        raise ValidationError("\n".join(errors))


def build_normalized(ad_rows, plan_rows, signal_rows, interface_rows):
    index, errors, warnings = build_ad_index(ad_rows), [], []
    signals, interfaces = {}, {}
    for r in signal_rows:
        if not r["NetName"] or r["NetName"] in signals:
            errors.append(f"signal_catalog.csv:{r['_line']} NetName 为空或重复: {r['NetName']}")
        signals[r["NetName"]] = r
    for r in interface_rows:
        if not r["SheetName"] or r["SheetName"] in interfaces:
            errors.append(f"interface_catalog.csv:{r['_line']} SheetName 为空或重复: {r['SheetName']}")
        if r["BoardGender"] or r["MatingGender"]:
            if not opposite_gender(r["BoardGender"], r["MatingGender"]):
                errors.append(f"interface_catalog.csv:{r['_line']} 板端与对插连接器公母关系不成立")
        if r["Point2NodeHeader"] not in {"节点号", "端子号"}:
            errors.append(f"interface_catalog.csv:{r['_line']} Point2NodeHeader 只能是 节点号 或 端子号")
        interfaces[r["SheetName"]] = r
    normalized, sheet_order, order_seen = [], [], set()
    for r in plan_rows:
        if not truthy(r["Include"]):
            continue
        if not all((r["SheetName"], r["Order"], r["Point1Code"], r["Point2Code"], r["NetName"])):
            errors.append(f"connection_plan.csv:{r['_line']} SheetName/Order/两端代号/NetName 不能为空")
            continue
        try:
            order = int(r["Order"])
            if order <= 0:
                raise ValueError
        except ValueError:
            errors.append(f"connection_plan.csv:{r['_line']} Order 必须为正整数")
            continue
        if (r["SheetName"], order) in order_seen:
            errors.append(f"{r['SheetName']} 中 Order 重复: {order}")
        order_seen.add((r["SheetName"], order))
        if r["SheetName"] not in sheet_order:
            sheet_order.append(r["SheetName"])
        if r["SheetName"] not in interfaces:
            errors.append(f"connection_plan.csv:{r['_line']} SheetName 未在 interface_catalog.csv 定义")
        topology = r["Topology"].lower()
        role = r["CoreRole"].lower() or "normal"
        if topology not in {"direct", "twisted_pair"}:
            errors.append(f"connection_plan.csv:{r['_line']} Topology 只能是 direct 或 twisted_pair")
            continue
        if topology == "twisted_pair" and role not in {"signal", "return"}:
            errors.append(f"connection_plan.csv:{r['_line']} 双绞线 CoreRole 必须是 signal 或 return")
        sig = signals.get(r["NetName"])
        if sig is None:
            errors.append(f"connection_plan.csv:{r['_line']} 网络 {r['NetName']} 未在 signal_catalog.csv 定义")
            continue
        try:
            board_pin = resolve_board_pin(r, index)
        except ValidationError as exc:
            errors.append(str(exc))
            continue
        if r["BoardEndpoint"] in {"1", "2"} and r["SheetName"] in interfaces:
            expected_code = interfaces[r["SheetName"]]["MatingConnectorModel"]
            actual_code = r[f"Point{r['BoardEndpoint']}Code"]
            if expected_code and actual_code != expected_code:
                errors.append(f"connection_plan.csv:{r['_line']} 板端对插侧代号 {actual_code} 与接口表型号 {expected_code} 不一致")
        if not r["Point1Node"] or not r["Point2Node"]:
            errors.append(f"connection_plan.csv:{r['_line']} 两端节点号必须明确；板端节点可由 AD 自动填充")
            continue
        normalized.append({"SheetName": r["SheetName"], "Order": order, "Topology": topology, "Point1Code": r["Point1Code"], "Point1Node": r["Point1Node"], "Point2Code": r["Point2Code"], "Point2Node": r["Point2Node"], "BoardConnector": r["BoardConnector"], "BoardPin": board_pin, "NetName": r["NetName"], "PairGroup": r["PairGroup"], "CoreRole": role, "FanoutId": r["FanoutId"], "WireType": r["WireType"] or sig["WireType"], "SignalDefinition": sig["SignalDefinition"] or r["NetName"], "ElectricalAttribute": sig["ElectricalAttribute"], "LabelText": r["LabelText"], "Notes": r["Notes"]})
    if errors:
        raise ValidationError("\n".join(errors))
    normalized.sort(key=lambda x: (sheet_order.index(x["SheetName"]), x["Order"]))
    validate_topology(normalized)
    return normalized, sheet_order, interfaces, warnings


def write_normalized_csv(rows, path: Path):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=NORMALIZED_FIELDS)
        writer.writeheader(); writer.writerows(rows)


def row_remark(r: dict) -> str:
    parts = [r["NetName"], r["SignalDefinition"], r["ElectricalAttribute"], r["Notes"], f"标签：{r['LabelText']}"]
    return "；".join(dict.fromkeys(p for p in parts if p))


def apply_style(ws, max_row: int, max_col: int, bold_rows):
    side, white = Side(style="thin", color="000000"), PatternFill("solid", fgColor="FFFFFF")
    for row in ws.iter_rows(min_row=1, max_row=max_row, min_col=1, max_col=max_col):
        for cell in row:
            cell.fill = white
            cell.font = Font(name="Arial", size=10, color="000000", bold=cell.row in bold_rows)
            cell.alignment = Alignment(horizontal="center" if cell.column != max_col else "left", vertical="center", wrap_text=True)
            cell.border = Border(left=side, right=side, top=side, bottom=side)
    for idx in range(1, max_row + 1):
        text_len = max((len(str(ws.cell(idx, c).value or "")) for c in range(1, max_col + 1)), default=0)
        ws.row_dimensions[idx].height = max(22, 15 * ((text_len // 42) + 1))


def write_xlsx(rows, sheet_order, interfaces, path: Path):
    wb = Workbook(); wb.remove(wb.active)
    for sheet in sheet_order:
        meta, ws = interfaces[sheet], wb.create_sheet(sheet[:31])
        ws.merge_cells("A1:G1")
        ws["A1"] = meta["Title"] or f"{meta['BoardConnector']}（{meta['BoardConnectorModel']}）对插 {meta['MatingConnectorModel']} 接线"
        ws.merge_cells("A2:A3"); ws["A2"] = "序号"
        ws.merge_cells("B2:C2"); ws["B2"] = "连接点1"
        ws.merge_cells("D2:E2"); ws["D2"] = "连接点2"
        ws.merge_cells("F2:F3"); ws["F2"] = "线型"
        ws.merge_cells("G2:G3"); ws["G2"] = "备注/标签"
        ws["B3"], ws["C3"], ws["D3"], ws["E3"] = "代号", "节点号", "代号", meta["Point2NodeHeader"]
        body = [r for r in rows if r["SheetName"] == sheet]
        for idx, r in enumerate(body, 1):
            ws.append([idx, r["Point1Code"], r["Point1Node"], r["Point2Code"], r["Point2Node"], r["WireType"], row_remark(r)])
        for col, width in enumerate([8, 20, 12, 20, 12, 12, 48], 1):
            ws.column_dimensions[get_column_letter(col)].width = width
        apply_style(ws, 3 + len(body), 7, {1, 2, 3}); ws.freeze_panes = "A4"
    ws = wb.create_sheet("接口与端子")
    ws.append(["线束/工作表", "板端接口", "板端型号", "板端公母", "对插连接器", "对插公母", "自由端端子", "对接对象/说明"])
    for sheet in sheet_order:
        m = interfaces[sheet]
        ws.append([sheet, m["BoardConnector"], m["BoardConnectorModel"], m["BoardGender"], m["MatingConnectorModel"], m["MatingGender"], m["TerminalModel"] or "待下游接口确认", "；".join(x for x in (m["MatesTo"], m["Description"]) if x)])
    for col, width in enumerate([16, 14, 18, 12, 20, 12, 20, 40], 1):
        ws.column_dimensions[get_column_letter(col)].width = width
    apply_style(ws, ws.max_row, 8, {1}); ws.freeze_panes = "A2"
    wb.save(path)


def verify_readback(rows, sheet_order, path: Path):
    wb = load_workbook(path, data_only=False)
    if wb.sheetnames != [s[:31] for s in sheet_order] + ["接口与端子"]:
        raise ValidationError(f"工作表顺序错误: {wb.sheetnames}")
    for sheet in sheet_order:
        ws = wb[sheet[:31]]
        if [ws["A2"].value, ws["B2"].value, ws["D2"].value, ws["G2"].value] != ["序号", "连接点1", "连接点2", "备注/标签"]:
            raise ValidationError(f"{sheet} 表头不符合固定版式")
        for idx, r in enumerate([x for x in rows if x["SheetName"] == sheet], 4):
            got = [ws.cell(idx, c).value for c in range(2, 8)]
            want = [r["Point1Code"], r["Point1Node"], r["Point2Code"], r["Point2Node"], r["WireType"] or None, row_remark(r)]
            if got != want:
                raise ValidationError(f"{sheet} 第 {idx} 行 Excel 回读不一致")
        for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=7):
            for cell in row:
                if cell.value is None:
                    continue
                if cell.fill.fill_type != "solid" or cell.fill.fgColor.rgb not in {"00FFFFFF", "FFFFFFFF"}:
                    raise ValidationError(f"{sheet} {cell.coordinate} 未保持白底")
                if cell.font.color and cell.font.color.type == "rgb" and cell.font.color.rgb not in {"00000000", "FF000000"}:
                    raise ValidationError(f"{sheet} {cell.coordinate} 未保持黑字")
                if not cell.alignment.wrap_text:
                    raise ValidationError(f"{sheet} {cell.coordinate} 未启用自动换行")


def write_report(path: Path, rows, warnings):
    pairs = len({(r["SheetName"], r["PairGroup"]) for r in rows if r["PairGroup"]})
    fanouts = len({r["FanoutId"] for r in rows if r["FanoutId"]})
    lines = ["# Wiring Table Validation Report", "", "## Result", "PASS", "", "## Summary", f"- Conductors: {len(rows)}", f"- Twisted-pair groups: {pairs}", f"- Declared fanout groups: {fanouts}", "- Board pins resolved from AD where BoardEndpoint=1/2: PASS", "- Topology and endpoint uniqueness: PASS", "- Excel layout/style/read-back: PASS", "", "## Warnings"]
    lines.extend([f"- {w}" for w in warnings] or ["- None"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Build and verify a topology-aware connector wiring table.")
    ap.add_argument("input_dir", type=Path); ap.add_argument("output_dir", type=Path)
    args = ap.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    rows, sheets, interfaces, warnings = build_normalized(read_csv(args.input_dir / "ad_pin_net.csv", AD_COLUMNS), read_csv(args.input_dir / "connection_plan.csv", PLAN_COLUMNS), read_csv(args.input_dir / "signal_catalog.csv", SIGNAL_COLUMNS), read_csv(args.input_dir / "interface_catalog.csv", INTERFACE_COLUMNS))
    write_normalized_csv(rows, args.output_dir / "normalized_connections.csv")
    xlsx = args.output_dir / "wiring_table.xlsx"; write_xlsx(rows, sheets, interfaces, xlsx); verify_readback(rows, sheets, xlsx)
    write_report(args.output_dir / "validation_report.md", rows, warnings)
    print(f"PASS: {len(rows)} conductors -> {xlsx}")


if __name__ == "__main__":
    main()
