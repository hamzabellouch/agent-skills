---
name: kicad-pcb-schematic-layout
metadata:
  category: Hardware Design and EDA FPGA
description: Design, route, and verify printed circuit boards (PCBs) using KiCad 8 EDA. Master schematic capture, Electrical Rules Check (ERC), footprint assignments, multi-layer stackups, impedance-controlled trace routing, ground plane stitching vias, Design Rules Check (DRC), and manufacturing fabrication exports (Gerber RS-274X, Excellon drill files, IPC-D-356 netlists). Trigger when designing electronics, routing PCBs, or preparing hardware for fabrication.
compatibility: KiCad 7+, KiCad 8+, IPC-2221 PCB Design Standard
---

# KiCad PCB Schematic & Layout Skill Guide

This skill governs best practices, electronic design automation (EDA) workflows, and manufacturing readiness standards for designing printed circuit boards in KiCad.

---

## 1. PCB Design Life Cycle Flow

```text
[ Electronic Requirements & Component Sourcing ]
                      |
                      v
[ 1. Schematic Capture (Eeschema) ]
  |-- Connect functional blocks & bypass capacitors
  |-- Assign reference designators & component values
  |-- Run Electrical Rules Check (ERC) -> 0 Errors
                      |
                      v
[ 2. Footprint Association & Netlist Sync (F8) ]
                      |
                      v
[ 3. PCB Layout & Routing (Pcbnew) ]
  |-- Layer Stackup Definition (e.g. 4-Layer: SIG - GND - PWR - SIG)
  |-- Critical Net Routing (Differential pairs, 50-ohm RF, high-current traces)
  |-- Solid Ground Plane Pours & Thermal Relief
  |-- Run Design Rules Check (DRC) -> 0 Errors / 0 Warnings
                      |
                      v
[ 4. Manufacturing Export ] -> Gerbers + Drill + BOM + Pick & Place (CPL)
```

---

## 2. Standard 4-Layer Stackup & Rules

For modern high-speed microcontrollers (ESP32, STM32, RP2040) and high-speed digital buses, a **4-layer board with continuous ground reference planes** is standard practice:

| Layer # | Layer Name | Type | Recommended Usage |
|---|---|---|---|
| **Layer 1** | F.Cu (Top) | Signal / Component | High-speed traces, component placement |
| **Layer 2** | In1.Cu | Solid Ground Plane | Unbroken 0V reference plane for return currents |
| **Layer 3** | In2.Cu | Power Plane / Mix | 3.3V / 5.0V power rail pours, non-critical signals |
| **Layer 4** | B.Cu (Bottom) | Signal / GND | Low-speed signals, bottom test points, solid GND pour |

---

## 3. Critical PCB Layout Design Rules

### A. Decoupling Capacitor Placement
- Place ceramic decoupling capacitors ($0.1\,\mu\text{F}$ and $10\,\mu\text{F}$) **as physically close as possible** to the IC power pin ($\le 2\,\text{mm}$).
- Route power from the capacitor pin to the IC pin directly, or place the via on the outside of the capacitor so current flows through the capacitor pads before reaching the IC:

```text
[ Power Plane Via ] ---> [ Decoupling Cap Pad ] ---> [ IC VDD Pin ]
```

### B. Differential Pair Routing & Trace Geometry
- Use KiCad's Differential Pair Routing tool (`Route -> Route Differential Pairs`).
- Maintain constant trace spacing ($S$) and width ($W$) along the entire run to preserve differential impedance (e.g., $90\,\Omega \pm 10\%$ for USB 2.0 D+/D-).
- Avoid 90-degree corners; use $45^\circ$ bends or smooth circular arcs to prevent impedance discontinuities.

### C. Ground Stitching Vias
- Place ground vias along the perimeter of the PCB at intervals of $\le \frac{\lambda}{10}$ (typically every 3 to 5 mm) to suppress RF emissions.
- Stitch together top and bottom ground copper pours around sensitive analog/RF sections.

---

## 4. Pre-Fabrication Verification Checklist

- [ ] **ERC Cleared:** Zero unconnected pins (use `No Connect` flag on unused pins) and no conflicting power outputs in Eeschema.
- [ ] **DRC Cleared:** Run DRC against the specific fabricator's capabilities (e.g. minimum trace width 0.127 mm, minimum clearance 0.127 mm, minimum via drill 0.3 mm).
- [ ] **Thermal Reliefs:** Ensure thermal relief spokes are enabled on component through-hole pins connected to power/ground planes to facilitate hand-soldering.
- [ ] **Silkscreen Legibility:** Check that reference designators (R1, C1, U1) do not overlap exposed copper pads or vias.
- [ ] **Gerber Inspection:** Review generated Gerbers using KiCad's `GerbView` before submitting to the PCB fabrication house.
