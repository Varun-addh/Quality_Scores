import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io
import base64
from pandas.api.types import infer_dtype
import subprocess
from .data_alerts import generate_data_alerts, get_alerts_html_content

subprocess.run(["python", "Data_Validation\\datadetairep\\data_alerts.py"])

# Function to dynamically represent memory usage
def format_memory_size(bytes_size):
    units = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB']
    index = 0
    while bytes_size >= 1024 and index < len(units) - 1:
        bytes_size /= 1024
        index += 1
    return f"{bytes_size:.2f} {units[index]}"

def estimate_unique(df):
    """Optimized unique value estimation using column-wise calculation"""
    unique_counts = 0
    for col in df.columns:
        try:
            unique_counts += df[col].nunique()
        except:
            unique_counts += len(df[col].unique())
    return unique_counts

def format_large_number(value):
    """Formats large numbers using K (thousands), M (millions), B (billions), etc."""
    if value < 1000:
        return str(value)

    units = ['K', 'M', 'B', 'T']
    index = 0
    while value >= 1000 and index < len(units):
        value /= 1000
        index += 1
    return f"{value:.2f}{units[index-1]}"

def generate_detailed_report(df, detailed_scores_df, overall_score):
    try:
        total_cells = len(df) * df.shape[1]
        unique_count = estimate_unique(df)
        missing_cells = df.isnull().sum().sum()
        duplicate_rows = df.duplicated().sum()

        def format_stat(value):
            """Formats statistics based on size."""
            if value < 1000:
                return str(value)
            return f"{value} ({format_large_number(value)})"

        dataset_statistics = {
            "Number of Rows": format_stat(len(df)),
            "Number of Columns": df.shape[1],
            "Missing Cells": format_stat(missing_cells),
            "Missing Cells (%)": f"{(missing_cells / total_cells) * 100:.2f}%",
            "Unique Values": format_stat(unique_count),
            "Unique Values (%)": f"{(unique_count / total_cells) * 100:.2f}%",
            "Duplicate Rows": format_stat(duplicate_rows),
            "Duplicate Rows (%)": f"{(duplicate_rows / len(df)) * 100:.2f}%",
            "Total Memory Usage": format_memory_size(df.memory_usage(deep=True, index=False).sum()),
        }

        variable_types = {
            "Text/Categorical": sum(df.apply(lambda col: infer_dtype(col) in ['string', 'categorical'])),
            "Numeric": sum(df.apply(lambda col: infer_dtype(col) in ['integer', 'floating'])),
            "Boolean": sum(df.apply(lambda col: infer_dtype(col) == 'boolean')),
            "Temporal": sum(df.apply(lambda col: infer_dtype(col).startswith('datetime')))
        }

        metrics = ['Completeness', 'Validity', 'Accuracy', 'Uniqueness', 'Consistency']

        html_content = []
        html_content.append("""<link rel="stylesheet" type="text/css" href="Data_Validation\\datadetairep\\Gde.css">""")
        html_content.append("""<script src="Data_Validation\\datadetairep\\DR.js"></script> """)
        html_content.append(""" <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@500;700&family=Space+Grotesk:wght@700&display=swap"> """)

        alerts = generate_data_alerts(df)
        alerts_html, alerts_count = get_alerts_html_content(alerts)

        html_content.append(alerts_html)

        html_content.append(f"""
            <div class="button-container">
                <button class="overview-button" onclick="toggleOverview()">Overview</button>
                <button id="alerts-button" class="alerts-button" onclick="toggleAlerts()">Alerts({alerts_count})</button>
            </div>
        """)

        html_content.append("""
            <div id="alerts-section" class="alerts-section">
                <h2 class="alerts-header">🚨 Dataset Alerts</h2>
                <div id="alerts-content" class="alerts-content">
                    <p class="alerts-message">Scanning for alerts...</p>
                </div>
            </div>
        """)

        # Step 4: Dataset Statistics and Variable Types Section
        html_content.append("""<div id='dataset-statistics' class='statistics-container'>
             <div class='statistics-section'>
                 <h6 class='section-title'>Dataset Statistics</h6>
                 <table>""")

        for key, value in dataset_statistics.items():
            if isinstance(value, dict):
                html_content.append(f"<tr><td colspan='2' class='table-key'>{key}</td></tr>")
                for sub_key, sub_value in value.items():
                    html_content.append(f"<tr><td class='sub-key'>{sub_key}</td><td class='sub-value'>{sub_value}</td></tr>")
            else:
                html_content.append(f"<tr class='data-row'><td class='data-key'>{key}</td><td class='data-value'>{value}</td></tr>")

        html_content.append("""</table></div>
            <div class='statistics-section'>
                <h6 class='section-title'>Variable Types</h6>
                <table>""")

        for key, value in variable_types.items():
            html_content.append(f"<tr class='data-row'><td class='data-key'>{key}</td><td class='data-value'>{value}</td></tr>")

        html_content.append("""</table></div></div>""")

        html_content.append("""
            <div id="overall-quality-score">
            <h4>Overall Quality Score</h4>
            <p>
                <span id="overall-score-value">--</span>
            </p>
        </div>
        """)

        html_content.append("""
            <div class='metric-selection-container' style='margin-top: 30px; padding: 40px; border-radius: 16px; background: linear-gradient(135deg, #ffffff, #f9fafb); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);'>
                <h4 style="font-family: 'Poppins', sans-serif; font-size: 28px; font-weight: 700; color: #1a237e; margin-bottom: 20px; text-shadow: 2px 2px 4px rgba(26, 35, 126, 0.2); letter-spacing: 0.8px; text-align: center;">
                    Select Metrics
                </h4>
                <div class='checkbox-container' style='display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 30px; padding: 20px; background: linear-gradient(135deg, #fdfbfb, #fdfbfb); border-radius: 16px;'>
        """)

        for metric in metrics:
            html_content.append(f"""
                <div class="checkbox-item" style="padding: 30px; border-radius: 16px; background: linear-gradient(135deg, #fdfbfb, #ebedee); transition: transform 0.3s ease, box-shadow 0.3s ease; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);">
                    <label for="checkbox-{metric}" style="font-size: 1.2em; font-weight: 600; color: #1e3a8a; cursor: pointer; display: flex; align-items: center; font-family: 'Poppins', sans-serif;">
                        <input type="checkbox" id="checkbox-{metric}" name="{metric}" onclick="toggleMetricScores('{metric}')" style="margin-right: 15px; accent-color: #4c51bf; cursor: pointer; transform: scale(1.2);">
                        {metric}
                    </label>
                    <input type="number" id="input-{metric}" class="metric-input" style="display: none; margin-top: 20px; padding: 15px; width: 100%; border: 1px solid #e2e8f0; border-radius: 12px; font-size: 1.2em; background-color: #ffffff; box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1); transition: border 0.3s ease, box-shadow 0.3s ease; font-family: 'Poppins', sans-serif;" placeholder="Enter your priority (%)">
                </div>
            """)

        html_content.append("""
                </div>
                <div style="text-align: center; margin-top: 40px;">
                    <button id="submit-priorities" onclick="submitAllWeights()" style="padding: 16px 40px; font-size: 1.3em; font-weight: 700; color: #ffffff; background: linear-gradient(135deg, #667eea, #764ba2); border: none; border-radius: 12px; cursor: pointer; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2); transition: transform 0.3s ease, box-shadow 0.3s ease;">
                        Submit Priorities
                    </button>
                </div>
            </div>
        """)

        html_content.append("""
                <div id='scores-table-container' style='margin-top: 40px; padding: 40px; border-radius: 16px; background: linear-gradient(135deg, #ffffff, #f9fafb); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);'>
                <h4 style="font-family: 'Poppins', sans-serif; font-size: 28px; font-weight: 700; color: #1a237e; margin-bottom: 20px; text-shadow: 2px 2px 4px rgba(26, 35, 126, 0.2); letter-spacing: 0.8px; text-align: center;">
                    Quality Scores
                </h4>
                <table id='scores-table' style='display: none; border-collapse: collapse; width: 100%; background: #ffffff; border-radius: 12px; box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1); overflow: hidden;'>
                    <thead id='table-header' style="background: linear-gradient(135deg, #3b82f6, #60a5fa); color: #ffffff; font-size: 1.2em; font-weight: 700; text-align: left;"> 
                <tr>
                    <th style="padding: 15px; text-align: left; border-right: 1px solid rgba(255, 255, 255, 0.2);">Column</th>
""")

        for metric in metrics:
            html_content.append(f"""
                            <th id="header-{metric}" style="display: none; padding: 15px; text-align: center; border-right: 1px solid #ffffff;">{metric} Score (%)</th>
            """)

        html_content.append("""
                        </tr>
                    </thead>
                    <tbody id='table-body'>
        """)

        for col, scores in detailed_scores_df.iterrows():
            html_content.append(f"""
                        <tr style="border-bottom: 1px solid #eee;">
                            <td style="padding: 12px; text-align: left; color: #555;">{col}</td>
            """)
            for metric in metrics:
                html_content.append(f"""
                            <td id="score-{metric}-{col}" style="display: none; padding: 12px; text-align: center; color: #333;">
                                {scores.get(metric, 0):.2f}%
                            </td>
                """)
            html_content.append("""
                        </tr>
            """)

        html_content.append("""
                    </tbody>
                </table>
            </div>
        """)

        import pandas as pd
        import plotly.express as px

        missing_data = df.isnull().sum()
        present_data = df.notnull().sum()
        missing_percent = (missing_data / len(df)) * 100
        features = df.columns

        missing_summary = pd.DataFrame({
            'Feature': features,
            'Present': present_data.values,
            'Missing': missing_data.values,
            'Missing (%)': missing_percent.values
        }).sort_values(by='Missing (%)', ascending=False)

        threshold = 50
        missing_summary['Flag'] = missing_summary['Missing (%)'] >= threshold

        fig = px.bar(
            missing_summary,
            x='Feature',
            y=['Present', 'Missing'],
            text_auto=True,
            color_discrete_sequence=['#3498db', '#e74c3c'],
            title="Missing Values Analysis",
            labels={'value': "Number of Values", 'Feature': "Dataset Features"},
            barmode="stack"
        )
        fig.update_layout(
            xaxis_tickangle=45,
            template="plotly_white",
            title_font=dict(size=18, family="Arial"),
            legend=dict(title="Legend", font=dict(size=12)),
            margin=dict(l=10, r=10, t=50, b=50)
        )

        missing_values_chart_html = fig.to_html(full_html=False, include_plotlyjs="cdn")

        csv_buffer = io.StringIO()
        missing_summary.to_csv(csv_buffer, index=False)
        csv_report = base64.b64encode(csv_buffer.getvalue().encode()).decode()

        html_content.append(f"""
        <div id="missing-values" class="missing-values-container">
            <h3 class="section-title">Missing Values Analysis</h3>
            <p class="section-description">The analysis identifies features with missing values, providing both counts and percentages. Interactive charts and data tables help in assessing the impact and prioritizing next steps.</p>
            <div class="chart-wrapper">
                {missing_values_chart_html}
            </div>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Feature</th>
                            <th>Present</th>
                            <th>Missing</th>
                            <th>Missing (%)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {" ".join(
                            f"<tr><td>{row['Feature']}</td><td>{row['Present']}</td><td>{row['Missing']}</td><td>{row['Missing (%)']:.2f}%</td></tr>"
                            for _, row in missing_summary.iterrows()
                        )}
                    </tbody>
                </table>
            </div>
            <a href="data:text/csv;base64,{csv_report}" download="missing_values_report.csv" class="btn btn-download">Download Missing Values Report</a>
        </div>
        """)

        html_content.append("""<div id="visualizations" style="text-align: center; padding: 25px; background: linear-gradient(135deg, #e3f2fd, #f0f4f8); border-radius: 18px; box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);">
    <h3 class='section-title' style="font-family: 'Poppins', sans-serif; font-size: 28px; font-weight: 700; color: #1a237e; margin-bottom: 20px; text-shadow: 2px 2px 4px rgba(26, 35, 126, 0.2); letter-spacing: 0.8px;">🚀 Explore Data </h3>
    <p style="font-family: 'Poppins', sans-serif; font-size: 15px; color: #546e7a; margin-bottom: 18px; line-height: 1.5;">Choose a column to generate visualizations instantly.</p>
    <select id="column-select" onchange="showChart(this.value)" style="font-family: 'Poppins', sans-serif; font-size: 18px; padding: 14px; width: 90%; max-width: 450px; border: 2px solid #5c6bc0; border-radius: 10px; background: #ffffff; box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.1), 0 5px 8px rgba(0, 0, 0, 0.15); transition: all 0.3s ease-in-out;">
        <option value="" disabled selected style="color: #90a4ae; font-weight: 500;">🔍 Select a Column to Reveal Insights</option>
""")
        charts_data = {}

        for col, scores in detailed_scores_df.iterrows():
            html_content.append(f"<option value='{col}'>{col}</option>")
            values = [scores.get(metric, 0) for metric in metrics]

            # Generate Bar Chart
            fig, ax = plt.subplots(figsize=(18, 12), dpi=200)
            sns.barplot(x=metrics, y=values, hue=metrics, ax=ax, palette="Blues_r", legend=False)

            ax.set_title(f"{col}", fontsize=22, fontweight="bold", pad=20)
            ax.set_xticks(range(len(metrics)))
            ax.set_xticklabels(metrics, rotation=45, fontsize=18)
            ax.set_yticks(ax.get_yticks())
            ax.set_yticklabels([f"{tick:.2f}" for tick in ax.get_yticks()], fontsize=18)
            ax.grid(axis="y", linestyle="--", alpha=0.7)

            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight')
            buffer.seek(0)
            bar_chart = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
            plt.close(fig)

            fig, ax = plt.subplots(figsize=(20, 14), dpi=200)  

            sns.heatmap(np.array(values).reshape(1, -1), annot=True, annot_kws={"size": 26, "weight": "bold"},
                        fmt=".2f", cmap="coolwarm", cbar=False, xticklabels=metrics, 
                        yticklabels=[col], linewidths=0.5, linecolor="black", ax=ax)
            
            ax.set_title(f"{col}", fontsize=26, fontweight="bold", pad=30)
            ax.set_xticks(range(len(metrics)))
            ax.set_xticklabels(metrics, rotation=45, fontsize=24) 
            ax.set_yticks([0])

            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight')
            buffer.seek(0)
            heatmap = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
            plt.close(fig)

            charts_data[col] = {'bar_chart': bar_chart, 'heatmap': heatmap}

        html_content.append("</select></div>")

        # Charts Section
        html_content.append("<div class='chart-container' id='chart-container'>")
        for col, charts in charts_data.items():
            html_content.append(f"""<div id="{col}-charts" style="display:none;" class="charts-side-by-side">
                <div class="chart">
                    <h3>Bar Chart</h3>
                    <img src='data:image/png;base64,{charts['bar_chart']}' alt='{col} Bar Chart'>
                </div>
                <div class="chart">
                    <h3>Heatmap</h3>
                    <img src='data:image/png;base64,{charts['heatmap']}' alt='{col} Heatmap'>
                </div>
            </div>""")
        html_content.append("</div>")
          # End Chart Container
        import os

        with open(os.path.join("Data_Validation", "datadetairep", "hi.html"), "r", encoding="utf-8") as ass:
            op_ass = ass.read()
            html_content.append(f"""{op_ass}""")


        return "\n".join(html_content)
 
    except Exception as e:
        print(f"Error generating report: {e}")
        return ""