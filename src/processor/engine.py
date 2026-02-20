from google import genai
import pandas as pd
import json
from datetime import datetime

from src.processor.load_data import download_files
from src.processor import readfiles

def generate_report(from_date, to_date, api_key, base_dir):

    start_date = datetime.strptime(from_date, "%Y-%m-%d")
    end_date = datetime.strptime(to_date, "%Y-%m-%d")
    delta = end_date - start_date
    
    if (delta.days == 4) or (delta.days == 6):
        print(f"Generating report for the week {start_date.date()} to {end_date.date()}")
        generate_weekly_report(from_date, to_date, api_key, base_dir)
    elif (delta.days==29) or (delta.days ==30):
        print(f"Generating report for the month {start_date.date()} to {end_date.date()}")
        generate_monthly_report(from_date, to_date, api_key, base_dir)
    else:
        print(f"Generating report for the period {start_date.date()} to {end_date.date()}")
        generate_period_report(from_date, to_date, api_key, base_dir)


def generate_period_report(from_date,to_date, api_key, base_dir):

    INPUT_DIR = base_dir + "data/"
    OUTPUT_DIR = base_dir + "report/"
    

    download_files(from_date, to_date, base_dir)
    
    ## Loading the HRMS timesheet entries
    df_ts = readfiles.read_csv(INPUT_DIR + 'taskwise_timeSheet.csv')
    #print(df_ts.head())
    
    #Loading the NstarX employee records
    df_emp= readfiles.read_csv(INPUT_DIR + 'all_employees.csv')
    #print(df_emp.head())

    #Loading the NstarX holidays for the year
    df_holidays= readfiles.read_excel(INPUT_DIR + 'Holidays_NSX.xlsx')
    #print(df_holidays.head())

    #Loading the leaves applied for during the current week
    df_leaves= readfiles.read_csv(INPUT_DIR + 'leaves.csv')
    #print(df_leaves.head())

    # The dataframes are converted to csv format 
    ts_as_csv = df_ts.to_csv(index=False)
    emp_as_csv = df_emp.to_csv(index=False)
    hol_as_csv = df_holidays.to_csv(index=False)
    leaves_as_csv = df_leaves.to_csv(index=False)

    # The promt for instructing the LLM to analyse the weekly timesheet records for each employee
    analysis_prompt = f"""

    1. Look into the timesheet records from {ts_as_csv}. 
    2. The list of employees is {emp_as_csv}
    3. The holidays for each location country is in {hol_as_csv}
    4. The list of leaves applied by the employees are in {leaves_as_csv}.
    5. The number of working hours in a day is 8 hours. For a given location/country the number of working hours in a time period is (number of week days - holidays) times 8 hours.
    6. Calculate the "required number of working hours in the time period" according to step 5.
    7. For every employee the "required number of working hours" is "required working hours in the week" - (8 times number of leaves he/she applied for)
    8. Employees can record their time for the time period in one row or they might split their time in muliple rows.
    9. If there are multiple records for one 'Employee Name' add up the 'Total Working Hours' for all the rows.
    10. For each employee in {emp_as_csv} calculate "Deficiency/Overtime in  Hours" = required working hours in the time periodk - (8 times number of leaves he/she applied for) 
    11. Create a json list output string that can be loaded in a python dictionary.
        for every employee in {emp_as_csv} add a dictionary to the list even if the employee has no timesheet records.
        The keys for each dictionary should be 
        "Name","Location", "Deficiency/Overtime in Hours", "Total Time Logged", "Holiday Hours", "PTO Hours", "Status", "Manager", "Validation Needed","Analysis of Deficiency".
        "Total Time Logged" is same as "Total Working Hours". 
        "Holiday Hours" is 8 times the total number of holidays in the time period.
        "PTO Hours" is 8 times the total number of leaves taken by the employee in the time period.
        "Status" is same as "Timesheet Status" .
        "Manager is the "Timesheet Approver"
        Include a brief summary of the time logged under "Analysis of Deficiency". 
        If time logged is not equivalet to the required number of working hours then set "Validation Needed" to "Yes". Otherwise "No"
        If the logged hours is less than the required number of working hours, precede the "Deficiency/Overtime in Hours" with a '-'
        If the logged hours is more than the required number of working hours, precede the "Deficiency/Overtime in Hours" with a '+'

    12. Do not include any string in the response apart from the json list. 
    """
    # Calling the LLM to analyse the data

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
        model="gemini-3-flash-preview", # Or a more powerful model like gemini-2.5-pro for complex analysis
        contents=analysis_prompt
    )
    except Exception as e:
        print(f"Configuration error: {e}")
        exit()
    

    emp_lst = json.loads(response.text)
    df_report = pd.DataFrame(emp_lst)
    #print(df_report.head())
    from_str = datetime.strptime(from_date,"%Y-%m-%d").strftime("%b%d")
    to_str = datetime.strptime(to_date,"%Y-%m-%d").strftime("%b%d")
    report_name = "Timesheet_Report_"+from_str+"_"+to_str+".xlsx"
    #print(report_name)
    df_report.to_excel(OUTPUT_DIR + report_name)



    





