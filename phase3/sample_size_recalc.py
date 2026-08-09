"""Frozen Phase 3 cluster sample-size recalculation.

Run only after the 4-week baseline database is locked and before randomization.
This utility does not authorize a confirmatory superiority claim in Phase 3.
"""
from __future__ import annotations

import argparse
import math

Z_ALPHA_OVER_2 = 1.959964
Z_POWER = 0.841621
D_PLANNING = 0.50
MIN_TEAMS_PER_ARM = 6


def required_teams_per_arm(nbar: float, icc: float, r: float, cluster_loss: float = 0.10) -> dict:
    if nbar <= 0:
        raise ValueError("nbar must be > 0")
    if not 0 <= icc < 1:
        raise ValueError("icc must be in [0, 1)")
    if not -1 < r < 1:
        raise ValueError("r must be in (-1, 1)")
    if not 0 <= cluster_loss < 1:
        raise ValueError("cluster_loss must be in [0, 1)")

    design_effect = 1 + (nbar - 1) * icc
    baseline_adjustment = 1 - r**2
    m_raw = (
        2
        * (Z_ALPHA_OVER_2 + Z_POWER) ** 2
        * baseline_adjustment
        * design_effect
        / (nbar * D_PLANNING**2)
    )
    m_loss_adjusted = math.ceil(m_raw / (1 - cluster_loss))
    required = max(MIN_TEAMS_PER_ARM, m_loss_adjusted)
    return {
        "nbar": nbar,
        "icc": icc,
        "baseline_correlation_r": r,
        "cluster_loss": cluster_loss,
        "planning_d": D_PLANNING,
        "m_raw": m_raw,
        "m_loss_adjusted": m_loss_adjusted,
        "required_teams_per_arm": required,
        "required_total_5_arms": 5 * required,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nbar", type=float, required=True)
    parser.add_argument("--icc", type=float, required=True)
    parser.add_argument("--r", type=float, required=True)
    parser.add_argument("--cluster-loss", type=float, default=0.10)
    args = parser.parse_args()

    result = required_teams_per_arm(args.nbar, args.icc, args.r, args.cluster_loss)
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
