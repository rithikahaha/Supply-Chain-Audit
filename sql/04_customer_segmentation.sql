-- Stage 4: Customer Segmentation (Value at Risk)
-- Buckets customers into spend tiers via a CTE, then checks whether SLA
-- failures are concentrated among high-value customers.

WITH UserValue AS (
    SELECT
        "Customer Id",
        SUM("Order Item Total") AS total_spent,
        AVG(Late_delivery_risk) AS delay_rate
    FROM supply_chain
    GROUP BY 1
)
SELECT
    CASE
        WHEN total_spent > 500 THEN 'Priority (High Spend)'
        WHEN total_spent BETWEEN 200 AND 500 THEN 'Standard (Mid Spend)'
        ELSE 'Casual (Low Spend)'
    END AS customer_segment,
    COUNT(*) AS user_count,
    ROUND(AVG(delay_rate) * 100, 2) AS avg_failure_pct
FROM UserValue
GROUP BY 1
ORDER BY avg_failure_pct DESC;
