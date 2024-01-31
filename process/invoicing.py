import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import calendar

pd.options.mode.chained_assignment = None  # default='warn'

pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 1000)
pd.options.display.float_format = '{:.2f}'.format

def load_data():
    df_invoice = pd.read_csv("csv_files/Invoices.csv")
    df_invoice.rename(columns={'Job Number': 'Job', 'Invoice Amount (excl VAT)': 'Invoice'}, inplace=True)
    df_invoice['Invoice'] = df_invoice['Invoice'].astype(float)
    df_invoice['Date Inv. Issued'] = pd.to_datetime(df_invoice['Date Inv. Issued'])

    return df_invoice

# processes the invoicing and returns a dataframe
def per_job(df_invoice):

    invoice_jobs = df_invoice['Job'].unique().tolist()

    job_invoices = []

    for job in invoice_jobs:
        df_filter = df_invoice[(df_invoice['Job'] == job)]
        job_invoice = df_filter['Invoice'].sum()
        job_invoices.append(job_invoice)

    df_job_invoices = pd.DataFrame({'Job': invoice_jobs, 'Invoiced': job_invoices})

    return df_job_invoices


def job_table(df, job_no):

    df_invoicing_filter = df[(df['Job'] == job_no)]

    ############# Look to remove this section ################################################

    invoice_ref = df_invoicing_filter['Invoice No'].tolist()

    dates = []

    for item in invoice_ref:
        year = item[0:2]
        month = item[2:4]
        day = "01"
        string = '20' + year + "-" + month + "-" + day

        date_obj = datetime.strptime(string, '%Y-%m-%d')
        last_day = calendar.monthrange(date_obj.year, date_obj.month)[1]

        end_of_month = '20' + year + "-" + month + "-" + str(last_day)

        dates.append(end_of_month)

    df_invoicing_filter['Date'] = np.array(dates)
    df_invoicing_filter['Date'] = pd.to_datetime(df_invoicing_filter['Date'])

    ##########################################################################################

    df_invoicing_filter['Sum'] = df_invoicing_filter['Invoice'].cumsum()

    if not df_invoicing_filter.shape[0] == 0:
        invoiced = df_invoicing_filter['Sum'].iloc[-1]
    else:
        invoiced = 0

    return df_invoicing_filter, invoiced