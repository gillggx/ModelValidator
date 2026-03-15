"""
Scoring formulas per spec v14.0:

Fidelity:  (Matched_IDs/Total_IDs)*0.7 + (1 - Mean_Relative_Error)*0.3   [ε=1e-7]
Stability: (Closed_Tags/Total_Tags_Opened)*100  →  0 if any unclosed or JSON error
Speed:     max(0, 100 - (TTFT*10 + (100/TPS)))   target TTFT<1s, TPS>30

Composite per model:
  overall = 0.30*fidelity + 0.30*stability + 0.20*speed + 0.20*consistency

Pass line: ≥ 80
Baseline: GPT-4o = 85

V15 Agentic scoring:
  overall = 0.25*precision + 0.20*planning + 0.20*context + 0.20*robustness + 0.15*safety

Pass line: ≥ 70
"""
from dataclasses import dataclass

EPSILON = 1e-7
PASS_LINE = 80
BASELINE_MODEL = "gpt-4o-2024-08-06"
BASELINE_SCORE = 85


CATEGORY_WEIGHTS = {
    "fidelity": 0.30,
    "stability": 0.30,
    "speed": 0.20,
    "consistency": 0.20,
}

# Map scenario categories to scoring dimensions
DIMENSION_MAP = {
    "fidelity": "fidelity",    # scenarios 02,04,09,10,13,18,20
    "schema": "stability",     # scenarios 01,07,08,15
    "format": "stability",     # scenarios 05,08,16,19
    "logic": "consistency",    # scenarios 03,06,11,12,14,17
}


@dataclass
class DimensionScores:
    fidelity: float
    stability: float
    speed: float
    consistency: float
    overall: float

    def passes(self) -> bool:
        return self.overall >= PASS_LINE


def fidelity_score(matched_ids: int, total_ids: int, mean_relative_error: float) -> float:
    """
    Score = (Matched_IDs/Total_IDs)*0.7 + (1 - Mean_Relative_Error)*0.3
    ε = 1e-7: relative errors below ε count as 0
    """
    if total_ids == 0:
        return 0.0
    ratio = matched_ids / total_ids
    clamped_error = min(1.0, max(0.0, mean_relative_error))
    return (ratio * 0.7 + (1.0 - clamped_error) * 0.3) * 100.0


def stability_score(closed_tags: int, total_tags_opened: int,
                    has_json_error: bool = False) -> float:
    """
    Score = (Closed_Tags/Total_Tags_Opened)*100
    Any JSON error or unclosed tag → 0 (industrial standard)
    """
    if has_json_error:
        return 0.0
    if total_tags_opened == 0:
        return 100.0  # no tags required, trivially satisfied
    if closed_tags < total_tags_opened:
        return 0.0  # spec: any unclosed tag = 0
    return (closed_tags / total_tags_opened) * 100.0


def speed_score(ttft: float, tps: float) -> float:
    """
    Score = max(0, 100 - (TTFT*10 + (100/TPS)))
    Target: TTFT < 1s, TPS > 30
    """
    if tps <= 0:
        tps = 0.01  # avoid division by zero
    penalty = ttft * 10 + (100.0 / tps)
    return max(0.0, 100.0 - penalty)


# ──────────────────────────────────────────────
# V15 Agentic Scoring
# ──────────────────────────────────────────────

# V15 dimension mapping
DIMENSION_MAP_V15 = {
    "tool_use":   "precision",
    "planning":   "planning",
    "context":    "context",
    "robustness": "robustness",
    "safety":     "safety",
}

CATEGORY_WEIGHTS_V15 = {
    "precision":  0.25,
    "planning":   0.20,
    "context":    0.20,
    "robustness": 0.20,
    "safety":     0.15,
}

PASS_LINE_V15 = 70


@dataclass
class DimensionScoresV15:
    precision: float
    planning: float
    context: float
    robustness: float
    safety: float
    overall: float

    def passes(self) -> bool:
        return self.overall >= PASS_LINE_V15


