import pandas as pd

def read_excel(filepath):
    try:
        df = pd.read_excel(filepath)
        print(f"Data from {filepath} loaded succesfully")
    except FileNotFoundError:
        print(f"Error: {filepath} not found. Please check the file path.")
        exit()
    except Exception as e:
        print(f"An error occurred while reading the Excel file: {e}")
        exit()

    return(df)

def read_csv(filepath):
    try:
        df = pd.read_csv(filepath)
   
    except FileNotFoundError:
        print(f"Error: {filepath} not found. Please check the file path")
        exit()
    except Exception as e:
        print(f"An error occured while reading the csv file: {e} ")
        exit()
    
    return df