def generate_weekly_report(from_date, to_date, api_key, base_dir):
    
    INPUT_DIR = base_dir + "data/"
    OUTPUT_DIR = base_dir + "report/"
    

    download_files(from_date, to_date, base_dir)
    
    ## Loading the HRMS timesheet entries
    df_ts = readfiles.read_csv(INPUT_DIR + 'taskwise_timeSheet.csv')
    #print(df_ts.head())
    
    #Loading the NstarX employee records
    df_emp= readfiles.read_csv(INPUT_DIR + 'all_employees.csv')
    #print(df_emp.head())

    #Loading the NstarX holidays for the year
    df_holidays= readfiles.read_excel(INPUT_DIR + 'Holidays_NSX.xlsx')
    #print(df_holidays.head())

    #Loading the leaves applied for during the current week
    df_leaves= readfiles.read_csv(INPUT_DIR + 'leaves.csv')
    #print(df_leaves.head())

    # The dataframes are converted to csv format 
    ts_as_csv = df_ts.to_csv(index=False)
    emp_as_csv = df_emp.to_csv(index=False)
    hol_as_csv = df_holidays.to_csv(index=False)
    leaves_as_csv = df_leaves.to_csv(index=False)

    # The promt for instructing the LLM to analyse the weekly timesheet records for each employee
    weekly_analysis_prompt = f"""

    1. Look into the timesheet records from {ts_as_csv}. 
    2. The list of employees is {emp_as_csv}
    3. The holidays for each location country is in {hol_as_csv}
    4. The list of leaves applied by the employees are in {leaves_as_csv}.
    5. The number of working hours in a day is 8 hours. For a given location/country the number of working hours in a week is (number of week days - holidays) times 8 hours.
    6. Calculate the "required number of working hours in the week" according to step 5.
    7. For every employee the "required number of working hours" is "required working hours in the week" - (8 times number of leaves he/she applied for in the week)
    8. Employees can record their time for the week in one row or they might split their time in muliple rows.
    9. If there are multiple records for one 'Employee Name' add up the 'Total Working Hours' for all the rows.
    10. For each employee in {emp_as_csv} calculate "Deficiency/Overtime in  Hours" = required working hours in the week - (8 times number of leaves he/she applied for) 
    11. Create a json list output string that can be loaded in a python dictionary.
        for every employee in {emp_as_csv} add a dictionary to the list even if the employee has no timesheet records.
        The keys for each dictionary should be 
        "Name","Location", "Deficiency/Overtime in Hours", "Total Time Logged", "Holiday Hours", "PTO Hours", "Status", "Manager", "Validation Needed","Analysis of Deficiency".
        "Total Time Logged" is same as "Total Working Hours". 
        "Holiday Hours" is 8 times the total number of holidays in the time period.
        "PTO Hours" is 8 times the total number of leaves taken by the employee in the time period.
        "Status" is same as "Timesheet Status" .
        "Manager is the "Timesheet Approver"
        Include a brief summary of the time logged under "Analysis of Deficiency". 
        If time logged is not equivalent to the required number of working hours then set "Validation Needed" to "Yes". Otherwise "No"
        If the logged hours is less than the required number of working hours, precede the "Deficiency/Overtime in Hours" with a '-'
        If the logged hours is more than the required number of working hours, precede the "Deficiency/Overtime in Hours" with a '+'

    12. Do not include any string in the response apart from the json list. 
    """
    # Calling the LLM to analyse the data

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
        model="gemini-3-flash-preview", # Or a more powerful model like gemini-2.5-pro for complex analysis
        contents=weekly_analysis_prompt
    )
    except Exception as e:
        print(f"Configuration error: {e}")
        exit()
    

    emp_lst = json.loads(response.text)
    df_report = pd.DataFrame(emp_lst)
    #print(df_report.head())
    from_str = datetime.strptime(from_date,"%Y-%m-%d").strftime("%b%d")
    to_str = datetime.strptime(to_date,"%Y-%m-%d").strftime("%b%d")
    report_name = "Weekly_Timesheet_Report_"+from_str+"_"+to_str+".xlsx"
    #print(report_name)
    df_report.to_excel(OUTPUT_DIR + report_name)







