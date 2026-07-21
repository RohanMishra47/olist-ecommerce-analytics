# Olist E-Commerce — Analytical Findings

> **Dataset:** Brazilian E-Commerce Public Dataset by Olist (Kaggle)
> **Scope:** 99,441 orders · September 2016 – October 2018 · 9 relational tables
> **Stack:** SQLite → Python (pandas, matplotlib, seaborn) → Power BI

---

## Key Highlights

Three findings stand out as the most surprising or actionable across the entire analysis:

**1. Olist's backend drops a 180-day fallback timestamp when carrier estimation fails.**
Hundreds of orders appeared to have been delivered 100–150 days *ahead* of schedule — physically impossible given normal 1–7 day transit times. A sequential timestamp audit revealed the anomaly was entirely in `order_estimated_delivery_date`, not in actual logistics. When routing APIs failed at checkout, the platform defaulted to a worst-case 180-day estimate. These rows were excluded from all delay-based analysis and flagged for transparency.

**2. Review score is a noisy satisfaction signal, not a clean delivery metric.**
The review distribution is sharply bimodal — 57.78% five-star, with one-star (11.51%) as the *second* most common score, well ahead of 2, 3, and 4. A subset of orders received perfect 5-star ratings despite delays exceeding 100 days. Investigation revealed two drivers: accidental UI taps on mobile (empty comment fields), and genuine satisfaction for high-tolerance product types (handmade, customized, or imported items) where proactive seller communication decoupled delivery speed from final satisfaction.

**3. Top categories by revenue and by volume tell different business stories.**
`watches_gifts` ranks #2 by revenue but only #7 by order volume — a high price-point, lower-frequency category. `bed_bath_table` is the inverse: #1 by volume, #3 by revenue. A business optimizing for transaction count and one optimizing for revenue would prioritize entirely different categories.

---

## Section 1 — Sales & Revenue

### Total Scale
- **Total orders:** 99,441 across all statuses; **96,478 delivered** (97.02%)
- **Product Revenue** (price only, delivered orders): **R$ 13,221,498.11**
- **GMV** (price + freight, delivered orders): **R$ 15,419,773.75**
- **Implied total freight collected:** ~R$ 2,198,275 — roughly **16.6% of product revenue**
- **Date range:** September 4, 2016 – October 17, 2018 (grouped by `order_purchase_timestamp`)

### Revenue Trend
Monthly revenue followed three distinct phases:

| Phase | Period | Characteristics |
|---|---|---|
| Pilot | Sep–Dec 2016 | Near-zero volume; 1–265 orders/month |
| Ramp | Jan–Nov 2017 | Steep growth from R$127K to R$1.15M/month |
| Plateau | Dec 2017–Aug 2018 | Stable R$966K–R$1.13M/month range |

**November 2017** is the single largest month — 7,289 orders and R$1,153,364 GMV — consistent with Black Friday demand. The trend line has an incomplete tail at both ends: the 2016 pilot phase had very few orders, and the October 2018 data is a partial month (extract cutoff October 17).

### Order Status
97.02% of orders reached delivered status, reflecting Olist's strong fulfillment rate. Combined canceled + unavailable orders account for only 1.24% of total volume.

### Top Product Categories

**By Revenue (GMV):**

| Rank | Category | GMV | Unique Orders |
|---|---|---|---|
| 1 | Health & Beauty | R$1,412,090 | 8,647 |
| 2 | Watches & Gifts | R$1,264,333 | 5,495 |
| 3 | Bed, Bath & Table | R$1,225,209 | 9,272 |
| 4 | Sports & Leisure | R$1,118,257 | 7,530 |
| 5 | Computer Accessories | R$1,032,724 | 6,530 |

**By Order Volume:**

| Rank | Category | Unique Orders | GMV |
|---|---|---|---|
| 1 | Bed, Bath & Table | 9,272 | R$1,225,209 |
| 2 | Health & Beauty | 8,647 | R$1,412,090 |
| 3 | Sports & Leisure | 7,530 | R$1,118,257 |
| 4 | Computer Accessories | 6,530 | R$1,032,724 |
| 5 | Furniture & Decor | 6,307 | R$880,330 |

