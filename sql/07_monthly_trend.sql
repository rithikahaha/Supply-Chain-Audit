-- Bonus: Monthly Trend (feeds the dashboard's time-series view)
-- Order volume, latency gap, and SLA breach rate by month and shipping mode.

SELECT
    strftime('%Y-%m', "order date (DateOrders)") AS order_month,
    "Shipping Mode",
    COUNT(*) AS order_volume,
    ROUND(AVG("Days for shipping (real)" - "Days for shipment (scheduled)"), 2) AS avg_latency_gap,
    ROUND(AVG(Late_delivery_risk) * 100, 2) AS sla_breach_rate
FROM supply_chain
GROUP BY 1, 2
ORDER BY 1, 2;
