import time
import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
from dotenv import load_dotenv 

# Import data validation modules
from Data_Validation.dataloD.data_loader import load_dataset
from Data_Validation.dataquame.data_quality_metrics import calculate_scores, overall_quality_score
from Data_Validation.datadetairep.detailed_report import generate_detailed_report
from Data_Validation.dataquaclms.quality_summary import generate_quality_summary
from Data_Validation.dataProfrep.data_profiling_report import generate_combined_report

import matplotlib
matplotlib.use('Agg')  

# Load environment variables
load_dotenv("fl.env")

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Set a secret key for the session

UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 

# Ensure necessary folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("EMAIL_USER")  
app.config['MAIL_PASSWORD'] = os.getenv("EMAIL_PASS") 
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("EMAIL_USER")

mail = Mail(app)

@app.route('/', methods=['GET'])
def index():
    """Render the index page with the file upload form."""
    return render_template('index.html')

@app.route('/generate_report', methods=['POST'])
def generate_report():
    """Generate a data quality report and redirect to avoid form resubmission."""
    start_time = time.time()
    
    try:
        # Validate file uploads
        if 'file1' not in request.files or 'file2' not in request.files:
            flash("Please upload both required files.", "error")
            return redirect(url_for('index'))

        file1 = request.files['file1']
        file2 = request.files['file2']

        if not file1.filename or not file2.filename:
            flash("Both files must have valid filenames.", "error")
            return redirect(url_for('index'))

        # Generate unique filenames
        unique_name1 = str(uuid.uuid4()) + '.csv'
        unique_name2 = str(uuid.uuid4()) + '.csv'
        dataset_path1 = os.path.join(app.config['UPLOAD_FOLDER'], unique_name1)
        dataset_path2 = os.path.join(app.config['UPLOAD_FOLDER'], unique_name2)
        file1.save(dataset_path1)
        file2.save(dataset_path2)

        # Load datasets
        df1 = load_dataset(dataset_path1)
        df2 = load_dataset(dataset_path2)

        # Validate dataset contents
        if df1 is None or df1.empty:
            flash(f"The dataset at {file1.filename} is empty or invalid. Please check the file content.", "error")
            return redirect(url_for('index'))
        if df2 is None or df2.empty:
            flash(f"The dataset at {file2.filename} is empty or invalid. Please check the file content.", "error")
            return redirect(url_for('index'))

        # Calculate scores
        detailed_scores_df = calculate_scores(df1, df2)
        overall_score = overall_quality_score(detailed_scores_df)

        # Generate reports
        detailed_report_content = generate_detailed_report(df1, detailed_scores_df, overall_score)
        quality_summary_content = generate_quality_summary(df1, detailed_scores_df)

        # Combine all sections into an HTML report
        output_filename = 'combined_data_quality_report.html'
        output_path = os.path.join(STATIC_FOLDER, output_filename)
        generate_combined_report(df1, detailed_report_content, quality_summary_content, output_path)

        # Clean up uploaded files to free space
        os.remove(dataset_path1)
        os.remove(dataset_path2)

        # Measure execution time
        execution_time_seconds = time.time() - start_time
        execution_minutes = int(execution_time_seconds // 60)
        execution_seconds = round(execution_time_seconds % 60, 2)
        execution_time_formatted = f"{execution_minutes} min {execution_seconds} sec"

        print(f"Report generation time: {execution_time_formatted}")

        # Store execution time in session
        session['execution_time'] = execution_time_formatted

        # Redirect to report page (PRG pattern)
        return redirect(url_for('view_report'))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('index'))

@app.route('/view_report')
def view_report():
    """Render the report viewer page."""
    report_url = url_for('static', filename='combined_data_quality_report.html')
    execution_time = session.get('execution_time', "0 min 0 sec")
    return render_template('report_viewer.html', report_url=report_url, execution_time=execution_time)

@app.route('/contact', methods=['GET', 'POST'])
def contact_support():
    """Render the contact support page or handle form submission."""
    if request.method == 'GET':
        return render_template('contact.html')

    if request.method == 'POST':
        try:
            # Get form data
            user_name = request.form.get("userName")
            user_email = request.form.get("userEmail")
            subject = request.form.get("subject")
            message = request.form.get("message")

            # Validate inputs
            if not user_name or not user_email or not subject or not message:
                flash("All fields are required.", "error")
                return redirect(url_for('contact_support'))

            # Send email
            msg = Message(subject=f"Support Request: {subject}",
                          sender=app.config['MAIL_DEFAULT_SENDER'],
                          recipients=["varunplm1605@gmail.com"])
            msg.body = f"From: {user_name} ({user_email})\n\n{message}"
            mail.send(msg)

            flash("Your message has been sent successfully!", "success")
            return redirect(url_for('contact_support') + '#contactForm') 
        except Exception as e:
            flash(f"Error sending message: {str(e)}", "error")
            return redirect(url_for('contact_support') + '#contactForm')

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)    
























