from process import wfm
import pandas as pd
from datetime import datetime, timedelta

pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 10000)
pd.options.display.float_format = '{:.2f}'.format


# Process the spend data from WFM

def job_spend(df, job_no):
    df_wfm_filter = df[(df['Job'] == job_no)]
    df_time = df_wfm_filter[['Date', 'Total']]
    df_time['Date'] = pd.to_datetime(df_time['Date'])
    df_time = df_time.groupby(['Date']).agg('sum')
    df_time.sort_index(inplace=True)
    df_time['Sum'] = df_time['Total'].cumsum()
    # df_time.reset_index(inplace=True)

    return df_time

def invoicing_load_data():
    df_invoice = pd.read_csv("csv_files/Invoices.csv")
    df_invoice.rename(columns={'Job Number': 'Job', 'Invoice Amount (excl VAT)': 'Invoice'}, inplace=True)
    df_invoice['Invoice'] = df_invoice['Invoice'].astype(float)
    df_invoice['Date Inv. Issued'] = pd.to_datetime(df_invoice['Date Inv. Issued'])

    return df_invoice

def invoicing_job_table(df, job_no):
    df_filter = df[(df['Job'] == job_no)]
    df_filter['Sum'] = df_filter['Invoice'].cumsum()


    return df_filter

def spend_on_date(df, date):
    df_date_list = df['Date'].tolist()
    for df_date in df_date_list:
        if df_date - date >= 0:
            match = df_date
        else:
            match = df_date_list[-1]
    df_filter= df[(df['Date'] == match)]
    spend = df_filter['Sum'].iloc[0]
    return spend



# The testing application

job_number = '3104'

wfm_data = wfm.load_data()
invoicing_data = invoicing_load_data()

# Create the spend information for the job:

df_time_table = job_spend(wfm_data, job_number)

print()
print(df_time_table)

# Create the invoicing information for the job:

invoicing_table = invoicing_job_table(invoicing_data, job_number)

print()
print(invoicing_table)
print()

invoicing_date_list = invoicing_table['Date Inv. Issued'].tolist()

spend_list = []

for date in invoicing_date_list:
    try:
        spend_on_date_line = df_time_table.iloc[df_time_table.index.get_loc(date, method='ffill')]
        spend = spend_on_date_line['Sum'].round(2)
    except:
        spend = df_time_table['Sum'].iloc[-1]
    spend_list.append(spend)

    print(f'{date} - £{spend}')

print(spend_list)

invoicing_table['Spend'] = spend_list

print(invoicing_table)

