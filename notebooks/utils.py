import numpy as np 
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# ------------------------------- PRE PROCESSING ------------------------------- 
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



# ------------------------------- VISUALIZATION ------------------------------- 

def plot_dist(train_data, col_name, label_col="outcome", bins=20):
    """
        The function plots the specific column distribution of values with respect to the outcome.
    """
    fig = go.Figure()

    for label in sorted(train_data[label_col].unique()):
        subset = train_data[train_data[label_col] == label][col_name].dropna()

        fig.add_trace(
            go.Histogram(
                x=subset,
                nbinsx=bins,
                name=f"{label_col}={label}",
                opacity=0.6
            )
        )

    fig.update_layout(
        barmode="stack",  # important for overlapping
        title=f"{col_name} Distribution by {label_col}",
        xaxis_title=col_name,
        yaxis_title="Count",
        template="plotly_white"
    )

    fig.show()




def plot_dist_grid(train_data, col_grid, label_col="outcome", bins=20):
    """
        The function plots the column distribution of values with respect to the outcome.
    """

    rows = len(col_grid)
    cols = len(col_grid[0])

    # fixed color mapping
    color_map = {
        1: "#D22D3E",   # Heart disease
        0: "#2DD2C1"    # No heart disease
    }

    fig = make_subplots(
        rows=rows,
        cols=cols,
        subplot_titles=[col for row in col_grid for col in row]
    )

    for r in range(rows):
        for c in range(cols):
            col_name = col_grid[r][c]

            for label in sorted(train_data[label_col].unique()):
                subset = train_data[train_data[label_col] == label][col_name].dropna()

                fig.add_trace(
                    go.Histogram(
                        x=subset,
                        nbinsx=bins,
                        name=f"{label_col}={label}",
                        opacity=0.65,
                        marker_color=color_map[label],   # ⭐ fixed color
                        showlegend=(r == 0 and c == 0)
                    ),
                    row=r+1,
                    col=c+1
                )

    fig.update_layout(
        barmode="overlay",   # overlay > stack for comparison
        template="plotly_white",
        height=300*rows,
        width=500*cols,
        legend_title_text="Class"
    )

    fig.show()