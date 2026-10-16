#!/usr/bin/env python3
"""Physical constants lookup + unit helpers. Usage: python constants.py [name ...]"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "..", "references", "constants.json")) as f:
    C = {k: v for k, v in json.load(f).items() if not k.startswith("_")}

def val(name): return C[name]["value"]
def eV_to_J(x): return x*val("e")
def J_to_eV(x): return x/val("e")
def wavelength_nm_to_eV(l_nm): return val("h")*val("c")/(l_nm*1e-9)/val("e")
def temperature_to_eV(T): return val("k_B")*T/val("e")
def compton_wavelength(m): return val("h")/(m*val("c"))
def schwarzschild_radius(M): return 2*val("G")*M/val("c")**2
def de_broglie(m, v): return val("h")/(m*v)

if __name__ == "__main__":
    names = sys.argv[1:] or sorted(C)
    for n in names:
        d = C[n]; print(f"{n:10s} = {d['value']:<18.10g} {d['unit']:<16s} {d['name']}")
    if len(sys.argv) == 1:
        print("\nDerived: 500nm photon =", round(wavelength_nm_to_eV(500), 4), "eV;",
              "kT(300K) =", round(temperature_to_eV(300)*1000, 2), "meV;",
              "r_s(Sun) =", round(schwarzschild_radius(val("M_sun"))/1000, 3), "km")
