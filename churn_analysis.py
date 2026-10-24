"""
Project 6: Customer Churn Drivers (Telco)
Run: python churn_analysis.py
Needs: pip install pandas numpy scipy matplotlib
Put the Kaggle CSV at data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency

os.makedirs("dashboard", exist_ok=True)
os.makedirs("data/clean", exist_ok=True)

# ---------- 1. Load and clean (log every step) ----------
df = pd.read_csv("data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv")
n0 = len(df)
blank = (df["TotalCharges"].astype(str).str.strip() == "").sum()
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)
df["churn"] = (df["Churn"] == "Yes").astype(int)
df["tenure_band"] = pd.cut(df["tenure"], [-1, 12, 24, 48, 100],
                           labels=["0-12", "13-24", "25-48", "49+"])
print(f"Rows: {n0:,} | blank TotalCharges set to 0: {blank}")
overall = df["churn"].mean()
print(f"Overall churn rate: {overall:.1%}")

# ---------- 2. Rank drivers by effect size (Cramer's V) ----------
def cramers_v(a, b):
    t = pd.crosstab(a, b)
    chi2 = chi2_contingency(t)[0]
    return np.sqrt(chi2 / (t.values.sum() * (min(t.shape) - 1)))

drivers = ["Contract", "tenure_band", "InternetService", "PaymentMethod",
           "TechSupport", "OnlineSecurity", "PaperlessBilling", "gender"]
ranking = pd.Series({d: cramers_v(df[d], df["churn"]) for d in drivers}
                    ).sort_values(ascending=False)
print("\nDriver strength (Cramer's V, higher = stronger):")
print(ranking.round(3))

# ---------- 3. Charts (one message each) ----------
def churn_chart(col):
    t = df.groupby(col, observed=True)["churn"].agg(["mean", "size"]).sort_values("mean")
    colors = ["#DC2626" if v > overall else "#94A3B8" for v in t["mean"]]
    ax = (t["mean"] * 100).plot.barh(color=colors, figsize=(7, 3.5))
    for i, (m, n) in enumerate(zip(t["mean"], t["size"])):
        ax.text(m * 100 + 0.5, i, f"{m:.0%} (n={n:,})", va="center", fontsize=8)
    ax.axvline(overall * 100, color="#14213D", linestyle="--")
    ax.set_xlabel("Churn rate, %")
    ax.set_title(f"Churn by {col} (dashed = average {overall:.0%})", loc="left")
    plt.tight_layout()
    plt.savefig(f"dashboard/churn_by_{col}.png", dpi=160)
    plt.close()

for c in ["Contract", "tenure_band", "InternetService", "PaymentMethod", "TechSupport"]:
    churn_chart(c)

# ---------- 4. Worst segment and revenue at risk ----------
seg = df[(df["Contract"] == "Month-to-month") & (df["InternetService"] == "Fiber optic")]
seg_churn = seg["churn"].mean()
lift = seg_churn / overall
at_risk = seg.loc[seg["churn"] == 1, "MonthlyCharges"].sum() * 12
share = seg["churn"].sum() / df["churn"].sum()
print(f"\nWorst segment: month-to-month + fiber")
print(f"  customers: {len(seg):,} | churn: {seg_churn:.0%} | lift: {lift:.1f}x average")
print(f"  share of ALL churn: {share:.0%}")
print(f"  annual revenue lost from this segment's churners: {at_risk:,.0f}")

# ---------- 5. Export clean file for Power BI ----------
df.to_csv("data/clean/telco_clean.csv", index=False)
print("\nSaved charts to dashboard/ and clean data to data/clean/telco_clean.csv")
