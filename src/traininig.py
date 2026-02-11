import pandas as pd
import joblib
import xgboost as xgb
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from data_prep import clean_and_feature_engineer, fit_encoders, encode_data

def train():
    """Train XGBoost model and save artifacts."""
    file_path = "./data/skygeni_sales_data.csv"
    print(f"Loading data from {file_path}...")
    df = pd.read_csv(file_path)

    print("Cleaning and engineering features...")
    df = clean_and_feature_engineer(df)
    df = df.dropna(subset=['target'])

    print("Fitting encoders...")
    encoders = fit_encoders(df)
    df_encoded = encode_data(df, encoders)

    feature_cols = [
        'deal_amount', 'sales_cycle_days', 'created_month', 'created_quarter', 'created_dow',
        'industry_encoded', 'region_encoded', 'product_type_encoded', 'lead_source_encoded',
        'amount_bucket_encoded', 'sales_rep_id_encoded', 'deal_stage_encoded'
    ]

    print("Saving test set...")
    df_train_raw, df_test_raw = train_test_split(pd.read_csv(file_path), test_size=0.2, random_state=42)
    df_test_raw.to_csv("./data/test_data_for_inference.csv", index=False)

    X = df_encoded.loc[df_train_raw.index, feature_cols]
    y = df_encoded.loc[df_train_raw.index, 'target']

    print("Training XGBoost Model...")
    model = xgb.XGBClassifier(
        objective='binary:logistic', eval_metric='logloss', use_label_encoder=False,
        n_estimators=100, max_depth=4, learning_rate=0.1
    )

    cv_scores = cross_val_score(model, X, y, cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=42), scoring='accuracy')
    print(f"Mean CV Accuracy: {cv_scores.mean():.4f}")

    model.fit(X, y)
    
    print("Saving artifacts...")
    joblib.dump(model, './pkl/risk_model.pkl')
    joblib.dump(encoders, './pkl/encoders.pkl')
    joblib.dump(feature_cols, './pkl/feature_cols.pkl')
    print("Training complete.")

train()
