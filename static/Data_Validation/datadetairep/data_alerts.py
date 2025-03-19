from collections import defaultdict

def generate_data_alerts(df, config=None):

    # Default configuration
    default_config = {
        'correlation_threshold': 0.85,
        'skew_threshold': 1.0,
        'kurtosis_threshold': 3.0,
        'low_cardinality_threshold': 5,
        'high_uniqueness_threshold': 0.95,
        'exclude_cols': [],
        'allowed_negative_cols': [],
        'outlier_sd_threshold': 3,
        'date_columns': []
    }
    import numpy as np
    import pandas as pd
    
    config = {**default_config, **(config or {})}
    alerts = []
    excluded_cols = set(config['exclude_cols'])
    
    # Helper function to check if column should be processed
    def should_process(col):
        return col not in excluded_cols
    
    if df.empty:
        return ["CRITICAL: Input DataFrame is completely empty"]
    
    # Missing Values Analysis
    missing_values = df.isna().sum()
    for col, count in missing_values.items():
        if should_process(col) and count > 0:
            pct_missing = (count / len(df)) * 100
            level = "CRITICAL" if pct_missing > 30 else "WARNING"
            alerts.append(
                f"{level}: '{col}' has {count} missing values ({pct_missing:.1f}%)"
            )
    
    # Duplicate Analysis
    duplicate_rows = df.duplicated().sum()
    if duplicate_rows > 0:
        pct_dupes = (duplicate_rows / len(df)) * 100
        level = "CRITICAL" if pct_dupes > 10 else "WARNING"
        alerts.append(
            f"{level}: {duplicate_rows} duplicate rows ({pct_dupes:.1f}%) detected"
        )
    
    # 2. Numerical Value Checks
    numeric_cols = df.select_dtypes(include=np.number).columns
    
    # Negative Values
    for col in numeric_cols:
        if should_process(col) and col not in config['allowed_negative_cols']:
            negative_count = (df[col] < 0).sum()
            if negative_count > 0:
                alerts.append(
                    f"WARNING: '{col}' contains {negative_count} negative values"
                )
    
    # Zero Values
    for col in numeric_cols:
        if should_process(col):
            zero_count = (df[col] == 0).sum()
            if zero_count > len(df) * 0.5:  # More than 50% zeros
                alerts.append(
                    f"WARNING: '{col}' contains {zero_count} zero values ({zero_count/len(df):.1%})"
                )
    
    # Outlier Detection
    for col in numeric_cols:
        if should_process(col):
            z_scores = (df[col] - df[col].mean()) / df[col].std()
            outlier_count = (np.abs(z_scores) > config['outlier_sd_threshold']).sum()
            if outlier_count > 0:
                alerts.append(
                    f"WARNING: '{col}' contains {outlier_count} outliers (±{config['outlier_sd_threshold']} SD)"
                )
    
    # 3. Correlation Analysis
    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr().abs()
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        high_corr_pairs = upper.stack()
        high_corr_pairs = high_corr_pairs[high_corr_pairs > config['correlation_threshold']]
        
        correlated_features = defaultdict(set)
        for (col1, col2), value in high_corr_pairs.items():
            if should_process(col1) and should_process(col2):
                correlated_features[col1].add(col2)
                correlated_features[col2].add(col1)
                alerts.append(
                    f"WARNING: High correlation between '{col1}' and '{col2}' ({value:.2f})"
                )
        
        for col, corr_cols in correlated_features.items():
            if len(corr_cols) > 2:
                alerts.append(
                    f"WARNING: '{col}' correlates with {len(corr_cols)} other features"
                )
    
    # 4.Distribution Checks
    # Skewness and Kurtosis
    for col in numeric_cols:
        if should_process(col):
            skew = df[col].skew()
            if abs(skew) > config['skew_threshold']:
                alerts.append(
                    f"NOTICE: '{col}' shows significant skewness ({skew:.2f})"
                )
            
            kurt = df[col].kurtosis()
            if abs(kurt) > config['kurtosis_threshold']:
                alerts.append(
                    f"NOTICE: '{col}' shows significant kurtosis ({kurt:.2f})"
                )
    
    # 5. Cardinality Checks
    for col in df.columns:
        if should_process(col):
            # Skip numeric columns with many unique values
            if col in numeric_cols and df[col].nunique() > 100:
                continue
                
            unique_count = df[col].nunique()
            total_count = len(df)
            
            # Low cardinality check
            if unique_count == 1:
                alerts.append(f"CRITICAL: '{col}' has only 1 unique value")
            elif df[col].dtype == 'object' and unique_count < config['low_cardinality_threshold']:
                alerts.append(
                    f"NOTICE: '{col}' has low cardinality ({unique_count} unique values)"
                )
            
            # High uniqueness check
            unique_ratio = unique_count / total_count
            if unique_ratio > config['high_uniqueness_threshold']:
                alerts.append(
                    f"WARNING: '{col}' has high uniqueness ({unique_ratio:.1%})"
                )
    
    # 6. Data Type Validation
    for col in config['date_columns']:
        if should_process(col):
            try:
                pd.to_datetime(df[col], errors='raise')
            except:
                alerts.append(f"CRITICAL: '{col}' contains invalid date values")
    
    # Numeric Columns Stored as Objects
    object_cols = df.select_dtypes(include='object').columns
    for col in object_cols:
        if should_process(col):
            try:
                pd.to_numeric(df[col], errors='raise')
                alerts.append(f"WARNING: '{col}' contains numeric data stored as objects")
            except:
                pass
    
    # 7. Special Value Checks
    # Infinite Values Check
    for col in numeric_cols:
        if should_process(col):
            inf_count = np.isinf(df[col]).sum()
            if inf_count > 0:
                alerts.append(f"CRITICAL: '{col}' contains {inf_count} infinite values")
    
    # Priority Sorting (CRITICAL > WARNING > NOTICE)
    priority_order = {'CRITICAL': 0, 'WARNING': 1, 'NOTICE': 2}
    alerts.sort(key=lambda x: priority_order.get(x.split(":")[0], 3))
    
    return alerts
    
def get_alerts_html_content(alerts):
    alerts_count = len(alerts)
    alerts_js = ", ".join([f'"{alert}"' for alert in alerts])

    return f"""
<div id="alerts-section" style="display: none; padding: 30px; background: linear-gradient(145deg, #fdfbfb, #ebedee); border-radius: 20px; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1), 0 -5px 15px rgba(255, 255, 255, 0.6); font-family: 'Poppins', sans-serif; color: #34495e;">
    <h2 style="text-align: center; color: #2c3e50; font-weight: 700; margin-bottom: 25px; letter-spacing: 1.2px; text-transform: uppercase;">🚨 Dataset Alerts</h2>
    <div id="alerts-content" style="padding: 20px; border-top: 2px solid rgba(0, 0, 0, 0.1);">
        <p style="text-align: center; color: rgba(44, 62, 80, 0.6); font-style: italic;">Scanning for alerts...</p>
    </div>
</div>

<script>
    window.alerts = [{alerts_js}];  
</script>
<script src="alerts.js"></script>
""", alerts_count
