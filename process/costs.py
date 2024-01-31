import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'

pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 1000)
pd.options.display.float_format = '{:.2f}'.format

def load_data():
    df = pd.read_csv("csv_files/Job Cost Report.csv")
    df.rename(columns={'[Job] Job No.': 'Job',
                             '[Cost] Date': 'Date',
                             '[Cost] Description': 'Description',
                             '[Cost] Cost': 'Cost'
                             }, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Cost'] = df['Cost'].str.replace(',', '').astype(float)
    df['Job'] = df['Job'].astype(str)

    return df


def per_job(df):

    cost_jobs = df['Job'].unique().tolist()

    job_cost = []
    for job in cost_jobs:
        df_filter = df[(df['Job'] == job)]
        job_spend = df_filter['Cost'].sum()
        job_cost.append(job_spend)

    df_costs = pd.DataFrame({'Job': cost_jobs, 'Cost': job_cost})

    return df_costs


def costs(df, job_no):
    cost_jobs = df['Job'].unique().tolist()

    job_cost = []
    for job in cost_jobs:
        df_filter = df[(df['Job'] == job)]
        job_spend = df_filter['Cost'].sum()
        job_cost.append(job_spend)

    df_costs = pd.DataFrame({'Job': cost_jobs, 'Cost': job_cost})

    df_filter = df_costs[(df_costs['Job'] == job_no)]

    if df_filter.empty:
        job_cost = 0
    else:
        job_cost = df_filter['Cost'].iloc[0]

    return job_cost


def job_table(df, job_no):
    df_filter = df[(df['Job'] == job_no)]
    df_filter['Sum'] = df_filter['Cost'].cumsum()
    df_filter['Date'] = df_filter['Date'].dt.date

    return df_filter