**Takeaway:** `Watches & Gifts` has an average GMV ~R$230/order vs. `Bed, Bath & Table` at ~R$132/order — nearly 75% higher revenue per transaction on roughly half the order volume. Categories that drive the most cash are not the same as those driving the most transactions.

### Payment Behavior
Credit card dominates at **74.03% of transactions**, with an average of **3.5 installments** — reflecting Brazil's deeply embedded installment payment culture. Boleto (bank slip) is the only meaningful alternative at 19.05%. Debit card and voucher together account for under 7%.

---

## Section 2 — Customers

### Geographic Concentration
Brazil's e-commerce market is heavily concentrated in the Southeast:

| State | Unique Customers | % of Orders |
|---|---|---|
| SP (São Paulo) | 40,302 | 41.92% |
| RJ (Rio de Janeiro) | 12,384 | 12.88% |
| MG (Minas Gerais) | 11,259 | 11.71% |

The top 3 states account for **66.51%** of all orders. The remaining 24 states share the rest, with several northern and central-western states (AC, AP, RR) each contributing under 0.1%.

### Repeat Purchase Behavior
- **96,136 unique customers** placed **99,441 total orders** — implying ~3,305 repeat purchases
- **Repeat purchase rate: 3.00%** of unique customers placed more than one order

The low repeat rate is a known characteristic of this dataset and likely reflects both the marketplace's relatively short operational window (2 years) and possible limitations in `customer_unique_id` linkage. It does not necessarily indicate poor retention — the 2-year window limits how many repeat cycles are observable.

### RFM Segmentation
Customers were segmented using Recency, Frequency, and Monetary (RFM) modeling based on their purchase behavior. Because Olist operates as a marketplace with a **97.00% single-purchase rate** (90,557 out of 93,358 unique customers ordered only once), the segment distribution is heavily influenced by purchase recency and monetary value:

* **At Risk (23.54% / 21,980 customers):** The largest group, consisting of older single-time buyers with low-to-moderate spend who have not purchased recently.
* **Lost Customers (16.45% / 15,362 customers):** Lapsed buyers with high recency (longest time since last order) and low overall spend.
* **Champions (16.18% / 15,108 customers):** Top-tier recent buyers who generated above-average order value (GMV).
* **Potential Loyalists (15.73% / 14,683 customers):** Recent buyers showing high potential with moderate transaction values.
* **Loyal Customers (8.19% / 7,649 customers):** Consistent, repeat, or higher-value transactions with strong recency.
* **Recent Customers & Need Attention (15.71% / 14,662 combined):** Newer buyers needing immediate re-engagement campaigns to prevent churn into "At Risk".
* **Others (4.19% / 3,914 customers):** Remaining tail end of customer segments.

> **Key Takeaway:** Over **40% of Olist's customer base sits in "At Risk" or "Lost" segments**, confirming that marketplace growth is currently driven almost entirely by new customer acquisition rather than retention or repeat purchases.

---

## Section 3 — Logistics

### Delivery Performance
- **Overall late delivery rate: 6.76%** of delivered orders arrived after the estimated date
- The bulk of orders are delivered *ahead* of schedule — Olist sets deliberately conservative estimates, and the delivery delay distribution is left-skewed (negative delay = early delivery)
- Typical actual delivery time peaks around **7–10 days** from purchase, with a long right tail extending to ~50 days for remote regions

### Late Delivery by State
Northern and northeastern states consistently show higher late delivery rates, reflecting the logistics reality of serving geographically remote areas far from SP-based seller concentration.

### Freight as % of Price
Freight represents a meaningful share of order value, particularly for:
- **Heavy or bulky categories** (furniture, mattresses) where physical weight drives carrier cost
- **Remote destination states** where inter-state shipping distances inflate freight relative to product price

