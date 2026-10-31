"""Do the payment-method and tech-support findings survive a confounder check?

Electronic check users are mostly month-to-month customers, and customers
without tech support are more likely to be on fiber. Both findings could be
another driver in disguise. This script:
  1. shows the contract mix of each payment method,
  2. compares churn by payment method WITHIN each contract group,
  3. fits a logistic regression that holds contract, tenure, monthly charges
     and internet service constant.

  4. repeats the tech-support comparison within each internet service type.

Usage:  python confounder_checks.py [path/to/csv]
"""
import sys
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

DEFAULT_PATH = "data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv"
path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH

df = pd.read_csv(path)
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)
df["churn"] = (df["Churn"] == "Yes").astype(int)
df["contract_group"] = np.where(df["Contract"] == "Month-to-month",
                                "Month-to-month", "1-2 year")

print("\n1) Contract mix by payment method (% of each method's customers)")
mix = pd.crosstab(df["PaymentMethod"], df["Contract"], normalize="index") * 100
print(mix.round(1))

print("\n2) Churn % by payment method, within each contract group")
strat = (df.groupby(["contract_group", "PaymentMethod"])["churn"]
           .agg(churn_pct=lambda s: round(s.mean() * 100, 1), customers="count"))
print(strat)
strat.to_csv("payment_method_stratified.csv")

print("\n3) Adjusted effect of electronic check (logistic regression)")
df["echeck"] = (df["PaymentMethod"] == "Electronic check").astype(int)
model = smf.logit(
    "churn ~ echeck + C(Contract) + tenure + MonthlyCharges + C(InternetService)",
    data=df).fit(disp=0)
odds = np.exp(model.params["echeck"])
lo, hi = np.exp(model.conf_int().loc["echeck"])
print(f"Odds ratio {odds:.2f} (95% CI {lo:.2f} to {hi:.2f}), holding contract, "
      "tenure, monthly charges and internet service constant.")

print("\n4) Churn % by tech support, within each internet service type")
net = df[df["InternetService"] != "No"]
tech = (net.groupby(["InternetService", "TechSupport"])["churn"]
           .agg(churn_pct=lambda s: round(s.mean() * 100, 1), customers="count"))
print(tech)
tech.to_csv("tech_support_stratified.csv")
print("\nSaved: payment_method_stratified.csv, tech_support_stratified.csv")
