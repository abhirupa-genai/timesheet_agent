import pandas as pd
import requests


# 1. Define the base URL where your FastAPI is running
BASE_URL = "http://127.0.0.1:8000"

def save_report(endpoint, filename, params=None):
    url = f"{BASE_URL}/{endpoint}"
    print(f"Downloading {filename}...")
    
    # Make the GET request to your FastAPI server
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        # Save the content as a local CSV file
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"✅ Success! Saved to {filename}")
    else:
        print(f"❌ Failed to download {filename}. Status: {response.status_code}")
        print(f"Error details: {response.text}")




def download_files(from_date, to_date, base_dir):

    OUTPUT_DIR = base_dir + "data/"
    # 1. Download the Employee Details (No parameters needed)
    save_report("download-report", OUTPUT_DIR + "all_employees.csv")

    # 2. Download Leaves Report with Date Filters
    leave_params = {
    "from_date": f"{from_date}",
    "to_date": f"{to_date}"
    }
    save_report("download-report-leaves", OUTPUT_DIR + "leaves.csv", params=leave_params)

    # 3. Download Summarized Timesheet
    timesheet_params = {
        "from_date": f"{from_date}",
        "to_date": f"{to_date}"
    }
    save_report("download-report-taskwise-breakdown", OUTPUT_DIR + "taskwise_timesheet.csv", params=timesheet_params)

    # 4. Download Project Mapping Report
    project_mapping_params = {
        "start_date" : f"{from_date}",
        "end_date" : f"{to_date}"
    }
    save_report("download-project-mapping-report", OUTPUT_DIR + "project_mapping_report.csv", params=project_mapping_params)

