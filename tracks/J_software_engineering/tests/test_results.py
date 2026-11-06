import csv
import json
import statistics
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RESULTS = ROOT / "tracks" / "J_software_engineering" / "results"
PROJECT = ROOT / "external" / "more-itertools"
PIN = "f42daddf205f335fea6e200dad46049f33e71221"


def _csv(name):
    with (RESULTS / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def test_pinned_public_source_is_large_clean_and_mit_licensed():
    source = json.loads((RESULTS / "source_provenance.json").read_text())
    assert source["commit"] == PIN
    assert source["license"] == "MIT"
    assert source["python_physical_lines"] >= 1000
    assert source["python_nonblank_noncomment_lines"] >= 1000
    assert source["checkout_dirty"] is False
    assert subprocess.check_output(["git", "-C", str(PROJECT), "rev-parse", "HEAD"], text=True).strip() == PIN


def test_baseline_was_profiled_before_selection_and_passed_completely():
    profile = json.loads((RESULTS / "baseline_profile.json").read_text())
    runs = _csv("baseline_runs.csv")
    assert profile["profiled_before_optimization"] is True
    assert profile["individual_test_count"] == 771
    assert profile["all_full_suite_tests_passed"] is True
    assert 0.0 <= profile["source_coverage_percent"] <= 100.0
    assert all(int(row["passed_tests"]) == 771 for row in runs)
    assert len(runs) == 3


def test_retained_line_sets_recompute_every_reported_objective_and_budget():
    coverage = json.loads((RESULTS / "candidate_coverage.json").read_text())["candidate_lines"]
    summaries = {row["method"]: row for row in _csv("selection_summary.csv")}
    selected: dict[str, list[str]] = {}
    for row in _csv("selected_tests.csv"):
        selected.setdefault(row["method"], []).append(row["candidate_id"])
    for method, identifiers in selected.items():
        union = set().union(*(set(coverage[identifier]) for identifier in identifiers))
        summary = summaries[method]
        assert len(union) == int(summary["objective_covered_lines"])
        assert float(summary["profiled_selection_cost_seconds"]) <= float(summary["budget_seconds"]) + 1e-12
        assert summary["profile_prediction_matches_rerun"] == "True"
        assert summary["all_selected_runs_passed"] == "True"


def test_greedy_improves_budgeted_coverage_and_exact_subset_is_verified():
    summaries = {row["method"]: row for row in _csv("selection_summary.csv")}
    original = summaries["original_order"]
    greedy = summaries["greedy_coverage_per_second"]
    assert int(greedy["objective_covered_lines"]) > int(original["objective_covered_lines"])
    exact = json.loads((RESULTS / "exact_subset_reference.json").read_text())
    assert exact["greedy_optimality_gap_lines"] == 0
    assert exact["original_order_optimality_gap_lines"] > 0


def test_selected_suites_are_faster_but_explicitly_not_full_regression():
    baseline_median = statistics.median(float(row["wall_time_seconds"]) for row in _csv("baseline_runs.csv"))
    summaries = _csv("selection_summary.csv")
    assert all(float(row["actual_wall_time_seconds_median"]) < baseline_median for row in summaries)
    manifest = json.loads((RESULTS / "manifest.json").read_text())
    assert manifest["all_selected_suites_passed"] is True
    assert manifest["coverage_predictions_verified"] is True
    assert "not substitutes for the full regression suite" in manifest["claim_limit"]
