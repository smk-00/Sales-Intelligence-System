import joblib
import numpy as np
import pandas as pd


def load_xgb_artifacts(path="models/xgb_sales_model.joblib"):
    return joblib.load(path)


def predict_with_saved_model(
    df_new: pd.DataFrame,
    artifacts: dict,
    proba_threshold=0.5,
):
    """
    Returns:
      - proba: win probability
      - pred: 0/1 using threshold
    """
    model = artifacts["model"]
    feature_columns = artifacts["feature_columns"]

    # Ensure required columns exist
    missing = [c for c in feature_columns if c not in df_new.columns]
    if missing:
        raise ValueError(f"Missing required feature columns: {missing}")

    X_new = df_new[feature_columns].copy()
    X_new = X_new.replace([np.inf, -np.inf], np.nan)

    proba = model.predict_proba(X_new)[:, 1]
    pred = (proba >= proba_threshold).astype(int)

    out = df_new.copy()
    out["pred_win_proba"] = proba
    out["pred_outcome"] = pred
    return out



sample_data = {'sales_rep_id': {0: 1},
 'industry': {0: 1},
 'region': {0: 1},
 'product_type': {0: 1},
 'lead_source': {0: 1},
 'deal_stage': {0: 1},
 'sales_cycle_days': {0: 5},
 'created_month': {0: 10}}

inference_data = pd.DataFrame(sample_data)
loaded = load_xgb_artifacts("models/xgb_sales_model.joblib")

prediction = predict_with_saved_model(inference_data, loaded)

print(prediction)