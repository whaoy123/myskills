#!/usr/bin/env python3
"""Traceable helpers for common hardware review calculations. Inputs use explicit SI units."""
from __future__ import annotations
import argparse, json, math
def emit(model, inputs, formula, result, sanity):
    print(json.dumps({"model": model, "inputs": inputs, "formula": formula, "nominal_result": result, "sanity_check": sanity}, indent=2))
def positive(name, x):
    if x <= 0:
        raise SystemExit(f"{name} must be > 0")
def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("divider"); p.add_argument("--vin", type=float, required=True, help="volts"); p.add_argument("--rtop", type=float, required=True, help="ohms"); p.add_argument("--rbottom", type=float, required=True, help="ohms")
    p = sub.add_parser("gain-noninverting"); p.add_argument("--rf", type=float, required=True, help="ohms"); p.add_argument("--rg", type=float, required=True, help="ohms")
    p = sub.add_parser("rc-lowpass"); p.add_argument("--r", type=float, required=True, help="ohms"); p.add_argument("--c", type=float, required=True, help="farads")
    p = sub.add_parser("resistor-power"); g = p.add_mutually_exclusive_group(required=True); g.add_argument("--voltage", type=float, help="volts across resistor"); g.add_argument("--current", type=float, help="amps through resistor"); p.add_argument("--r", type=float, required=True, help="ohms")
    a = ap.parse_args()
    if a.cmd == "divider":
        positive("rtop", a.rtop); positive("rbottom", a.rbottom); ratio=a.rbottom/(a.rtop+a.rbottom); vout=a.vin*ratio; inverse=vout/ratio
        emit("resistor-divider:v1", [{"name":"vin","value":a.vin,"unit":"V"},{"name":"rtop","value":a.rtop,"unit":"ohm"},{"name":"rbottom","value":a.rbottom,"unit":"ohm"}], "Vout = Vin * Rbottom / (Rtop + Rbottom)", {"name":"vout","value":vout,"unit":"V"}, {"method":"inverse","vin_reconstructed":inverse,"unit":"V"})
    elif a.cmd == "gain-noninverting":
        positive("rf", a.rf); positive("rg", a.rg); gain=1+a.rf/a.rg; rf_back=(gain-1)*a.rg
        emit("noninverting-gain:v1", [{"name":"rf","value":a.rf,"unit":"ohm"},{"name":"rg","value":a.rg,"unit":"ohm"}], "Av = 1 + Rf/Rg", {"name":"gain","value":gain,"unit":"V/V"}, {"method":"inverse","rf_reconstructed":rf_back,"unit":"ohm"})
    elif a.cmd == "rc-lowpass":
        positive("r", a.r); positive("c", a.c); fc=1/(2*math.pi*a.r*a.c); c_back=1/(2*math.pi*a.r*fc)
        emit("rc-lowpass:v1", [{"name":"r","value":a.r,"unit":"ohm"},{"name":"c","value":a.c,"unit":"F"}], "fc = 1 / (2*pi*R*C)", {"name":"fc","value":fc,"unit":"Hz"}, {"method":"inverse","c_reconstructed":c_back,"unit":"F"})
    elif a.cmd == "resistor-power":
        positive("r", a.r)
        if a.voltage is not None: pwr=a.voltage*a.voltage/a.r; current=a.voltage/a.r; formula="P = V^2/R"
        else: pwr=a.current*a.current*a.r; current=a.current; formula="P = I^2*R"
        emit("resistor-power:v1", [{"name":"r","value":a.r,"unit":"ohm"},{"name":"current","value":current,"unit":"A"}], formula, {"name":"power","value":pwr,"unit":"W"}, {"method":"ohms-law","voltage":current*a.r,"unit":"V"})
if __name__ == "__main__": main()
