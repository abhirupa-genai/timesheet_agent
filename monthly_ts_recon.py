from google import genai
from openai import OpenAI
import ollama
#from google.generativeai import types
import pandas as pd
import json
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv()

try:
    df_ts = pd.read_excel('summarized_timeSheet_Jan2026.xlsx')
    # Optional: Display the first few rows to confirm it loaded correctly
    print("Data loaded successfully:")
    print(df_ts.head())
except FileNotFoundError:
    print(f"Error: summarized_timeSheet_Jan2026.xlsx not found. Please check the file path.")
    exit()
except Exception as e:
    print(f"An error occurred while reading the Excel file: {e}")
    exit()

try:
    df_emp= pd.read_excel('Employee_report.xlsx')

    print("Employees data loaded successfully")
    print(df_emp)

except FileNotFoundError:
    print(f"Error: report.xlsx not found. Please check the file path.")
    exit()
except Exception as e:
    print(f"An error occurred while reading the Excel file: {e}")
    exit()


try:
    df_holidays= pd.read_excel('Holidays_NSX.xlsx')

    print("Holidays data loaded successfully")
    print(df_holidays)

except FileNotFoundError:
    print(f"Error: Holidays_NSX.xlsx not found. Please check the file path.")
    exit()
except Exception as e:
    print(f"An error occurred while reading the Excel file: {e}")
    exit()

try:
    df_leaves= pd.read_excel('leaves_Jan2026.xlsx')

    print("Leaves data loaded successfully")
    print(df_leaves)

except FileNotFoundError:
    print(f"Error: leave_Jan2026.xlsx not found. Please check the file path.")
    exit()
except Exception as e:
    print(f"An error occurred while reading the Excel file: {e}")
    exit()

ts_as_csv = df_ts.to_csv(index=False)
emp_as_csv = df_emp.to_csv(index=False)
hol_as_csv = df_holidays.to_csv(index=False)
leaves_as_csv = df_leaves.to_csv(index=False)


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

try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    client = genai.Client(api_key=api_key)
except ValueError as e:
    print(f"Configuration error: {e}")
    exit()


response = client.models.generate_content(
    model="gemini-3-flash-preview", # Or a more powerful model like gemini-2.5-pro for complex analysis
    contents=monthly_analysis_prompt
    
    
)

analysis_result = response.text

emp_lst = json.loads(analysis_result)
df_report = pd.DataFrame(emp_lst)
df_report.to_excel("Monthly_Report_January_2026.xlsx", index=False, sheet_name="January_2026") 