Inter-state shipments carry materially higher freight burdens than intra-state, as expected given Brazil's geographic scale.

### Data Quality Finding — Placeholder Timestamps
A subset of orders showed `order_estimated_delivery_date` values 100–180 days beyond actual delivery. Sequential audit confirmed physical transit was normal (1–7 days). The inflated estimated dates originated from a backend fallback: when carrier routing APIs failed at checkout, the system inserted a 180-day worst-case timestamp. These rows were flagged as outliers and excluded from all delay-based metrics. Reporting delay figures without this exclusion would artificially inflate the "early delivery" rate.

---

## Section 4 — Satisfaction

### Review Score Overview
- **Global average (all orders):** 4.09
- **Delivered orders average (order-level):** 4.16
- The delivered-only figure is higher because canceled and unavailable orders tend to generate more negative reviews — a natural selection effect

### Score Distribution

| Score | Count | Share |
|---|---|---|
| 5 ⭐ | 57,328 | 57.78% |
| 4 ⭐ | 19,142 | 19.29% |
| 3 ⭐ | 8,179 | 8.24% |
| 2 ⭐ | 3,151 | 3.18% |
| 1 ⭐ | 11,424 | 11.51% |

The distribution is sharply **bimodal**: five-star dominates, and one-star is the second most common score — far ahead of 2, 3, and 4. This is a classic e-commerce review pattern where customers are far more likely to leave feedback at the extremes of their experience.

### Delivery Delay vs. Review Score
- **Pearson r (full dataset):** −0.27

The negative correlation confirms that longer delays associate with lower scores — directionally expected. However the relationship is modest (not strong), because review score is influenced by many factors beyond delivery timing: product quality, seller communication, and UI behavior all introduce noise.

**Anomaly — 5-star reviews on 100+ day delays:** Investigation identified two distinct sub-groups:
- **Accidental taps:** Empty comment fields suggest users dismissed mobile feedback prompts by tapping the top star rating without intent
- **Genuine satisfaction:** Written comments in this group explicitly praised sellers for customized, handmade, or imported items where long lead times were understood and accepted upfront

**Implication:** Review score should not be used as a direct proxy for delivery satisfaction without controlling for product category and comment presence. It is a useful signal at scale, but noisy at the individual order level.

### Review Score by Category
Categories with high average scores tend to be gift or experience-oriented (flowers, books, arts). Categories with lower average scores tend to involve complex logistics or higher customer expectations (electronics, computers, furniture) — where delivery condition and product accuracy matter more and disappoint more readily.

---

## Limitations & Caveats

**Date range:** The dataset covers September 2016 – October 2018. The first few months (2016) represent a pilot phase with very low order volumes that are not representative of steady-state operations. The October 2018 data is a partial month. Both endpoints should be treated with caution in trend analysis.

**Anonymized data:** All customer, seller, and product identifiers are anonymized UUIDs. No personally identifiable information is present. City and state fields are retained but zip codes are truncated.

**Repeat purchase rate:** The 3.00% figure is almost certainly understated. The `customer_unique_id` field links customers across orders, but its linkage accuracy over a 2-year window with address/device changes is unknown. The true repeat rate may be higher.

**Review score noise:** Two confirmed noise sources — accidental mobile UI taps (empty-comment 5-star reviews) and high-tolerance product-type satisfaction — reduce the reliability of review score as a precise satisfaction metric. Aggregate trends are valid; individual scores are not.

**Placeholder timestamp exclusions:** Rows with `order_estimated_delivery_date` inflated by the 180-day backend fallback were excluded from delivery delay metrics. These rows remain in the dataset with an outlier flag for transparency, and are visible in Power BI via the outlier severity slicer.

**Revenue definition:** "Product Revenue" refers to the sum of `price` from `olist_order_items_dataset`, scoped to delivered orders. "GMV" adds `freight_value` to that sum. Neither figure represents Olist's net revenue after marketplace fees — the dataset does not contain fee/commission data.
