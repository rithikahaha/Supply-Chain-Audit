-- Stage 2: SLA Performance (The Promise Test)
-- Strict success = arrived on/before the promised date.
-- Buffered success = arrived within a 1-day grace period.
-- Comparing the two shows whether failures are marginal misses or a
-- systemic gap between what's promised and what's delivered.

SELECT
    "Shipping Mode",
    COUNT(*) AS order_volume,
    ROUND(AVG(CASE WHEN "Days for shipping (real)" <= "Days for shipment (scheduled)" THEN 1.0 ELSE 0.0 END) * 100, 2) AS strict_success_rate,
    ROUND(AVG(CASE WHEN "Days for shipping (real)" <= ("Days for shipment (scheduled)" + 1) THEN 1.0 ELSE 0.0 END) * 100, 2) AS buffered_success_rate
FROM supply_chain
GROUP BY 1
ORDER BY order_volume DESC;
