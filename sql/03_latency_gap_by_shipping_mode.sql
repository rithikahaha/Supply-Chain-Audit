-- Stage 3: Fulfillment Funnel (The Latency Gap)
-- Latency Gap = Actual Days - Promised Days, averaged per shipping mode.
-- Isolates which tier is "leaking" the most time in the fulfillment funnel.

SELECT
    "Shipping Mode",
    AVG("Days for shipment (scheduled)") AS promised_days,
    AVG("Days for shipping (real)") AS actual_days,
    ROUND(AVG("Days for shipping (real)" - "Days for shipment (scheduled)"), 2) AS avg_latency_gap
FROM supply_chain
GROUP BY 1
ORDER BY avg_latency_gap DESC;
