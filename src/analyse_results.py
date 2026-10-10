"""
Analyse the Ansys Icepak results from my thesis and make the charts for the README.

Input  (data/):
    case_summary.csv            max motor controller IC temperature per case
    component_temperatures.csv  temperature of every component in all 4 cases

Output (results/):
    01_max_temperature_by_case.png
    02_hot_components_by_case.png
    03_temperature_rise_above_ambient.png
    summary_table.md            reduction per case (pasted into the README)

Usage:
    pip install -r requirements.txt
    python src/analyse_results.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

AMBIENT_C = 25.0     # ambient temperature used in all simulations
LIMIT_C = 85.0       # common max. operating temperature mentioned in the literature review

# chart style: thin marks, quiet grid, text in ink colours (not series colours)
INK = "#1f1f1e"
INK_2 = "#5c5b55"
GRID = "#e4e3de"
SURFACE = "#fcfcfb"
BLUE = "#2a78d6"
CASE_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]  # validated categorical order
CASE_LABELS = ["1  No heat sink", "2  Heat sink", "3  Optimised heat sink",
               "4  Optimised heat sink + fan"]

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": INK_2, "text.color": INK,
    "xtick.color": INK_2, "ytick.color": INK_2, "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False,
})


def load():
    summary = pd.read_csv(DATA / "case_summary.csv")
    comps = pd.read_csv(DATA / "component_temperatures.csv")
    return summary, comps


def summary_table(summary):
    base = summary.loc[0, "max_ic_temperature_C"]
    s = summary.copy()
    s["drop_vs_case1_C"] = (base - s["max_ic_temperature_C"]).round(1)
    s["drop_vs_case1_pct"] = (100 * s["drop_vs_case1_C"] / base).round(1)
    s["rise_above_ambient_C"] = (s["max_ic_temperature_C"] - AMBIENT_C).round(1)
    s["rise_reduction_pct"] = (100 * (1 - s["rise_above_ambient_C"] /
                                       s.loc[0, "rise_above_ambient_C"])).round(1)
    return s


def chart_max_temperature(s):
    fig, ax = plt.subplots(figsize=(8, 4.2))
    y = range(len(s))[::-1]
    ax.barh(list(y), s["max_ic_temperature_C"], color=BLUE, height=0.55)
    for yi, v in zip(y, s["max_ic_temperature_C"]):
        ax.text(v + 2, yi, f"{v:.1f} °C", va="center", color=INK, fontsize=10)
    ax.axvline(LIMIT_C, color=INK_2, lw=1, ls="--")
    ax.text(LIMIT_C + 1.5, -0.45, "85 °C typical limit", color=INK_2, fontsize=9, va="center")
    ax.set_yticks(list(y))
    ax.set_yticklabels(s["description"])
    ax.set_xlim(0, 175)
    ax.set_ylim(-0.75, len(s) - 0.5)
    ax.set_xlabel("Maximum motor controller IC temperature (°C)")
    ax.xaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_title("Hotspot temperature drops from 154.3 °C to 53.9 °C",
                 loc="left", fontsize=12, color=INK, pad=12)
    fig.tight_layout()
    fig.savefig(RESULTS / "01_max_temperature_by_case.png", dpi=160)
    plt.close(fig)


def chart_hot_components(comps):
    cols = [c for c in comps.columns if c.startswith("case")]
    # components that were above 60 °C in case 1 (the ones that needed cooling)
    hot = comps[comps[cols[0]] > 60].sort_values(cols[0], ascending=False)
    fig, ax = plt.subplots(figsize=(9, 4.6))
    n = len(hot)
    width = 0.2
    for i, (col, color, label) in enumerate(zip(cols, CASE_COLORS, CASE_LABELS)):
        xs = [x + (i - 1.5) * (width + 0.01) for x in range(n)]
        ax.bar(xs, hot[col], width=width, color=color, label=label)
    ax.axhline(AMBIENT_C, color=INK_2, lw=1, ls=":")
    ax.set_xticks(range(n))
    ax.set_xticklabels(hot["component"])
    ax.set_ylabel("Temperature (°C)")
    ax.yaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=9, ncol=2, loc="upper right")
    ax.set_ylim(0, 185)
    ax.set_title("Components above 60 °C without cooling, across the 4 cases  (dotted line = 25 °C ambient)",
                 loc="left", fontsize=12, color=INK, pad=12)
    fig.tight_layout()
    fig.savefig(RESULTS / "02_hot_components_by_case.png", dpi=160)
    plt.close(fig)


def chart_rise(s):
    fig, ax = plt.subplots(figsize=(8, 3.8))
    x = range(len(s))
    ax.plot(list(x), s["rise_above_ambient_C"], color=BLUE, lw=2, marker="o", ms=8)
    for xi, v in zip(x, s["rise_above_ambient_C"]):
        ax.text(xi, v + 7, f"+{v:.1f} K", ha="center", color=INK, fontsize=10)
    ax.set_xticks(list(x))
    ax.set_xticklabels([l.split("  ")[1] for l in CASE_LABELS], fontsize=9)
    ax.set_ylim(0, 150)
    ax.set_ylabel("IC temperature rise above ambient (K)")
    ax.yaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_title("Temperature rise above ambient cut by 77.6 %",
                 loc="left", fontsize=12, color=INK, pad=12)
    fig.tight_layout()
    fig.savefig(RESULTS / "03_temperature_rise_above_ambient.png", dpi=160)
    plt.close(fig)


def write_markdown(s):
    lines = ["| Case | Setup | Max IC temp (°C) | Drop vs case 1 | Rise above ambient |",
             "|---|---|---|---|---|"]
    for _, r in s.iterrows():
        drop = "–" if r["case"] == 1 else f"−{r['drop_vs_case1_C']} °C ({r['drop_vs_case1_pct']} %)"
        lines.append(f"| {r['case']} | {r['description']} | **{r['max_ic_temperature_C']}** | "
                     f"{drop} | +{r['rise_above_ambient_C']} K |")
    (RESULTS / "summary_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    summary, comps = load()
    s = summary_table(summary)
    print(s[["case", "description", "max_ic_temperature_C", "drop_vs_case1_C",
             "drop_vs_case1_pct", "rise_above_ambient_C", "rise_reduction_pct"]]
          .to_string(index=False))
    chart_max_temperature(s)
    chart_hot_components(comps)
    chart_rise(s)
    write_markdown(s)
    print(f"\nCharts and summary written to {RESULTS.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
