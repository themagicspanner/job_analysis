import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
pio.templates.default = "plotly_white"


pd.options.mode.chained_assignment = None  # default='warn'

pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 1000)
pd.options.display.float_format = '{:.2f}'.format


# converts the workflowmax dataframe to a line per job dataframe
def jobs_data(df):
    df_jobs = (df[["Job", "Name", "Client", "Discipline", "Office", "Account Manager", "Manager"]]
               .drop_duplicates().set_index('Job'))

    jobs = df_jobs.index.tolist()

    spend = []
    last_activity = []

    for job in jobs:
        df_filtered = df[(df['Job'] == job)]

        job_spend = df_filtered['Total'].sum()
        spend.append(job_spend)

        dates = df_filtered['Date'].tolist()
        last = max(dates)
        last_activity.append(last)

    df_jobs['Spend'] = spend
    df_jobs['Last Activity'] = last_activity

    return df_jobs


def merge(df_jobs, df_costs, df_fees, df_invoices):

    # 1st merge

    df = pd.merge(df_jobs, df_costs, how='left', on='Job')
    df["Cost"] = df["Cost"].fillna(0)
    df['Total Spend'] = df['Spend'] + df['Cost']

    # 2nd merge

    df = pd.merge(df, df_fees, how='left', on='Job')
    df["MHB Fee"] = df["Total Fee"] - df["Cost"]
    df['% Spend'] = df['Spend'] / df['MHB Fee']
    df['Spend Status'] = np.where(df['% Spend'] > 1, 'Overspend', 'Underspend')

    # 3rd merge

    df = pd.merge(df, df_invoices, how='left', on='Job').set_index('Job')
    df["Invoiced"] = df["Invoiced"].fillna(0)
    df['% Invoiced'] = df['Invoiced'] / df['Total Fee']

    # Set the fee/invoicing status

    fee = df["Total Fee"]
    invoiced = df["Invoiced"]
    pct_invoiced = df["% Invoiced"]

    conditions_1 = [
        (fee == 0),
        (invoiced == 0),
        (pct_invoiced == 1),
        (pct_invoiced > 1),
        (pct_invoiced < 1)
    ]

    returns_1 = [
        "No Fee",
        "No Invoicing",
        "Complete",
        "Missing fee",
        "In Progress"
    ]

    df["Invoiced Status"] = np.select(conditions_1, returns_1, np.nan)


    # Calculate the projected figures

    df['Projected Spend'] = np.where((df['% Invoiced'] < 1) & (df['% Invoiced'] > 0),
                                     df['Spend'] / df['% Invoiced'] + df['Cost'],
                                     np.nan)

    df['Projected Profit/Loss'] = df['Total Fee'] - df['Projected Spend']
    df['% Projected'] = df['Projected Spend'] / df['Total Fee']

    df['Profit/Loss'] = np.where((df['% Invoiced'] == 1), df['Total Fee'] - df['Total Spend'],
                               np.nan)



    # Remove non-values from the dataframes

    df.replace([np.inf, -np.inf], 0, inplace=True)
    # df.replace([np.nan], 0, inplace=True)

    # Set the projected status

    pct_projected = df['% Projected']

    conditions_2 = [
        (pct_projected > 1),
        (pct_projected <= 1)
    ]

    returns_2 = [
        'Overspend',
        'Underspend'
    ]

    df["Projected Status"] = np.select(conditions_2, returns_2, "No Projection")

    return df


def job_spend_tables(df, job_no):

    df_job = df[(df['Job'] == job_no)]

    # create lists of task and staff for the job

    tasks = df_job['Task'].unique()
    staff = df_job['Staff'].unique()

    # Create a dataframe with the tasks as the first column

    df_table = pd.DataFrame({'Task': tasks})

    # for each member of staff cycle through the tasks and add the total spend for each task

    for person in staff:
        totals = []
        df_person = df_job[(df_job['Staff'] == person)]

        for task in tasks:
            df_person_task = df_person[(df_person['Task'] == task)]
            person_task_total = df_person_task['Total'].sum()
            totals.append(person_task_total)

        df_table[person] = totals

    df_table.set_index("Task", inplace=True)
    df_table['Total'] = df_table.iloc[:, :].sum(axis=1)
    df_table.loc['Total'] = df_table.sum()

    # total spend is the last row of the totals column

    spend = df_table['Total'].iloc[-1]

    # create the tasks table

    df_task_table = df_table['Total'].to_frame().reset_index()
    df_task_table['%'] = df_task_table['Total'] / spend
    df_task_table['%'].iloc[-1] = ""


    # create the staff table

    df_staff_table = df_table.transpose()
    df_staff_table = df_staff_table['Total'].to_frame().reset_index()
    df_staff_table.rename(columns={'index': 'Staff'}, inplace=True)
    df_staff_table['%'] = df_staff_table['Total'] / spend
    df_staff_table['%'].iloc[-1] = ""

    return df_table, df_task_table, df_staff_table, spend


