"""Headless, deterministic plot generation from result mappings."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


def plot_metric(
    rows: Iterable[Mapping[str, Any]],
    *,
    x_key: str,
    y_key: str,
    output_path: str | Path,
    group_key: str | None = None,
    title: str = "",
    x_label: str | None = None,
    y_label: str | None = None,
) -> Path:
    import matplotlib

    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    data = list(rows)
    if not data:
        raise ValueError("at least one row is required")

    groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in data:
        key = str(row[group_key]) if group_key else "series"
        groups[key].append(row)

    figure, axis = plt.subplots(figsize=(6.4, 4.0), constrained_layout=True)
    for label, group in sorted(groups.items()):
        ordered = sorted(group, key=lambda row: float(row[x_key]))
        axis.plot(
            [float(row[x_key]) for row in ordered],
            [float(row[y_key]) for row in ordered],
            marker="o",
            label=label,
        )
    axis.set_title(title)
    axis.set_xlabel(x_label or x_key)
    axis.set_ylabel(y_label or y_key)
    axis.grid(True, alpha=0.3)
    if group_key:
        axis.legend()

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(target, dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)
    return target
