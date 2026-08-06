"""識学型・営業部行動管理プロトコル比較シミュレーション。

合成Monte Carlo実験であり、実績データから因果効果を推定するものではない。
"""
from pathlib import Path
import numpy as np
import pandas as pd

PROTOCOLS = {
    "P0_現状型": dict(clarity=.45, cadence=.35, authority=.50, change=.25, pressure=.30, admin=.20),
    "P1_KPI強化": dict(clarity=.70, cadence=.45, authority=.50, change=.30, pressure=.55, admin=.35),
    "P2_結果期限明確": dict(clarity=.85, cadence=.60, authority=.60, change=.40, pressure=.45, admin=.30),
    "P3_責任権限一致": dict(clarity=.85, cadence=.65, authority=.85, change=.50, pressure=.45, admin=.28),
    "P4_週報最適化": dict(clarity=.90, cadence=.85, authority=.85, change=.80, pressure=.40, admin=.22),
    "P5_過剰管理": dict(clarity=.95, cadence=.95, authority=.75, change=.70, pressure=.90, admin=.65),
}

def simulate(seed, p, n_agents=12, weeks=52):
    rng = np.random.default_rng(seed)
    skill = rng.normal(0, .35, n_agents)
    pipeline = rng.normal(0, .25, n_agents)
    fatigue = np.zeros(n_agents)
    sales, visits, proposals, overdue, quality, attrition = ([] for _ in range(6))
    for _ in range(weeks):
        ambiguity = 1 - p["clarity"]
        alignment = .45*p["clarity"] + .25*p["authority"] + .20*p["cadence"] + .10*p["change"]
        stress = max(0, p["pressure"]-.55) + .4*ambiguity + .25*(1-p["authority"])
        fatigue = np.clip(.72*fatigue + stress - .22*p["change"], 0, 2)
        activity = np.exp(1.2 + .22*skill + .28*pipeline + .55*alignment - .30*p["admin"] - .20*fatigue + rng.normal(0,.12,n_agents))
        v = rng.poisson(np.clip(activity*1.35, .1, None))
        e = rng.binomial(v, np.clip(.35+.20*p["clarity"]+.08*p["cadence"]-.05*fatigue,.05,.9))
        pr = rng.binomial(e, np.clip(.45+.20*p["clarity"]+.12*p["change"]-.06*fatigue,.05,.95))
        win_p = np.clip(.12+.08*p["clarity"]+.07*p["authority"]+.07*p["change"]+.04*p["cadence"]-.08*ambiguity-.06*fatigue,.02,.65)
        wins = rng.binomial(pr, win_p)
        rev = wins*np.exp(11.2+.08*skill+rng.normal(0,.18,n_agents))
        od = np.clip(.28+.35*ambiguity+.18*(1-p["cadence"])+.12*(1-p["authority"])+.08*fatigue-rng.normal(0,.03,n_agents),0,1)
        q = np.clip(.55+.20*p["clarity"]+.12*p["change"]+.10*p["authority"]-.10*fatigue+rng.normal(0,.03,n_agents),0,1)
        leave = np.clip(.002+.010*np.maximum(fatigue-.7,0)+.006*ambiguity,0,.08)
        sales.append(rev.sum()); visits.append(v.sum()); proposals.append(pr.sum())
        overdue.append(od.mean()); quality.append(q.mean()); attrition.append(leave.mean())
        pipeline = .75*pipeline + .04*(v-v.mean())/max(v.std(),1) + .08*p["change"] - .04*fatigue
        skill += .012*p["change"]*(q-.5) + rng.normal(0,.006,n_agents)
    annual_sales = sum(sales)
    target = n_agents*weeks*np.exp(11.2)*.55
    goal = annual_sales/target
    utility = goal + .55*np.mean(quality) - .75*np.mean(overdue) - 4*np.mean(attrition) - .20*p["admin"]
    return dict(annual_sales=annual_sales, goal_attainment=goal,
                proposal_rate=sum(proposals)/max(sum(visits),1),
                overdue_rate=np.mean(overdue), quality=np.mean(quality),
                attrition_risk=np.mean(attrition), admin_load=p["admin"], utility=utility)

def main():
    out = Path("results"); out.mkdir(exist_ok=True)
    rows = []
    for name, p in PROTOCOLS.items():
        for seed in range(500):
            row = simulate(seed, p); row.update(protocol=name, seed=seed); rows.append(row)
    raw = pd.DataFrame(rows)
    summary = raw.groupby("protocol").agg(
        annual_sales_mean=("annual_sales","mean"), annual_sales_sd=("annual_sales","std"),
        goal_attainment_mean=("goal_attainment","mean"), proposal_rate_mean=("proposal_rate","mean"),
        overdue_rate_mean=("overdue_rate","mean"), quality_mean=("quality","mean"),
        attrition_risk_mean=("attrition_risk","mean"), utility_mean=("utility","mean"),
        utility_sd=("utility","std")).reset_index()
    summary["rank"] = summary["utility_mean"].rank(ascending=False, method="min").astype(int)
    raw.to_csv(out/"simulation_raw.csv", index=False, encoding="utf-8-sig")
    summary.sort_values("rank").to_csv(out/"protocol_summary.csv", index=False, encoding="utf-8-sig")
    print(summary.sort_values("rank").to_string(index=False))

if __name__ == "__main__":
    main()