def spend_graph(df_wfm, df_invoicing, job_no, total_fee, df_cost):
    df_wfm_filter = df_wfm[(df_wfm['Job'] == job_no)]

    df_time = df_wfm_filter[['Date', 'Total']]
    df_time['Date'] = pd.to_datetime(df_time['Date'])
    df_time = df_time.groupby(['Date']).agg('sum')
    df_time.sort_index(inplace=True)
    df_time['Sum'] = df_time['Total'].cumsum()

    df_invoice_filter = df_invoicing[(df_invoicing['Job'] == job_no)]

    # Calculate the start and end dates for the graph

    start_date_time = df_time.index.min()
    end_date_time = df_time.index.max()
    end_date_invoiced = df_invoice_filter['Date'].max()
    end_date = max(end_date_time, end_date_invoiced)
    total_cost = df_cost[(df_cost['Job'] == job_no)]['Cost'].sum()

    # add start and end lines to the cost dataframe

    first_row = {'Job': job_no, 'Date': start_date_time, 'Description': "", "Cost": 0, 'Sum': 0}
    last_row = {'Job': job_no, 'Date': end_date, 'Description': "", "Cost": 0, 'Sum': total_cost}
    df_cost = pd.concat([df_cost, pd.DataFrame.from_records([first_row, last_row])])

    df_cost.sort_values(by=['Date'], inplace=True)

    df_cost['Fee Minus Costs'] = total_fee - df_cost['Sum']

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=df_time.index,
            y=df_time['Sum'],
            name='Spend',
            mode='lines',
            line_shape='hv',
            line = dict(color='blue')

        )
    )

    figure.add_trace(
        go.Scatter(
            x=df_invoice_filter['Date Inv. Issued'],
            y=df_invoice_filter['Sum'],
            name='Invoicing',
            mode='markers+lines',
            line_shape='hv',
            line = dict(color='red', dash='dot')
        )
    )

    figure.add_trace(
        go.Scatter(
            x=df_cost['Date'],
            y=df_cost['Fee Minus Costs'],
            name='Fee - Costs',
            mode = 'markers+lines',
            line_shape='hv',
            line = dict( color='blue', dash='dot')
        )
    )

    figure.add_hline(
        y=total_fee,
        name="Total Fee",
        line_color="red",
        opacity = .5
    )


    figure.update_traces(hoverinfo='x+y')
    figure.update_layout(showlegend=True,
                         xaxis_title="Date",
                         yaxis_title="Spend/Invoicing"
                         )

    return figure


def job_and_name_list(df):

    df_jobs = df[["Job", "Name"]].drop_duplicates().set_index('Job')

    jobs = df_jobs.index.tolist()
    names = df_jobs['Name'].tolist()

    job_and_name = []
    i = 0
    for j in jobs:
        j_and_n = j + " - " + names[i]
        job_and_name.append(j_and_n)
        i += 1

    job_and_name_list = list(zip(job_and_name, jobs))

    return job_and_name_list


def information(df, job_no):
    df_filtered = df[(df['Job'] == job_no)]

    job_name = df_filtered['Name'].iloc[0]
    job_manager = df_filtered['Manager'].iloc[0]
    office = df_filtered['Office'].iloc[0]
    discipline = df_filtered['Discipline'].iloc[0]

    # create the job info dataframe

    job_info = [["Job No", job_no],
                ["Name", job_name],
                ["Office", office],
                ["Discipline", discipline],
                ["Manager", job_manager]]

    df_job_info = pd.DataFrame(job_info)

    return df_job_info
