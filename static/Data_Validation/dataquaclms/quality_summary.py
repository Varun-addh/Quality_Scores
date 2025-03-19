def generate_quality_summary(df, scores_df):
    try:
        # Initialize the HTML content with a link to the external CSS
        html_content = []
        html_content.append("""
        <link rel="stylesheet" href="Data_Validation\\dataquaclms\\Gqcls.css">

        <div class="container">
            <div class="metrics-container">
        """)

        # Generate HTML content for each metric card
        for metric in scores_df.columns:
            columns_passing = scores_df[scores_df[metric] >= 80].index.tolist()

            html_content.append(f"""
            <div class="metric-card">
                <div class="metric-title">{metric}</div>
            """)

            if columns_passing:
                html_content.append("<ul class='columns-list'>")
                for col in columns_passing:
                    html_content.append(f"<li>{col}</li>")
                html_content.append("</ul>")
            else:
                html_content.append("<p class='no-columns'>No columns are passing 80% or above.</p>")

            html_content.append("</div>")  # Closing metric-card

        # Close containers
        html_content.append("""
            </div> <!-- Closing metrics-container -->
            
            <!-- Note Section -->
            <div class="note">
                <p><strong>Note:</strong> Only columns where the quality score is at least <span class="highlight">80%</span> or above are displayed.</p>
            </div>

        </div> <!-- Closing container -->
        """)

        return "\n".join(html_content)

    except Exception as e:
        print(f"Error generating quality summary report: {e}")
        return ""