# from Data_Validation.dataloD.data_loader import load_dataset
# from Data_Validation.dataquame.data_quality_metrics import calculate_scores, overall_quality_score
# from Data_Validation.datadetairep.detailed_report import generate_detailed_report
# from Data_Validation.dataquaclms.quality_summary import generate_quality_summary
# from Data_Validation.dataProfrep.data_profiling_report import generate_combined_report
# import matplotlib
# import io
# import requests
# import zipfile

# # Ensure matplotlib works in headless environments
# matplotlib.use("Agg")


# if __name__ == "__main__":
#     try:
#         if(1):
#             response = requests.get("https://www.kaggle.com/api/v1/datasets/download/dongrelaxman/amazon-reviews-dataset")
#             zf = zipfile.ZipFile(io.BytesIO(response.content))
#             zf.extractall("Data_Validation\\Ds'S")
#         # Step 1: Load the datasets
#         dataset_path = "Data_Validation\\Ds'S\\sample.csv"
#         dataset_path2 = "Data_Validation\\Ds'S\\second_dataset.csv"
#         df = load_dataset(dataset_path)
#         df2 = load_dataset(dataset_path2)

#         # Validate if the datasets are loaded properly
#         if df is None or df.empty:
#             raise ValueError(f"The dataset at {dataset_path} is empty or failed to load. Check the file path and content.")
#         if df2 is None or df2.empty:
#             raise ValueError(f"The dataset at {dataset_path2} is empty or failed to load. Check the file path and content.")

#         # Step 2: Calculate detailed scores for each column
#         detailed_scores_df = calculate_scores(df, df2)

#         # Step 3: Calculate the overall data quality score
#         overall_score = overall_quality_score(detailed_scores_df)

#         # Step 4: Generate the detailed report content
#         detailed_report_content = generate_detailed_report(df, detailed_scores_df, overall_score)

#         # Step 5: Generate the quality summary content
#         quality_summary_content = generate_quality_summary(df, detailed_scores_df)

#         # Step 6: Generate the combined report with all sections
#         output_path = "combined_data_quality_report.html"
#         generate_combined_report(df, detailed_report_content, quality_summary_content,output_path)

#         print(f"Data quality report generated successfully and saved as '{output_path}'!")

#     except FileNotFoundError as e:
#         print(f"Error: {e}. Check if the file paths '{dataset_path}' and '{dataset_path2}' exist.")
#     except Exception as e:
#         print(f"An error occurred: {e}")
























# from Data_Validation.dataloD.data_loader import load_dataset
# from Data_Validation.dataquame.data_quality_metrics import calculate_scores, overall_quality_score
# from Data_Validation.datadetairep.detailed_report import generate_detailed_report
# from Data_Validation.dataquaclms.quality_summary import generate_quality_summary
# from Data_Validation.dataProfrep.data_profiling_report import generate_combined_report
# import matplotlib
# import io
# import requests
# import zipfile

# # Ensure matplotlib works in headless environments
# matplotlib.use("Agg")


# if __name__ == "__main__":
#     try:
#         if(1):
#             response = requests.get("https://www.kaggle.com/api/v1/datasets/download/dongrelaxman/amazon-reviews-dataset")
#             zf = zipfile.ZipFile(io.BytesIO(response.content))
#             zf.extractall("Data_Validation\\Ds'S")
#         # Step 1: Load the datasets
#         dataset_path = "Data_Validation\\Ds'S\\sample.csv"
#         dataset_path2 = "Data_Validation\\Ds'S\\second_dataset.csv"
#         df = load_dataset(dataset_path)
#         df2 = load_dataset(dataset_path2)

#         # Validate if the datasets are loaded properly
#         if df is None or df.empty:
#             raise ValueError(f"The dataset at {dataset_path} is empty or failed to load. Check the file path and content.")
#         if df2 is None or df2.empty:
#             raise ValueError(f"The dataset at {dataset_path2} is empty or failed to load. Check the file path and content.")

#         # Step 2: Calculate detailed scores for each column
#         detailed_scores_df = calculate_scores(df, df2)

#         # Step 3: Calculate the overall data quality score
#         overall_score = overall_quality_score(detailed_scores_df)

#         # Step 4: Generate the detailed report content
#         detailed_report_content = generate_detailed_report(df, detailed_scores_df, overall_score)

#         # Step 5: Generate the quality summary content
#         quality_summary_content = generate_quality_summary(df, detailed_scores_df)

#         # Step 6: Generate the combined report with all sections
#         output_path = "combined_data_quality_report.html"
#         generate_combined_report(df, detailed_report_content, quality_summary_content,output_path)

#         print(f"Data quality report generated successfully and saved as '{output_path}'!")

#     except FileNotFoundError as e:
#         print(f"Error: {e}. Check if the file paths '{dataset_path}' and '{dataset_path2}' exist.")
#     except Exception as e:
#         print(f"An error occurred: {e}")

