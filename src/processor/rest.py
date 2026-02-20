from fastapi import FastAPI, Response, Query
import requests, csv, io
import logging

log = logging.getLogger(__name__)
app = FastAPI()

FRAPPE_URL = "https://hrms.nstarxinc.com/api/method/frappe.desk.query_report.run"
API_KEY = "be5f35aa2edff2d"
API_SECRET = "35a9acb364dae6a"

def generate_csv_response(data, filename):
    """
    Helper function to convert Frappe JSON message to CSV Response.
    Handles both Dictionary rows (key-value) and List rows (ordered values).
    """
    columns = data.get("columns", [])
    rows = data.get("result", [])

    # Extract headers
    headers_row = [c.get("label") for c in columns]
    fieldnames = [c.get("fieldname") for c in columns]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers_row)

    for row in rows:
        # CHECK: If row is a dictionary, map it using fieldnames
        if isinstance(row, dict):
            writer.writerow([row.get(field) for field in fieldnames])
        # CHECK: If row is already a list (like in Summarized Timesheet), write it directly
        elif isinstance(row, (list, tuple)):
            writer.writerow(row)

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/download-report")
def download_report():
    headers = {"Authorization": f"token {API_KEY}:{API_SECRET}"}
    payload = {"report_name": "All Employee Details with Location"}

    r = requests.post(FRAPPE_URL, json=payload, headers=headers)
    resp = r.json()
    
    if "message" not in resp:
        return Response(str(resp), media_type="text/plain", status_code=500)
        
    return generate_csv_response(resp["message"], "report.csv")

@app.get("/download-project-mapping-report")
def download_project_mapping_report(
    start_date: str = Query(..., description="Format YYYY-MM-DD", examples=["2026-01-01"], pattern=r"^\d{4}-\d{2}-\d{2}$"),
    end_date: str = Query(..., description="Format YYYY-MM-DD", examples=["2026-01-31"], pattern=r"^\d{4}-\d{2}-\d{2}$")
):
    headers = {"Authorization": f"token {API_KEY}:{API_SECRET}"}
    payload = {
        "report_name": "Project Mapping Report",
        "filters": {
            "start_date": start_date,
            "end_date": end_date
        }
    }

    r = requests.post(FRAPPE_URL, json=payload, headers=headers)
    resp = r.json()

    if "message" not in resp:
        return Response(str(resp), media_type="text/plain", status_code=500)

    return generate_csv_response(resp["message"], "project_mapping_report.csv")

@app.get("/download-report-summarized-timesheet")
def download_summarized_timesheet(
    start_date: str = Query(..., description="Format YYYY-MM-DD", examples=["2026-01-01"], pattern=r"^\d{4}-\d{2}-\d{2}$"),
    end_date: str = Query(..., description="Format YYYY-MM-DD", examples=["2026-01-31"], pattern=r"^\d{4}-\d{2}-\d{2}$")
):
    headers = {"Authorization": f"token {API_KEY}:{API_SECRET}"}
    
    # Summarized Timesheet usually works with start_date/end_date
    payload = {
        "report_name": "Summarized Timesheet Report",
        "filters": {
            "start_date": start_date,
            "end_date": end_date
        }
    }

    r = requests.post(FRAPPE_URL, json=payload, headers=headers)
    resp = r.json()

    if "message" not in resp:
        return Response(str(resp), media_type="text/plain", status_code=500)

    # The helper function will now handle the list format safely
    return generate_csv_response(resp["message"], "summarized_timesheet.csv")

@app.get("/download-report-leaves")
def download_leaves_report(
    from_date: str = Query(..., description="Format YYYY-MM-DD", examples=["2026-01-01"], pattern=r"^\d{4}-\d{2}-\d{2}$"),
    to_date: str = Query(..., description="Format YYYY-MM-DD", examples=["2026-01-31"], pattern=r"^\d{4}-\d{2}-\d{2}$")
):
    headers = {"Authorization": f"token {API_KEY}:{API_SECRET}"}
    
    # FIX: The SQL query for this specific report uses uppercase placeholders with spaces.
    # We must map our variables to "FROM DATE" and "TO DATE" exactly.
    payload = {
        "report_name": "leave application list report",
        "filters": {
            "FROM DATE": from_date,
            "TO DATE": to_date
        }
    }

    r = requests.post(FRAPPE_URL, json=payload, headers=headers)
    resp = r.json()

    if "message" not in resp:
        # It's good practice to log the error here if you have a logger
        print(f"Frappe Error: {resp}") 
        return Response(str(resp), media_type="text/plain", status_code=500)

    return generate_csv_response(resp["message"], "leaves.csv")

@app.get("/download-report-taskwise-breakdown")
def download_taskwise_breakdown_report(
    from_date: str = Query(..., description="Format YYYY-MM-DD", examples=["2026-01-01"], pattern=r"^\d{4}-\d{2}-\d{2}$"),
    to_date: str = Query(..., description="Format YYYY-MM-DD", examples=["2026-01-31"], pattern=r"^\d{4}-\d{2}-\d{2}$")
):
    headers = {"Authorization": f"token {API_KEY}:{API_SECRET}"}
    
    # FIX: The SQL query for this specific report uses uppercase placeholders with spaces.
    # We must map our variables to "FROM DATE" and "TO DATE" exactly.
    payload = {
        "report_name": "Task-wise Breakdown Report",
        "filters": {
            "start_date": from_date,
            "end_date": to_date
        }
    }

    r = requests.post(FRAPPE_URL, json=payload, headers=headers)
    resp = r.json()
    print(f"DEBUG DATA: {resp}") #delete once the issue is resolved

    if "message" not in resp:
        # It's good practice to log the error here if you have a logger
        print(f"Frappe Error: {resp}") 
        return Response(str(resp), media_type="text/plain", status_code=500)

    return generate_csv_response(resp["message"], "taskwise_timesheet.csv")

    # To run from command promt uvicorn rest:app --reload 