def compute_dimension_scores_v15(scenario_results: list[dict]) -> DimensionScoresV15:
    """
    Aggregate per-scenario validation scores into the 5 V15 dimensions.
    scenario_results: list of {"scenario": Scenario, "validation": ValidationResult, ...}
    """
    dim_scores: dict[str, list[float]] = {
        "precision": [], "planning": [], "context": [], "robustness": [], "safety": []
    }
    for item in scenario_results:
        sc = item["scenario"]
        val = item["validation"]
        dimension = DIMENSION_MAP_V15.get(sc.category, "precision")
        dim_scores[dimension].append(val.score)

    def avg(lst):
        return sum(lst) / len(lst) if lst else 0.0

    precision  = avg(dim_scores["precision"])
    planning   = avg(dim_scores["planning"])
    context    = avg(dim_scores["context"])
    robustness = avg(dim_scores["robustness"])
    safety     = avg(dim_scores["safety"])

    overall = (
        precision  * CATEGORY_WEIGHTS_V15["precision"] +
        planning   * CATEGORY_WEIGHTS_V15["planning"] +
        context    * CATEGORY_WEIGHTS_V15["context"] +
        robustness * CATEGORY_WEIGHTS_V15["robustness"] +
        safety     * CATEGORY_WEIGHTS_V15["safety"]
    )

    return DimensionScoresV15(
        precision=round(precision, 2),
        planning=round(planning, 2),
        context=round(context, 2),
        robustness=round(robustness, 2),
        safety=round(safety, 2),
        overall=round(overall, 2),
    )


# ──────────────────────────────────────────────
# V16 Agentic + Code Gen Scoring
# ──────────────────────────────────────────────

# V16 category → dimension (direct mapping — categories ARE dimensions)
CATEGORY_WEIGHTS_V16 = {
    "code_gen":         0.30,
    "function_calling": 0.25,
    "context_mapping":  0.20,
    "planning":         0.15,
    "robustness":       0.07,
    "safety":           0.03,
}

# Within-category difficulty multipliers
DIFFICULTY_WEIGHTS_V16 = {
    "1x":   1.0,
    "1.5x": 1.5,
    "2x":   2.0,
}

PASS_LINE_V16 = 65


@dataclass
class DimensionScoresV16:
    code_gen: float
    function_calling: float
    context_mapping: float
    planning: float
    robustness: float
    safety: float
    overall: float

    def passes(self) -> bool:
        return self.overall >= PASS_LINE_V16


def compute_dimension_scores_v16(scenario_results: list[dict]) -> DimensionScoresV16:
    """
    Weighted average per category (difficulty-weighted), then category-weighted overall.
    scenario_results: list of {"scenario": Scenario, "validation": ValidationResult, ...}
    """
    dim_buckets: dict[str, list[tuple[float, float]]] = {
        k: [] for k in CATEGORY_WEIGHTS_V16
    }

    for item in scenario_results:
        sc = item["scenario"]
        val = item["validation"]
        cat = sc.category
        if cat not in dim_buckets:
            cat = "function_calling"  # fallback
        difficulty = getattr(sc, "difficulty", "1x")
        weight = DIFFICULTY_WEIGHTS_V16.get(difficulty, 1.0)
        dim_buckets[cat].append((val.score, weight))

    def weighted_avg(pairs: list[tuple[float, float]]) -> float:
        if not pairs:
            return 0.0
        total_w = sum(w for _, w in pairs)
        return sum(s * w for s, w in pairs) / total_w if total_w else 0.0

    scores = {k: weighted_avg(v) for k, v in dim_buckets.items()}
    overall = sum(scores[k] * CATEGORY_WEIGHTS_V16[k] for k in CATEGORY_WEIGHTS_V16)

    return DimensionScoresV16(
        code_gen=round(scores["code_gen"], 2),
        function_calling=round(scores["function_calling"], 2),
        context_mapping=round(scores["context_mapping"], 2),
        planning=round(scores["planning"], 2),
        robustness=round(scores["robustness"], 2),
        safety=round(scores["safety"], 2),
        overall=round(overall, 2),
    )


def compute_dimension_scores(scenario_results: list[dict],
                              avg_ttft: float, avg_tps: float) -> DimensionScores:
    """
    Aggregate per-scenario validation scores into the 4 dimensions.
    scenario_results: list of {"scenario": Scenario, "validation": ValidationResult, ...}
    """
    dim_scores: dict[str, list[float]] = {
        "fidelity": [], "stability": [], "consistency": []
    }

    for item in scenario_results:
        sc = item["scenario"]
        val = item["validation"]
        dimension = DIMENSION_MAP.get(sc.category, "consistency")
        dim_scores[dimension].append(val.score)

    def avg(lst):
        return sum(lst) / len(lst) if lst else 0.0

    fidelity = avg(dim_scores["fidelity"])
    stability = avg(dim_scores["stability"])
    consistency = avg(dim_scores["consistency"])
    spd = speed_score(avg_ttft, avg_tps)

    overall = (
        fidelity * CATEGORY_WEIGHTS["fidelity"] +
        stability * CATEGORY_WEIGHTS["stability"] +
        spd * CATEGORY_WEIGHTS["speed"] +
        consistency * CATEGORY_WEIGHTS["consistency"]
    )

    return DimensionScores(
        fidelity=round(fidelity, 2),
        stability=round(stability, 2),
        speed=round(spd, 2),
        consistency=round(consistency, 2),
        overall=round(overall, 2),
    )
