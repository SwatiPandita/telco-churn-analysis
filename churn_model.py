"""
Project 6 upgrade: can we predict who will churn, and who should retention call first?
Run AFTER churn_analysis.py, in the same folder (or the same Colab notebook).
Needs: pandas numpy scikit-learn   (pip install scikit-learn)
"""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# ---------- 0. Load (same file the main script reads) ----------
df = pd.read_csv("data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv")
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)
y = (df["Churn"] == "Yes").astype(int)
X = df.drop(columns=["customerID", "Churn"])
num = ["SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges"]
cat = [c for c in X.columns if c not in num]

prep = ColumnTransformer([
    ("num", StandardScaler(), num),
    ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), cat),
])
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# ---------- 1. Cross-validated accuracy of two models ----------
logit = Pipeline([("prep", prep), ("m", LogisticRegression(max_iter=2000))])
boost = Pipeline([("prep", prep), ("m", HistGradientBoostingClassifier(random_state=42))])

p_logit = cross_val_predict(logit, X, y, cv=cv, method="predict_proba")[:, 1]
p_boost = cross_val_predict(boost, X, y, cv=cv, method="predict_proba")[:, 1]
print("1. CROSS-VALIDATED AUC (5 folds, every prediction is on unseen customers)")
print(f"   logistic regression:  {roc_auc_score(y, p_logit):.3f}")
print(f"   gradient boosting:    {roc_auc_score(y, p_boost):.3f}")
print("   0.5 = coin flip, 1.0 = perfect. Both models see only data a company would have.\n")

# ---------- 2. Does contract still matter after controlling for everything else? ----------
logit.fit(X, y)
names = logit.named_steps["prep"].get_feature_names_out()
coefs = pd.Series(logit.named_steps["m"].coef_[0], index=names)
key = [n for n in names if n == "cat__Contract_Two year"]
if key:
    or_two = np.exp(-coefs[key[0]])
    print("2. ADJUSTED EFFECT (holding all other columns constant)")
    print(f"   month-to-month vs two-year contract: odds of churn are about {or_two:.1f}x higher")
    print("   (an odds ratio, not a probability ratio; still an association, not proof of cause)\n")

# ---------- 3. Who should retention call first? ----------
best = p_logit if roc_auc_score(y, p_logit) >= roc_auc_score(y, p_boost) else p_boost
d = df.assign(churn=y.values, risk=best).sort_values("risk", ascending=False)
d["annual_rev"] = d["MonthlyCharges"] * 12
total_churners = d["churn"].sum()
print("3. TARGETING: call the highest-risk customers first")
print("   contact top...   churners reached   vs random calling   lift")
for pct in (0.10, 0.20, 0.30):
    k = int(len(d) * pct)
    caught = d.head(k)["churn"].sum() / total_churners
    print(f"   {pct:>4.0%} of customers   {caught:>6.0%}             {pct:>6.0%}            {caught / pct:.1f}x")
print()

# ---------- 4. What is it worth? (assumption-based scenario) ----------
k = int(len(d) * 0.20)
top = d.head(k)
rev_at_risk = (top["churn"] * top["annual_rev"]).sum()
print("4. SCENARIO: call the top 20% by predicted risk")
print(f"   annual revenue of the churners inside this group: {rev_at_risk:,.0f}")
print("   ASSUMPTION (not a result): a retention offer saves X% of those churners")
for s in (0.10, 0.20, 0.30):
    print(f"   save {s:.0%} -> about {rev_at_risk * s:,.0f} per year retained")
print("   The true save rate must come from an A/B test (Project 8).")