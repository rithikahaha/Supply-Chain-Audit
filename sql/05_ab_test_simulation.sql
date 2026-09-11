-- Stage 5: A/B Test Simulation (Success Recovery)
-- Splits First Class orders into a control (1-day promise) and a variant
-- (4-day realistic estimate) using Order Id parity, then compares
-- fulfillment success rates between the two.

SELECT
    CASE WHEN ("Order Id" % 2 = 0) THEN 'Control (1-Day Promise)' ELSE 'Variant (4-Day Estimate)' END AS test_group,
    ROUND(AVG(CASE
        WHEN ("Order Id" % 2 != 0 AND "Days for shipping (real)" <= 4) THEN 1.0
        WHEN ("Order Id" % 2 = 0 AND "Days for shipping (real)" <= "Days for shipment (scheduled)") THEN 1.0
        ELSE 0.0
    END) * 100, 2) AS fulfillment_success_rate
FROM supply_chain
WHERE "Shipping Mode" = 'First Class'
GROUP BY 1;
