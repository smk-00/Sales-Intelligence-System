# Risk Scoring Model Documentation

This document describes the end-to-end approach for building and using a **Deal Risk Scoring** model (XGBoost) that outputs a probability.

**0 → 1**, where **1 = likely Won**.

**0 = high chance of Losing**.

## Overall Approach

We transform raw CRM deal data into model-ready numeric features, train an XGBoost classifier to predict **deal outcome**, and use the predicted probability (`p_win`) as the **risk score** for open deals. During inference, we recompute time-dependent features (like sales cycle) using the **current date** so the model can score live/open deals accurately.

---

## 1. Data Preparation

The preprocessing converts raw sales data into model-ready features:

### Date handling

- Convert `created_date` and `closed_date` into datetime types.
- **Drop `created_date` and `closed_date` from training features** (model does not directly train on raw timestamps).
- To help the model learn time-related patterns, we extract:
  - **`created_month`** only (month has an order-like structure and captures seasonality trends).

### Feature engineering

- **`created_month`**: extracted from `created_date`.
- **`amount_bucket`**: bucketize `deal_amount` into 3 quantiles using `qcut` (labels: 1,2,3) to capture non-linear deal size effects.
- **`sales_cycle_days`**:
  - Used during training (from historic deals).
  - During inference (open deals), **computed as:** `current_date - created_date`.

### Target mapping

- `outcome` mapped to binary:
  - `Won = 1`, `Lost = 0`

### Categorical encoding (Label Encoding)

Categorical fields are mapped into integer IDs:

- `sales_rep_id`, `industry`, `region`, `product_type`, `lead_source`, `deal_stage`

> Note: XGBoost can work well with integer-encoded categories in many practical setups and avoids the high dimensionality of one-hot encoding.

---

## 2. Model Training

### Training objective

- Train an **XGBoost classifier** to predict `outcome` (Won/Lost).
- Output probability is used as `p_win` (win likelihood).

### Validation strategy (Stratified K-Fold)

- Uses **Stratified K-Fold Cross-Validation (k = 3)**  
  - Ensures each fold preserves the Won/Lost ratio.
  - Helps estimate performance on unseen data and reduces overfitting to a single split.

### Features used

The model uses a mix of deal context, process, rep, and time-derived features:

| Feature Category | Features | Why it helps |
| :--- | :--- | :--- |
| Deal Value | `deal_amount`, `amount_bucket` | Deal size impacts scrutiny, cycle length, and close probability. |
| Timing / Velocity | `sales_cycle_days` | Stale deals are less likely to close; often highly predictive. |
| Seasonality | `created_month` | Captures monthly seasonality patterns and ordering. |
| Deal Context | `industry`, `region`, `product_type` | Different segments convert differently. |
| Sales Process | `deal_stage`, `lead_source` | Stage reflects progress; lead source impacts quality. |
| Rep Performance | `sales_rep_id` | Captures rep-level conversion differences historically. |

---

## 3. Inference (Deal Risk Scoring)

### When scoring runs

- **On new deal creation:** score immediately.
- **On deal stage updates:** rescore immediately.

### How inference differs from training

- **No `closed_date` exists** for open deals, so it is not used.
- **`sales_cycle_days` is recomputed at scoring time** using:
  - `sales_cycle_days = current_date - created_date`
- Apply the same encodings and feature transformations as training.

### Output

- Model returns `p_win ∈ [0, 1]`
  - `p_win` close to **1** → likely Won
  - `p_win` close to **0** → high risk of Losing

This probability is stored and used downstream for:

- risk alerts (score drops / low score)
- stall detection
- CRO dashboards and prioritization
