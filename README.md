# Telco Customer Churn: Who Leaves and What To Do First

## Question
About 1 in 4 customers leave. Which groups drive that, and where should retention start?

## Answer
- Overall churn is 26.5% (7,043 customers).
- Month-to-month fiber customers churn at 55%, 2.1x the average. This group is about 30% of customers but 62% of all churn, with roughly 1.2M in annual revenue lost.
- Contract type is the strongest driver (Cramer's V 0.41), followed by tenure, online security, tech support and internet service. Gender is near zero (0.008).

## Recommendations
1. Offer an incentive to move month-to-month customers onto 1-year plans.
2. Bundle online security and tech support for new fiber customers.
3. Review payment-method patterns (see charts) and test auto-pay prompts.

## Data
Kaggle: https://www.kaggle.com/datasets/blastchar/telco-customer-churn (IBM sample, 7,043 rows).

## Method
Cleaned data (11 blank TotalCharges values set to 0), calculated churn by segment, ranked drivers by Cramer's V, and sized the worst segment's revenue at risk. Charts are in /dashboard.

## Limits
Associations, not proof of cause. One snapshot of one company. Revenue at risk is an estimate (monthly charges x 12). Next step: A/B test the contract-upgrade offer.
