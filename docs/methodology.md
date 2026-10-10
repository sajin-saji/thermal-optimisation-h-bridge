# Methodology (short version)

The full text is in [`thesis_optimum_design_electronic_cooling.pdf`](thesis_optimum_design_electronic_cooling.pdf). This page is the summary.

## 1. Why a motor controller

More and more cars are electric. After the battery, the motor controller is one of the most important parts of an EV, and its reliability depends a lot on temperature. A hotter component fails sooner. So I picked a simplified **H-bridge motor controller board** as the test case.

## 2. Steps

1. **Geometry:** I built the board in Ansys Icepak with component sizes based on standard packages (figures `01` and `02`).
2. **Materials and heat loads:** Controller IC 20 W, MOSFETs 2 W each, electrolytic capacitors 1 W each. Everything else is passive (see `data/component_setup.csv`).
3. **Mesh:** Mesher HD with a multi-level mesh. Level 1 for the PCB, level 2 for the power and motor pins, level 3 for the support IC and MOSFETs, level 4 for resistors, diodes and optocouplers. 644,499 elements in total.
4. **Case 1, no heat sink:** Natural convection, laminar, cabinet with two openings, gravity perpendicular to the board. Convergence checked (converged after about 175 iterations).
5. **Case 2, heat sink:** Aluminium heat sink on the controller IC with the same footprint as the IC. 8 fins, 2 mm fin thickness, 1.5 mm base, 11 mm overall height.
6. **Case 3, optimised heat sink:** Fin count `N`, fin thickness `th` and base height `bh` became parameters (`$N`, `$th`, `$bh` in Icepak). Workbench Response Surface Optimisation ran 35 design points (`data/doe_design_points.csv`) with the objectives max. temperature, heat sink mass and thermal resistance.
7. **Case 4, fan:** The cabinet openings were replaced by a fan (1000 rpm) on one side and a grille on the other, with the airflow parallel to the fins. Forced convection with the turbulent k-ε model. Air speed was about 8.7 m/s at the inlet and about 7.5 m/s through the fins (figures `07`, `08`, `09`).
8. **Comparison:** I compared the temperature, pressure and velocity fields of all four cases.

## 3. Governing equations

Icepak solves the 3-D continuity, momentum (Navier–Stokes) and energy equations. Buoyancy comes in through the Boussinesq approximation. For case 4 the turbulence is closed with the standard k-ε model.

For a quick estimate of a heat sink alone, the thesis also gives the lumped energy balance:

```
d(ρ c V T)/dt = P − h A (T − T∞) − ε σ A (T⁴ − T∞⁴)
```

This can be solved with the 4th-order Runge–Kutta method.

## 4. Figures in `docs/figures`

| File | Content |
|---|---|
| `01_board_geometry_isometric.png` | 3-D model of the board |
| `02_board_layout_top.png` | Top view with component labels |
| `03_case1_no_heatsink.png` | Temperature field, case 1 |
| `04_case2_heatsink.png` | Temperature field, case 2 |
| `05_case3_optimised_heatsink.png` | Temperature field, case 3 |
| `06_case4_fan_isometric.png` | Temperature field, case 4 (isometric) |
| `07_case4_fan_side.png` | Temperature field, case 4 (side view) |
| `08_fan_enclosure_setup.png` | Cabinet with fan and grille |
| `09_fan_curve.png` | Fan curve (pressure vs. volume flow) |
