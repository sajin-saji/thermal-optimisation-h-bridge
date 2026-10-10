"""
Rebuild the Design of Experiments (DOE) table used for the heat sink optimisation.

In Ansys Workbench (Response Surface Optimisation) I varied three parameters:
    N  = number of fins        8 ... 14
    bh = base height  [mm]     0.5 ... 2.0
    th = fin thickness [mm]    0.5 ... 2.0

For every fin count Workbench generated 5 points: the centre of the (bh, th)
square plus its 4 corners. 7 fin counts x 5 points = 35 design points.
This script writes the same table (thesis Figure 4.11) to data/doe_design_points.csv.

Usage:
    python src/generate_doe.py
"""

from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "doe_design_points.csv"

FIN_COUNTS = range(8, 15)          # 8 .. 14
LOW, MID, HIGH = 0.5, 1.25, 2.0    # mm

# (bh, th) pattern used by Workbench for each fin count, in this order
PATTERN = [
    (MID, MID),    # centre point
    (LOW, LOW),
    (HIGH, LOW),
    (LOW, HIGH),
    (HIGH, HIGH),
]


def build_points():
    points = []
    point_id = 1
    for n in FIN_COUNTS:
        for bh, th in PATTERN:
            points.append({"design_point": point_id, "N_fins": n,
                           "bh_base_height_mm": bh, "th_fin_thickness_mm": th})
            point_id += 1
    return points


def main():
    points = build_points()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(points[0].keys()))
        writer.writeheader()
        writer.writerows(points)
    print(f"Wrote {len(points)} design points to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
