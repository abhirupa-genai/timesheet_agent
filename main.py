from dotenv import load_dotenv
import os
import sys
from src.processor import engine as eg




def main():

    # This looks for the .env file in the current directory
    load_dotenv() 
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        base_dir = os.getenv("BASE_DIR")
        if not base_dir:
            raise ValueError("BASE DIRECTORY not found")
        from_date = os.getenv("FROM_DATE")
        if not from_date:
            raise ValueError("FROM_DATE not found")
        to_date = os.getenv("TO_DATE")
        if not to_date:
            raise ValueError("TO_DATE not found")
    #client = genai.Client(api_key=api_key)

    except ValueError as e:
        print(f"Configuration error: {e}")
        exit()

    #Load the reporting engine
    try:
        eg.generate_report(from_date, to_date, api_key, base_dir)
        #eg.generate_weekly_report(from_date, to_date, api_key, base_dir)
        #eg.generate_monthly_report(from_date, to_date, api_key, base_dir)

    except Exception as e:
        print(f"Report error : {e}")
        exit()

if __name__=="__main__":
    main()

