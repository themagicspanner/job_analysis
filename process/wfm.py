import pandas as pd
import numpy as np

def load_data():
    df = pd.read_csv("csv_files/Active Job Time Report.csv")

    df.rename(columns={'[Job] Job No.': 'Job',
                       '[Job] Name': 'Name',
                       '[Job] Client': 'Client',
                       '[Job] Discipline': 'Discipline',
                       '[Job] Office': 'Office',
                       '[Job] Job Manager': 'Manager',
                       '[Job] Account Manager': 'Account Manager',
                       '[Task] Name + Label': 'Task',
                       '[Staff] Name': 'Staff',
                       '[Time] Billable Amount': 'Total',
                       '[Time] Date': 'Date',
                       }, inplace=True)

    df['Total'] = df['Total'].str.replace(',', '').astype(float)
    df['Task'] = df['Task'].astype('str')
    df['Manager'] = df['Manager'].replace(np.nan, 'Not Assigned')
    df['Account Manager'] = df['Account Manager'].replace(np.nan, 'Not Assigned')
    df['Office'] = df['Office'].replace(np.nan, 'Not Assigned')
    df['Discipline'] = df['Discipline'].replace(np.nan, 'Not Assigned')
    df['Date'] = pd.to_datetime(df['Date']).dt.date

    return df
