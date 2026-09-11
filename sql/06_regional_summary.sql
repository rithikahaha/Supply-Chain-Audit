-- Bonus: Regional Summary (feeds the dashboard's geo map)
-- Order volume, SLA breach rate, and revenue by market/region/country.

SELECT
    "Market",
    "Order Region",
    "Order Country",
    COUNT(*) AS order_volume,
    ROUND(AVG("Days for shipping (real)" - "Days for shipment (scheduled)"), 2) AS avg_latency_gap,
    ROUND(AVG(Late_delivery_risk) * 100, 2) AS sla_breach_rate,
    ROUND(SUM(Sales), 2) AS total_sales
FROM supply_chain
GROUP BY 1, 2, 3
ORDER BY order_volume DESC;
