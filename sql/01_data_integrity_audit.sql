-- Stage 1: Data Integrity Audit
-- Checks for duplicate order IDs, zero/negative-value transactions, and
-- extreme shipping-time outliers before any SLA metric is trusted.

SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT "Order Id") AS unique_orders,
    SUM(CASE WHEN "Order Item Total" <= 0 THEN 1 ELSE 0 END) AS price_errors,
    SUM(CASE WHEN "Days for shipping (real)" > 10 THEN 1 ELSE 0 END) AS extreme_delays
FROM supply_chain;
