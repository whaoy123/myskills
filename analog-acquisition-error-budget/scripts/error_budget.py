#!/usr/bin/env python3
"""Normalize and combine analog acquisition error sources.

Input is JSON. The script intentionally uses a small, explicit schema so every
number remains auditable. Complex datasheet specifications should first be
translated into one of the supported spec types.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List


SUPPORTED_SPEC_TYPES = {
    "percent_reading",
    "ppm_reading",
    "ppm_per_c_reading",
    "local_offset_v",
    "local_offset_uv_per_c",
    "percent_full_scale",
    "lsb",
    "local_noise_rms_v",
    "input_referred_v",
    "input_referred_percent",
    "current_times_resistance",
    "cmrr_db",
    "psrr_db",
    "first_order_lowpass_attenuation",
    "jitter_rms_s",
}


@dataclass
class NormalizedSource:
    name: str
    component: str
    spec_type: str
    combination: str
    calibration_class: str
    basis: str
    raw_input_error: float
    input_error: float
    formula: str
    notes: str
    retained_after_calibration: bool


def _require_number(value: Any, field: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{field} must be a number")
    if not math.isfinite(float(value)):
        raise ValueError(f"{field} must be finite")
    return float(value)


def _node_gain(measurement: Dict[str, Any], node: str) -> float:
    nodes = measurement.get("nodes", {})
    if node not in nodes:
        raise ValueError(f"unknown node {node!r}; define it in measurement.nodes")
    gain = _require_number(nodes[node], f"measurement.nodes.{node}")
    if gain == 0:
        raise ValueError(f"node gain for {node!r} cannot be zero")
    return abs(gain)


def _adc_lsb(measurement: Dict[str, Any]) -> float:
    adc = measurement.get("adc")
    if not isinstance(adc, dict):
        raise ValueError("measurement.adc is required for spec_type=lsb")
    bits = int(_require_number(adc.get("bits"), "measurement.adc.bits"))
    span = _require_number(adc.get("input_span_v"), "measurement.adc.input_span_v")
    if bits <= 0 or span <= 0:
        raise ValueError("ADC bits and input span must be positive")
    return span / (2 ** bits)


def _calibration_removes(mode: str, calibration_class: str) -> bool:
    mode = mode.lower()
    calibration_class = calibration_class.lower()
    if calibration_class in {"none", ""}:
        return False
    if mode == "none":
        return False
    if mode == "zero":
        return calibration_class == "offset"
    if mode == "gain":
        return calibration_class == "gain"
    if mode in {"two_point", "offset_and_gain"}:
        return calibration_class in {"offset", "gain", "both"}
    raise ValueError(f"unsupported calibration_mode: {mode}")


def _apply_result_algorithm(measurement: Dict[str, Any], source: Dict[str, Any], raw_error: float, spec_type: str) -> tuple[float, str]:
    """Translate a physical input-referred error into error of the reported metric.

    Fixed DC offsets do not map linearly into an RMS result. The source may set
    error_role explicitly; local offset and leakage-current types default to offset.
    """
    role = str(source.get("error_role", "")).lower()
    if not role:
        role = "offset" if spec_type in {"local_offset_v", "local_offset_uv_per_c", "current_times_resistance"} else "other"
    if role != "offset":
        return raw_error, "direct"
    algorithm = str(measurement.get("result_algorithm", "direct")).lower()
    x = abs(_require_number(measurement.get("value"), "measurement.value"))
    if algorithm == "direct":
        return raw_error, "direct offset effect"
    if algorithm == "rms_mean_removed":
        return 0.0, "fixed offset removed before RMS"
    if algorithm == "rms_raw_zero_mean_signal":
        return math.sqrt(x * x + raw_error * raw_error) - x, "sqrt(X²+offset²)-X"
    raise ValueError(f"unsupported result_algorithm: {algorithm}")


def normalize_source(measurement: Dict[str, Any], source: Dict[str, Any]) -> NormalizedSource:
    name = str(source.get("name", "unnamed source"))
    component = str(source.get("component", "unspecified"))
    spec_type = str(source.get("spec_type", ""))
    if spec_type not in SUPPORTED_SPEC_TYPES:
        raise ValueError(f"{name}: unsupported spec_type {spec_type!r}")
    combination = str(source.get("combination", "systematic")).lower()
    if combination not in {"systematic", "random"}:
        raise ValueError(f"{name}: combination must be systematic or random")
    calibration_class = str(source.get("calibration_class", "none")).lower()
    if calibration_class not in {"none", "offset", "gain", "both"}:
        raise ValueError(f"{name}: invalid calibration_class")
    basis = str(source.get("basis", "unspecified"))
    notes = str(source.get("notes", ""))
    x = abs(_require_number(measurement.get("value"), "measurement.value"))
    dt = abs(
        _require_number(measurement.get("temperature_operating_c", 25.0), "temperature_operating_c")
        - _require_number(measurement.get("temperature_reference_c", 25.0), "temperature_reference_c")
    )
    value = abs(_require_number(source.get("value", 0.0), f"{name}.value"))
    node = str(source.get("node", "system_input"))
    gain = _node_gain(measurement, node)

    if spec_type == "percent_reading":
        err = x * value / 100.0
        formula = f"{x:g} × {value:g}%"
    elif spec_type == "ppm_reading":
        err = x * value * 1e-6
        formula = f"{x:g} × {value:g} ppm"
    elif spec_type == "ppm_per_c_reading":
        err = x * value * 1e-6 * dt
        formula = f"{x:g} × {value:g} ppm/°C × {dt:g}°C"
    elif spec_type == "local_offset_v":
        err = value / gain
        formula = f"{value:g} V at {node} ÷ {gain:g}"
    elif spec_type == "local_offset_uv_per_c":
        local = value * 1e-6 * dt
        err = local / gain
        formula = f"{value:g} µV/°C × {dt:g}°C ÷ {gain:g}"
    elif spec_type == "percent_full_scale":
        fs = abs(_require_number(source.get("full_scale_input", measurement.get("full_scale_input")), f"{name}.full_scale_input"))
        err = fs * value / 100.0
        formula = f"{fs:g} full-scale × {value:g}%FS"
    elif spec_type == "lsb":
        lsb = _adc_lsb(measurement)
        err = value * lsb / gain
        formula = f"{value:g} LSB × {lsb:g} V/LSB ÷ {gain:g}"
    elif spec_type == "local_noise_rms_v":
        err = value / gain
        formula = f"{value:g} V RMS at {node} ÷ {gain:g}"
    elif spec_type == "input_referred_v":
        err = value
        formula = f"already input-referred: {value:g}"
    elif spec_type == "input_referred_percent":
        err = x * value / 100.0
        formula = f"input-referred {value:g}% × {x:g}"
    elif spec_type == "current_times_resistance":
        current_a = abs(_require_number(source.get("current_a", value), f"{name}.current_a"))
        resistance = abs(_require_number(source.get("resistance_ohm"), f"{name}.resistance_ohm"))
        local = current_a * resistance
        err = local / gain
        formula = f"{current_a:g} A × {resistance:g} Ω ÷ {gain:g}"
    elif spec_type == "cmrr_db":
        stimulus = abs(_require_number(source.get("stimulus_local_v"), f"{name}.stimulus_local_v"))
        local = stimulus / (10 ** (value / 20.0))
        err = local / gain
        formula = f"{stimulus:g} V ÷ 10^({value:g}/20) ÷ {gain:g}"
    elif spec_type == "psrr_db":
        ripple = abs(_require_number(source.get("ripple_local_v"), f"{name}.ripple_local_v"))
        local = ripple / (10 ** (value / 20.0))
        err = local / gain
        formula = f"{ripple:g} V ripple ÷ 10^({value:g}/20) ÷ {gain:g}"
    elif spec_type == "first_order_lowpass_attenuation":
        f = abs(_require_number(source.get("frequency_hz", measurement.get("frequency_hz")), f"{name}.frequency_hz"))
        fc = abs(_require_number(source.get("cutoff_hz"), f"{name}.cutoff_hz"))
        if fc == 0:
            raise ValueError(f"{name}.cutoff_hz cannot be zero")
        h = 1.0 / math.sqrt(1.0 + (f / fc) ** 2)
        err = x * abs(1.0 - h)
        formula = f"{x:g} × |1 - 1/sqrt(1+({f:g}/{fc:g})²)|"
    elif spec_type == "jitter_rms_s":
        f = abs(_require_number(source.get("frequency_hz", measurement.get("frequency_hz")), f"{name}.frequency_hz"))
        err = x * 2.0 * math.pi * f * value
        formula = f"{x:g} × 2π × {f:g} Hz × {value:g} s RMS"
    else:  # pragma: no cover
        raise AssertionError(spec_type)

    raw_err = abs(err)
    result_err, algorithm_note = _apply_result_algorithm(measurement, source, raw_err, spec_type)
    if algorithm_note != "direct":
        formula = f"{formula}; {algorithm_note}"
    mode = str(measurement.get("calibration_mode", "none"))
    retained = not _calibration_removes(mode, calibration_class)
    return NormalizedSource(
        name=name,
        component=component,
        spec_type=spec_type,
        combination=combination,
        calibration_class=calibration_class,
        basis=basis,
        raw_input_error=raw_err,
        input_error=abs(result_err),
        formula=formula,
        notes=notes,
        retained_after_calibration=retained,
    )


def summarize(measurement: Dict[str, Any], rows: List[NormalizedSource], post_calibration: bool) -> Dict[str, float]:
    selected = [r for r in rows if (r.retained_after_calibration or not post_calibration)]
    sys_values = [r.input_error for r in selected if r.combination == "systematic"]
    rnd_values = [r.input_error for r in selected if r.combination == "random"]
    systematic_wc = sum(sys_values)
    systematic_rss = math.sqrt(sum(v * v for v in sys_values))
    random_rms = math.sqrt(sum(v * v for v in rnd_values))
    k = abs(_require_number(measurement.get("random_sigma_multiplier", 3.0), "random_sigma_multiplier"))
    typical_rss = math.sqrt(systematic_rss ** 2 + random_rms ** 2)
    conservative = systematic_wc + k * random_rms
    x = abs(_require_number(measurement.get("value"), "measurement.value"))
    return {
        "systematic_worst_case": systematic_wc,
        "systematic_rss_estimate": systematic_rss,
        "random_rms": random_rms,
        "typical_combined_rss": typical_rss,
        "conservative_systematic_plus_k_sigma": conservative,
        "relative_systematic_worst_case_percent": (systematic_wc / x * 100.0) if x else math.inf,
        "relative_conservative_percent": (conservative / x * 100.0) if x else math.inf,
    }


def analyze(data: Dict[str, Any]) -> Dict[str, Any]:
    measurement = data.get("measurement")
    if not isinstance(measurement, dict):
        raise ValueError("measurement object is required")
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("sources must be a non-empty list")
    rows = [normalize_source(measurement, s) for s in sources]
    pre = summarize(measurement, rows, post_calibration=False)
    post = summarize(measurement, rows, post_calibration=True)
    ranked = sorted(rows, key=lambda r: r.input_error, reverse=True)
    return {
        "measurement": measurement,
        "sources": [asdict(r) for r in rows],
        "pre_calibration": pre,
        "post_calibration": post,
        "dominant_sources": [asdict(r) for r in ranked[:5]],
        "warnings": build_warnings(measurement, rows),
    }


def build_warnings(measurement: Dict[str, Any], rows: List[NormalizedSource]) -> List[str]:
    warnings: List[str] = []
    if any(r.basis.lower() == "typical" for r in rows):
        warnings.append("预算包含 typical 指标，不能作为保证边界。")
    if measurement.get("calibration_mode", "none") != "none":
        has_cal_ref = any("校准" in r.name and r.retained_after_calibration for r in rows)
        if not has_cal_ref:
            warnings.append("启用了校准，但未看到校准源不确定度或拟合残差项。")
    if not any(r.combination == "random" for r in rows):
        warnings.append("未提供随机噪声项，随机 RMS 结果为 0 并不代表真实系统无噪声。")
    if any(r.spec_type == "percent_full_scale" for r in rows) and measurement.get("full_scale_input") is None:
        warnings.append("存在 %FS 项，确认 full_scale_input 定义与被测输入单位一致。")
    return warnings


def render_markdown(result: Dict[str, Any]) -> str:
    m = result["measurement"]
    unit = m.get("unit", "input units")
    lines = [
        f"# {m.get('name', 'Analog acquisition')} 误差预算",
        "",
        f"- 工作点：{m.get('value')} {unit}",
        f"- 校准模式：{m.get('calibration_mode', 'none')}",
        f"- 结果算法：{m.get('result_algorithm', 'direct')}",
        f"- 温度：{m.get('temperature_reference_c', 25)}°C → {m.get('temperature_operating_c', 25)}°C",
        "",
        "## 误差明细",
        "",
        "| 来源 | 类型 | 原始输入等效 | 对结果的误差 | 合并 | 校准后保留 | 公式 |",
        "|---|---|---:|---:|---|---|---|",
    ]
    for row in result["sources"]:
        safe_formula = str(row["formula"]).replace("|", "\\|")
        lines.append(
            f"| {row['name']} | {row['spec_type']} | {row['raw_input_error']:.9g} {unit} | "
            f"{row['input_error']:.9g} {unit} | {row['combination']} | "
            f"{'是' if row['retained_after_calibration'] else '否'} | {safe_formula} |"
        )
    lines.extend(["", "## 合并结果", "", "| 场景 | 系统最坏值 | 系统 RSS | 随机 RMS | 系统最坏+kσ | 相对保守误差 |", "|---|---:|---:|---:|---:|---:|"])
    for title, key in [("未校准", "pre_calibration"), ("校准后", "post_calibration")]:
        s = result[key]
        lines.append(
            f"| {title} | {s['systematic_worst_case']:.9g} {unit} | "
            f"{s['systematic_rss_estimate']:.9g} {unit} | {s['random_rms']:.9g} {unit} | "
            f"{s['conservative_systematic_plus_k_sigma']:.9g} {unit} | {s['relative_conservative_percent']:.6g}% |"
        )
    lines.extend(["", "## 主导误差", ""])
    for idx, row in enumerate(result["dominant_sources"], start=1):
        lines.append(f"{idx}. {row['name']}：{row['input_error']:.9g} {unit}")
    if result["warnings"]:
        lines.extend(["", "## 警告", ""])
        for w in result["warnings"]:
            lines.append(f"- {w}")
    return "\n".join(lines) + "\n"


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON input file")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        result = analyze(data)
        text = render_markdown(result) if args.format == "markdown" else json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text)
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
