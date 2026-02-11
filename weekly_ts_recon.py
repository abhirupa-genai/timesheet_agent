from google import genai
from openai import OpenAI
import ollama
#from google.generativeai import types
import pandas as pd
import json
import os
from dotenv import load_dotenv, find_dotenv


load_dotenv()

# Loading the HRMS timesheet entries
try:
    df_ts = pd.read_excel('summarized_timeSheet_Feb02-06.xlsx')
    # Optional: Display the first few rows to confirm it loaded correctly
    print("Data loaded successfully:")
    #print(df_ts.head())
except FileNotFoundError:
    print(f"Error: ummarized_timeSheet_Feb02-06.xlsx not found. Please check the file path.")
    exit()
except Exception as e:
    print(f"An error occurred while reading the Excel file: {e}")
    exit()

start_date = min(df_ts['Start Date'])

#Loading the NstarX employee records
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

#Loading the NstarX holidays for the year
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

#Loading the leaves applied for during the current week
try:
    df_leaves= pd.read_excel('leaves_Feb02-06.xlsx')

    print("Leaves data loaded successfully")
    print(df_leaves)

except FileNotFoundError:
    print(f"Error: leaves_Feb02-06.xlsx not found. Please check the file path.")
    exit()
except Exception as e:
    print(f"An error occurred while reading the Excel file: {e}")
    exit()

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
5. The number of working hours in a day is 8 hours. For a given location/country the number of working hours in a week is (5 - holidays in the week) times 8 hours.
6. Calculate the "required number of working hours in the week" according to step 5.
7. For every employee the "required number of working hours" is "required working hours in the week" - (8 times number of leaves he/she applied for)
8. Employees can record their time for the week in one row or they might split their time in muliple rows.
9. If there are multiple records for one 'Employee Name' add up the 'Total Working Hours' for all the rows.
10. For each employee in {emp_as_csv} calculate "Deficiency/Overtime in  Hours" = required working hours in the week - (8 times number of leaves he/she applied for) 
11. Create a json list output string that can be loaded in a python dictionary.
    for every employee in {emp_as_csv} add a dictionary to the list even if the employee has no timesheet records.
    The keys for each dictionary should be 
    "Name","Location", "Deficiency/Overtime in Hours", "Total Time Logged", "Holiday Hours", "PTO Hours", "Status", "Manager", "Validation Needed","Analysis of Deficiency".
    "Total Time Logged" is same as "Total Working Hours". 
    "Holiday Hours" is 8 times the total number of holidays in the week.
    "PTO Hours" is 8 times the total number of leaves taken by the employee in the week.
    "Status" is same as "Timesheet Status" .
    "Manager is the "Timesheet Approver"
    Include a brief summary of the time logged under "Analysis of Deficiency". 
    If time logged is not equivalet to the required number of working hours then set "Validation Needed" to "Yes". Otherwise "No"
    If the logged hours is less than the required number of working hours, precede the "Deficiency/Overtime in Hours" with a '-'
    If the logged hours is more than the required number of working hours, precede the "Deficiency/Overtime in Hours" with a '+'

12. Do not include any string in the response apart from the json list. 
"""

# generating the client using the generative api key
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    client = genai.Client(api_key=api_key)
except ValueError as e:
    print(f"Configuration error: {e}")
    exit()

#Running the LLM query/analysis
response = client.models.generate_content(
    model="gemini-3-flash-preview", # Or a more powerful model like gemini-2.5-pro for complex analysis
    contents=analysis_prompt
)

#Loading the LLM response into a data frame
analysis_result = response.text
emp_lst = json.loads(analysis_result)
df_report = pd.DataFrame(emp_lst)
report_as_csv = df_report.to_csv(index=False) # the dataframe is again converted into csv format for passing into LLM prompt

# Prompt to search for timesheet defaulters
defaulters_search_prompt = f"""

1. Look into the reports records from {report_as_csv}. 
2. The list of employees is {emp_as_csv}
3. Look for employees who did not file required number of hours in the column "Deficiency/Overtime in Hours".
4. For the defaulters the column "Validation Needed" should be "Yes".
5. Create a json list output string that can be loaded in a python dictionary. The list should include one dictionary defaulter found in step 4.
6. The keys for each dictionary should be 
    "Name","Location", "Deficiency/Overtime in Hours", "Total Time Logged", "Holiday Hours", "PTO Hours", "Status", "Manager","Week Defaulted".
7. All the matching columns in step 6 should be as they are in {report_as_csv}.
8. The column "Week Defaulted" should be the last working date ("DD-MM-YYYY")of the week starting on {start_date}.
9. Do not include any string in the response apart from the json list. 
"""

#Running the LLM analysis
response = client.models.generate_content(
    model="gemini-3-flash-preview", # Or a more powerful model like gemini-2.5-pro for complex analysis
    contents=defaulters_search_prompt
)

#Generating the dataframe of defaulters from the LLM response
defaulters_result = response.text
defaulters_lst = json.loads(defaulters_result)
df_defaulters = pd.DataFrame(defaulters_lst)

#Writing the reports into excel file
try:
    with pd.ExcelWriter("Weekly_Report_Feb02-06.xlsx", engine='openpyxl') as writer:
        df_report.to_excel(writer, sheet_name='Timesheet Report Feb 02-06', index=False)
        df_defaulters.to_excel(writer, sheet_name='Defaulters Feb 02-06', index=False)

    print(f"Successfully created '{"Weekly_Report_Feb02-06.xlsx"}' with multiple sheets.")

except Exception as e:
    print(f"An error occurred: {e}")