def generate_monthly_report(from_date, to_date, api_key, base_dir):
    
    INPUT_DIR = base_dir + "data/"
    OUTPUT_DIR = base_dir + "report/"


    download_files(from_date, to_date, base_dir)
    
    ## Loading the HRMS timesheet entries
    df_ts = readfiles.read_csv(INPUT_DIR + 'taskwise_timeSheet.csv')
    #print(df_ts.head())
    
    #Loading the NstarX employee records
    df_emp= readfiles.read_csv(INPUT_DIR + 'all_employees.csv')
    #print(df_emp.head())

    #Loading the NstarX holidays for the year
    df_holidays= readfiles.read_excel(INPUT_DIR + 'Holidays_NSX.xlsx')
    #print(df_holidays.head())

    #Loading the leaves applied for during the current week
    df_leaves= readfiles.read_csv(INPUT_DIR + 'leaves.csv')
    #print(df_leaves.head())

    # The dataframes are converted to csv format 
    ts_as_csv = df_ts.to_csv(index=False)
    emp_as_csv = df_emp.to_csv(index=False)
    hol_as_csv = df_holidays.to_csv(index=False)
    leaves_as_csv = df_leaves.to_csv(index=False)

    # The promt for instructing the LLM to analyse the weekly timesheet records for each employee
    monthly_analysis_prompt = f"""

    1. Look into the timesheet records from {ts_as_csv}. 
    2. The list of employees is {emp_as_csv}
    3. The holidays for each location country is in {hol_as_csv}
    4. The list of leaves applied by the employees are in {leaves_as_csv}.
    5. The number of working hours in a day is 8 hours. For a given location/country the number of working hours in a month is 
    (total working days in the month - holidays) times 8 hours.
    6. Calculate the "required number of working hours in the month" according to step 5.
    7. An employee can have multiple rows in {leaves_as_csv}.
    8. For every employee calculate the number of leave days in the month by adding the total_leave_days column values.
    9. For every employee the "required number of working hours" is "required working hours in the month" - (8 times number of leave days)
    10. Employees have their time recorded in muliple rows.
    11. For each 'Employee Name' add up the 'Total Working Hours' for all the rows.
    12. For each employee calculate "Deficiency/Overtime in  Hours" = required working hours in the month - (8 times number of leaves he/she applied for) 
    13. Create a json list output string that can be loaded in a python dictionary. The list should include one dictionary for each employee from {emp_as_csv}.
        The keys for each dictionary should be 
        "Name","Location", "Deficiency/Overtime in Hours", "Total Time Logged","Holiday Hours", "PTO Hours", "Status", "Manager", "Validation Needed","Analysis of Deficiency".
        "Total Time Logged" is same as "Total Working Hours". 
        "Holiday Hours" is 8 times the total number of holidays in the month.
        "PTO Hours" is 8 times the number of leave days in the month for the employee. It is 0 hours for those who have not taken any leave.
        "Status" is same as "Timesheet Status" .
        "Manager is the "Timesheet Approver"
        Include a brief summary of the time logged under "Analysis of Deficiency". 
        If time logged is not equivalet to the required number of hours then set "Validation Needed" to "Yes". Otherwise "No"
        If the logged hours is less than the required number of hours, precede the "Deficiency/Overtime in Hours" with a '-'
        If the logged hours is more than the required number of hours, precede the "Deficiency/Overtime in Hours" with a '+'

    12. Do not include any string in the response apart from the json list. 
    """
    # Calling the LLM to analyse the data

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
        model="gemini-3-flash-preview", # Or a more powerful model like gemini-2.5-pro for complex analysis
        contents=monthly_analysis_prompt
    )
    except Exception as e:
        print(f"Configuration error: {e}")
        exit()
    

    emp_lst = json.loads(response.text)
    df_report = pd.DataFrame(emp_lst)
    #print(df_report.head())
    from_str = datetime.strptime(from_date,"%Y-%m-%d").strftime("%b%d")
    to_str = datetime.strptime(to_date,"%Y-%m-%d").strftime("%b%d")
    report_name = "Monthly_Timesheet_Report_"+from_str+"_"+to_str+".xlsx"
    #print(report_name)
    df_report.to_excel(OUTPUT_DIR + report_name)
    


