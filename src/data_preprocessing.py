import numpy as np 
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def update_date_dtype(data):
    data = data.copy()
    data["created_date"] = pd.to_datetime(data["created_date"])
    data["closed_date"] = pd.to_datetime(data["closed_date"])
    return data


def categorical_encoding(data):
    data = data.copy()

    # Mapping the categroes to the numerical number
    sales_rep_id_map = {k:v+1 for v, k in enumerate(data["sales_rep_id"].unique())}
    industry_map = {k:v+1 for v, k in enumerate(data["industry"].unique())}
    region_map = {k:v+1 for v, k in enumerate(data["region"].unique())}
    product_type_map = {k:v+1 for v, k in enumerate(data["product_type"].unique())}
    lead_source_map = {k:v+1 for v, k in enumerate(data["lead_source"].unique())}
    deal_stage_map = {k:v+1 for v, k in enumerate(data["deal_stage"].unique())}
    outcome_map = {"Lost":0, "Won":1}

    # Replacing the categories string to integer label
    data["sales_rep_id"].replace(sales_rep_id_map, inplace=True)
    data["industry"].replace(industry_map, inplace=True)
    data["region"].replace(region_map, inplace=True)
    data["product_type"].replace(product_type_map, inplace=True)
    data["lead_source"].replace(lead_source_map, inplace=True)
    data["deal_stage"].replace(deal_stage_map, inplace=True)
    data["outcome"].replace(outcome_map, inplace=True)

    return data

def feature_engineering(data):
    data = data.copy()
    data['created_month'] = data['created_date'].dt.month
    data['amount_bucket'] = pd.qcut(data['deal_amount'], q=3, labels=[1, 2, 3])
    return data

