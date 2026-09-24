# Project Guide

A plain-English walkthrough of what this project found, how I got there, and what I'd say if someone asked me about it.

## The short version

Customers who pay for faster shipping mostly don't get it. First Class promises delivery in 1 day, and not a single First Class order in the data arrived in 1 day. They all took 2. Second Class promises 2 days and takes about 4. Standard Class keeps its promise on average, and Same Day is close.

So the shipping network isn't broken. The promises on the checkout page are wrong. If the site showed delivery dates that match what actually happens, most of the missed-promise problem would disappear without changing anything in operations.

It also isn't a problem limited to a few unlucky customers. Big spenders and small spenders get late orders at about the same rate, around 55%.

## The data

The dataset is DataCo Smart Supply Chain from Kaggle. It has 180,519 rows, but a row is one item in an order, not one order. There are 65,752 actual orders. I mention this because the two numbers show up in different places and people get confused.

Each row has the shipping mode, how many days were promised, how many days it really took, the customer, the order value, and where it shipped. I used those and ignored most of the other columns.

## How I worked through it

**1. Check the data is trustworthy.** No zero-value orders, no deliveries over 10 days, nothing strange. The file needed ISO-8859-1 encoding to load because of accented city names. I dropped rows missing shipping days or a customer ID.

**2. Compare promise against reality.** For each shipping mode I checked what share of orders arrived within the promised days (strict), and what share arrived within one extra day (buffered). First Class: 0% strict, 100% buffered. Second Class: 20% strict, 40% buffered. Standard: 60% strict, 80% buffered. Same Day: 52% strict, 100% buffered.

**3. Measure the gap in days.** Average actual days minus promised days. Second Class is 1.99 days over. First Class is 1.0 day over. Same Day is 0.48 over. Standard is 0.0. Gaps that steady point to a fixed process problem, not random bad luck.

**4. Check whether valuable customers are hit harder.** I grouped customers by total spend (over $500, $200 to $500, under $200) and compared how often their orders were late. All three groups land between 54.5% and 55.9%. Nobody is being protected and nobody is being singled out.

**5. Test what happens if the promise is realistic.** I split orders into two halves. One half keeps the current promise. The other gets a promise set to the mode's real average delivery time, rounded up. Then I counted how many orders would have met their promise.

| Shipping mode | Current promise | Realistic promise | Met promise before | Met promise after |
| :--- | :---: | :---: | :---: | :---: |
| First Class | 1 day | 2 days | 0% | 100% |
| Same Day | 0 days | 1 day | 52% | 100% |
| Second Class | 2 days | 4 days | 20% | 60% |
| Standard Class | 4 days | 4 days | 60% | 60% |

Standard Class doesn't change because its promise was already the real average. The other three improve a lot, and the difference is statistically significant (I used a two-proportion z-test, which just asks whether a gap this big could happen by chance). For Standard Class it can, p = 0.95.

## What that last test does and doesn't prove

It's a simulation, not a live experiment. Nobody actually changed the checkout page. The "realistic promise" is calculated from the same delivery times I then score it against, so the improvement is close to guaranteed by how it's built. First Class hitting exactly 100% is the giveaway.

What it does show is how much room there is. If the site promised what really happens, this is the ceiling on how many orders could meet their promise. A real test would need to show different promises to different customers and watch what happens to complaints and repeat orders, which this dataset can't tell us.

## Two numbers that look like they disagree

The dashboard says First Class is late 95.3% of the time. The SQL says 0% of First Class orders arrive within the promise. Both are right. The 95.3% comes from a `Late_delivery_risk` flag that's already in the dataset. The 0% comes from my own comparison of actual days against promised days. They measure lateness slightly differently, and I use the dataset's flag on the dashboard and my own comparison in the SQL.

Same idea for the overall 54.83% on the dashboard. That's the dataset's flag averaged over everything. It's the same thing as "about 55%" in the segment analysis.

## PySpark and Snowflake

I reran the same five steps in PySpark and in Snowflake to check I'd get the same answers on different tools. I did. With 180K rows PySpark isn't needed, since Pandas handles it fine. The point was showing the logic carries over to data that would be too big for one machine. Only the original single-mode A/B test was rerun there. The all-modes z-test version exists only in `python/ab_test_simulation.py`.

## The dashboard

Live on [Tableau Public](https://public.tableau.com/app/profile/rithika.h8756/viz/SupplyChainSLAAudit/SupplyChainSLAAudit). It has a small metrics block (total orders, overall late rate, average gap), a chart of strict versus buffered success by shipping mode, a world map colored by late rate, a line chart of late rate by month, and the spend-tier chart that shows the flat 55%. The month chart is worth a look because every line stays flat all year. Seasonality isn't the cause.

Tableau Public workbooks are public, and anyone can download the data behind them. I removed names, emails, passwords and street addresses before publishing.

## What's in the repo

- `notebooks/` has the original Pandas and SQLite analysis, plus the PySpark version.
- `sql/` has one file per analysis step, and `sql/exports/` has the result of each as a small CSV.
- `python/prepare_dashboard_data.py` rebuilds the exports and the file Tableau reads.
- `python/ab_test_simulation.py` runs the promise test for every shipping mode.
- `data/` is empty on GitHub because the files are too big. The README says where to download the dataset.
- `dashboard/` has the build spec and a screenshot.

## Questions I'd expect

**Why does First Class show 95% late but 0% on time?** The two numbers come from different definitions of late. See the section above.

**Is the A/B test real?** No, it's a simulation, and I say so in the README. It shows the upside if promises were realistic. It can't show how customers would react.

**Why 55% and not something that varies?** Because the delay comes from the shipping mode, not from who the customer is. Every spend tier ships through the same modes in roughly the same mix.

**Why use PySpark on 180K rows?** To show the logic scales. I wouldn't pick it for this size in real work.

**What would you do next?** Run a real test on a slice of checkout traffic, with the realistic date shown to some customers, and compare complaints and repeat purchases against the rest.
