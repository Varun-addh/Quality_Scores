import pandas as pd
import re
from typing import Optional, Callable

def completeness_score(column):
    """Calculate the completeness score of a column."""
    if len(column) == 0:
        return 0.0
    return (1 - column.isna().mean()) * 100

def uniqueness_score(column: pd.Series) -> float:
    """Calculate the percentage of unique values in a column."""
    if len(column) == 0:
        return 0.0
    return (column.nunique() / len(column)) * 100

def validity_score(
    column: pd.Series, 
    validation_func: Optional[Callable] = None
) -> float:
    """Calculate the percentage of valid values using custom validation rules."""
    if len(column) == 0:
        return 0.0
    
    if validation_func is None:
        # Default validation based on dtype
        if pd.api.types.is_numeric_dtype(column):
            validation_func = lambda x: not pd.isna(x)
        elif pd.api.types.is_datetime64_any_dtype(column):
            validation_func = lambda x: not pd.isna(x)
        else:
            validation_func = lambda x: isinstance(x, str) and x.strip() != ""
    
    return column.apply(validation_func).mean() * 100

# def timeliness_score(column, threshold_date):
#     """Calculate the timeliness score of a datetime column."""
#     if pd.api.types.is_datetime64_any_dtype(column):
#         if threshold_date is None:
#             raise ValueError("Threshold date must be provided and cannot be None.")
        
#         threshold_date = pd.to_datetime(threshold_date).tz_localize(None)
#         timely_entries = (column >= threshold_date).sum()
#         return timely_entries / len(column) * 100

#     return 100.0  # If not a datetime column, assume 100% timeliness

def accuracy_score(
    reference_df: pd.DataFrame,
    target_df: pd.DataFrame,
    column_name: str
) -> float:
    """Calculate the percentage of matching values between two DataFrames."""
    for df in [reference_df, target_df]:
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' missing in DataFrame")
    
    ref_col = reference_df[column_name]
    target_col = target_df[column_name]
    
    if len(ref_col) != len(target_col):
        raise ValueError("DataFrames must have the same length")
    
    # Consider matching NaN as correct
    matches = (ref_col == target_col) | (ref_col.isna() & target_col.isna())
    return matches.mean() * 100


# def accuracy_score(df, df2, column_name, threshold=None):
#     """Calculates the accuracy score between two DataFrames for a specific column."""
    
#     # Check if the column exists in both DataFrames
#     missing_columns = []
#     if column_name not in df.columns:
#         missing_columns.append(f"'{column_name}' in the first DataFrame")
#     if column_name not in df2.columns:
#         missing_columns.append(f"'{column_name}' in the second DataFrame")
    
#     if missing_columns:
#         raise ValueError(f"Column(s) missing: " + ", ".join(missing_columns))
    
#     # Extract the columns to compare
#     col1 = df[column_name]
#     col2 = df2[column_name]
    
#     # Create a mask for non-missing values in both columns
#     non_missing_mask = ~col1.isna() & ~col2.isna()
    
#     # Count correct matches only for non-missing values
#     correct_entries = (col1[non_missing_mask] == col2[non_missing_mask]).sum()
    
#     # Total entries to consider include non-missing and mismatched entries
#     total_entries = len(col1)
    
#     # Calculate accuracy percentage
#     accuracy_percentage = (correct_entries / total_entries) * 100 if total_entries > 0 else 0
    
#     return accuracy_percentage



def consistency_score(
    reference_df: pd.DataFrame,
    target_df: pd.DataFrame,
    reference_col: str,
    target_col: Optional[str] = None
) -> float:
    """Calculate consistency between related columns in two DataFrames."""
    target_col = target_col or reference_col
    for col, df in [(reference_col, reference_df), (target_col, target_df)]:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' missing in DataFrame")
    
    ref_series = reference_df[reference_col]
    target_series = target_df[target_col]
    
    # Vectorized comparison
    consistent = (ref_series == target_series) | (ref_series.isna() & target_series.isna())
    return consistent.mean() * 100

def calculate_scores(df, df2, selected_metrics=None, threshold_date=None):

    if selected_metrics is None:
        selected_metrics = ["Completeness", "Validity", "Uniqueness", "Accuracy", "Consistency"]
    
    if threshold_date is None:
        threshold_date = pd.to_datetime("today")
    
    detailed_scores = {}
    for col in df.columns:
        column_data = df[col]
        column_scores = {}

        if "Completeness" in selected_metrics:
            column_scores["Completeness"] = completeness_score(column_data)

        if "Uniqueness" in selected_metrics:
            column_scores["Uniqueness"] = uniqueness_score(column_data)

        if "Validity" in selected_metrics:
            column_scores["Validity"] = validity_score(
                column_data,
                lambda x: bool(
                    re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", str(x))
                ),
            ) if "email" in col.lower() else 100

        if "Accuracy" in selected_metrics:
            column_scores["Accuracy"] = accuracy_score(df, df2, col)

        if "Consistency" in selected_metrics:
            column_scores["Consistency"] = consistency_score(df, df2, col)

        detailed_scores[col] = column_scores

    scores_df = pd.DataFrame(detailed_scores).T
    return scores_df

def overall_quality_score(scores_df, selected_metrics=None):
    """Calculate the overall quality score based on selected metrics."""
    if selected_metrics is None:
        selected_metrics = scores_df.columns
    return scores_df[selected_metrics].mean().mean()
