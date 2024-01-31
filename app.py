from process import costs, invoicing, fees, wfm, process

import dash
from dash import dcc, html, Input, Output, dash_table
from dash.dash_table import FormatTemplate
import dash_bootstrap_components as dbc
import pandas as pd

###########################################
# This is the overview section of the app #
###########################################

pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 10000)
pd.options.display.float_format = '{:.2f}'.format

# Load the raw data

df_wfm_data = wfm.load_data()
df_costs_data = costs.load_data()
df_fees_data = fees.load_data()
df_invoices_data = invoicing.load_data()

# proces the data into one line per job table

df_jobs = process.jobs_data(df_wfm_data)

df_costs_per_job = costs.per_job(df_costs_data)

df_invoices_per_job = invoicing.per_job(df_invoices_data)

managers = df_jobs['Manager'].unique().tolist()
managers.sort(key=str.lower)
clients = df_jobs['Client'].unique().tolist()

offices = df_jobs['Office'].unique().tolist()
disciplines = df_jobs['Discipline'].unique().tolist()

df_analysis = process.merge(df_jobs=df_jobs,
                                 df_costs=df_costs_per_job,
                                 df_fees=df_fees_data,
                                 df_invoices=df_invoices_per_job)

df_analysis.reset_index(inplace=True)

# spend_status = df_analysis['Spend Status'].unique().tolist()
invoice_status = df_analysis['Invoiced Status'].unique().tolist()
projected_status = df_analysis['Projected Status'].unique().tolist()

sort_by_list = ['Job', 'Last Activity', '% Spend', '% Invoiced', '% Projected', 'Profit/Loss']


#########################################
# This is the report section of the app #
#########################################

# Create the dropdown list for job selection

dropdown_values = process.job_and_name_list(df_wfm_data)
jobs = df_wfm_data['Job'].unique().tolist()


# ########################
# Create the app layout #
# ########################

app = dash.Dash(
external_stylesheets=[dbc.themes.BOOTSTRAP]
)

app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='Overview', children=[
            dbc.Row([
                dbc.Col([
                    html.H2('Offices'),
                    dcc.Checklist(id='office',
                                  options=[{'label': i, 'value': i} for i in offices],
                                  value=offices,
                                  ),
                ]),
                dbc.Col([
                    html.H2('Disciplines'),
                    dcc.Checklist(id='discipline',
                                  options=[{'label': i, 'value': i} for i in disciplines],
                                  value=disciplines,
                                  # inline=False
                                  ),
                ]),
                # dbc.Col([
                #     html.H2('Spend Status'),
                #     dcc.Checklist(id='spend status',
                #                   options=[{'label': i, 'value': i} for i in spend_status],
                #                   value=spend_status,
                #                   ),
                # ]),
                dbc.Col([
                    html.H2('Invoice Status'),
                    dcc.Checklist(id='invoiced status',
                                  options=[{'label': i, 'value': i} for i in invoice_status],
                                  value=invoice_status,
                                  ),
                ]),
                dbc.Col([
                    html.H2('Projected Status'),
                    dcc.Checklist(id='projected status',
                                  options=[{'label': i, 'value': i} for i in projected_status],
                                  value=projected_status,
                                  ),
                ]),
            ]),

            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id="sorting_dropdown",
                        options=[{'label': x, 'value': x} for x in sort_by_list],
                        value= sort_by_list[0],
                ),
                    ]),

                dbc.Col([
                    dcc.Dropdown(
                        id="order_dropdown",
                        options=[
                            {'label': 'Ascending', 'value': 'Ascending'},
                            {'label': 'Descending', 'value': 'Descending'},
                        ],
                        value= 'Ascending',
                    ),
                    ]),
            ],style={'padding-top':'10px', 'padding-bottom':'10px'}),

                html.Div(id="table",),
        ]),

        dcc.Tab(label='Job Report', children=[
            html.Div([
                dbc.Row([
                    dcc.Dropdown(
                        id="job_dropdown",
                        options=[{'label': x, 'value': y} for x, y in dropdown_values],
                        value=jobs[0],
                    ),
                ]),

                html.H2('Job Information', style={'padding-top':'10px'}),
                html.Div(id="info_table", style={'width': '100%'}),
                html.H2('Financial Overview', style={'padding-top':'20px'}),
                html.Div(id="finance_table", style={'width': '100%'}),
                html.H2('Cost', style={'padding-top': '20px'}),
                html.Div(id="report_costs_table", style={'width': '100%'}),
                html.H2('Spend by Task', style={'padding-top':'20px'}),
                html.Div(id="task_table", style={'width': '100%'}),
                html.H2('Spend by Staff', style={'padding-top':'20px'}),
                html.Div(id="staff_table", style={'width': '100%'}),
                html.H2('Invoicing', style={'padding-top':'20px'}),
                html.Div(id="invoice_table", style={'width': '100%'}),
                html.H2('Spend and Invoicing Graph', style={'padding-top':'20px'}),
                dcc.Graph(id='figure', style={'width': '100%'}),
            ], style={'width': '55%'})
        ]),
    ]),
], style={'padding':'30px', 'padding-bottom':'100px'})

@app.callback(
    # Tab 1 outputs
    Output('table', 'children'),
    # Tab 2 outputs
    Output('info_table', 'children'),
    Output('finance_table', 'children'),
    # Output('spend_table', 'children'),
    Output('report_costs_table', 'children'),
    Output('task_table', 'children'),
    Output('staff_table', 'children'),
    Output('invoice_table', 'children'),
    Output('figure', 'figure'),
    # Tab 1 inputs
    # Input('spend status', 'value'),
    Input('invoiced status', 'value'),
    Input('projected status', 'value'),
    Input('office', 'value'),
    Input('discipline', 'value'),
    Input('sorting_dropdown', 'value'),
    Input('order_dropdown', 'value'),
    # tab 2 inputs
    Input('job_dropdown', 'value'),
)
def create_table(
        # spend_status,
        invoiced_status,
        projected_status,
        office,
        discipline,
        sort_by,
        order,
        job_no
):

    ####################
    # Tab 1 processing #
    ####################

    filtered_table = df_analysis[
        # df_analysis['Spend Status'].isin(spend_status)
        df_analysis['Invoiced Status'].isin(invoiced_status)
        & df_analysis['Projected Status'].isin(projected_status)
        & df_analysis['Office'].isin(office)
        & df_analysis['Discipline'].isin(discipline)
    ]

    if order == 'Ascending':
        order_bool = True
    else:
        order_bool = False

    filtered_table.sort_values(sort_by, ascending=order_bool, inplace=True)

    names = filtered_table['Name']
    trunk_names = []
    for name in names:
        trunk_name = name[:50]
        trunk_names.append(trunk_name)

    filtered_table['Name'] = trunk_names

    # Calculate totals for the bottom row and append

    total_spend = filtered_table['Spend'].sum()
    total_cost = filtered_table['Cost'].sum()
    total_total_spend = total_spend + total_cost
    total_fee_proposals = filtered_table['Fee Proposal'].sum()
    total_variations = filtered_table['Variations'].sum()
    total_total_fee = total_fee_proposals + total_variations
    total_invoiced = filtered_table['Invoiced'].sum()
    # total_invoiced_pct = total_invoiced / total_total_fee
    total_profit = filtered_table['Profit/Loss'].sum()
    total_projected_overspend = filtered_table['Projected Profit/Loss'].sum()
    # total_spend_projected = total_total_spend / total_invoiced_pct
    # total_spend_projected_pct = total_spend_projected / total_total_fee

    table_row = {'Job': '',
                 'Name': '',
                 'Client': '',
                 'Discipline': '',
                 'Office': '',
                 'Account Manager': '',
                 'Manager': '',
                 'Spend': total_spend,
                 'Last Activity': '',
                 'Cost': total_cost,
                 'Total Spend': total_total_spend,
                 'Fee Proposal': total_fee_proposals,
                 'Variations': total_variations,
                 'Total Fee': total_total_fee,
                 '% Spend': '',
                 'Spend Status': '',
                 'Invoiced': total_invoiced,
                 '% Invoiced': '',
                 'Profit/Loss': total_profit,
                 'Invoiced Status': '',
                 'Projected': '',
                 'Projected Profit/Loss': total_projected_overspend,
                 '% Projected': ''
    }

    df_summary = pd.DataFrame(table_row, index=[0])

    filtered_table = pd.concat([filtered_table, df_summary])



    # set number formats

    money = {'locale': {'symbol': ['\xA3', '']}, 'nully': '', 'prefix': None, 'specifier': '$,.2f'}
    percentage = FormatTemplate.percentage(1)

    # Create Dash Datatable

    table1 = dash_table.DataTable(
        data=filtered_table.to_dict('records'),
        columns=[
            dict(id='Job', name='Job No.'),
            dict(id='Name', name='Job Title'),
            # dict(id='Client', name='Client'),
            dict(id='Discipline', name='Discipline'),
            dict(id='Office', name='Office'),
            # dict(id='Account Manager', name='Account Manager'),
            # dict(id='Manager', name='Manager'),
            dict(id='Last Activity', name='Last Activity'),
            # dict(id='Fee Proposal', name='Fee', type='numeric', format=money),
            # dict(id='Variations', name='Variations', type='numeric', format=money),
            dict(id='Total Fee', name='Total Fee', type='numeric', format=money),
            dict(id='Cost', name='Ex. Cost', type='numeric', format=money),
            dict(id='MHB Fee', name='MHB Fee', type='numeric', format=money),
            dict(id='Spend', name='MHB Spend', type='numeric', format=money),
            dict(id='Total Spend', name='Total Spend', type='numeric', format=money),
            dict(id='% Spend', name='% Spend', type='numeric', format=percentage),
            dict(id='Invoiced', name='Invoiced', type='numeric', format=money),
            dict(id='% Invoiced', name='% Invoiced', type='numeric', format=percentage),
            dict(id='Profit/Loss', name='Profit/Loss (+/-)', type='numeric', format=money),
            dict(id='Projected Spend', name='Proj. Spend', type='numeric', format=money),
            dict(id='Projected Profit/Loss', name='Proj. Profit/Loss (+/-)', type='numeric', format=money),
            dict(id='% Projected', name='Proj. %', type='numeric', format=percentage),

        ],
        style_as_list_view=False,
        # export_format="csv",
        style_data_conditional=[
            {
                "if": {"row_index": len(filtered_table) - 1},
                "fontWeight": "bold",
                'backgroundColor': 'lightgrey',
                'border-top': '2px solid black',
                'border-bottom': '2px solid black'
            },

        ],
        style_header={
            'fontWeight': 'bold'
        },
        style_cell={'padding-right': '3px', 'padding-left': '3px'
                    },
    )

    ####################
    # Tab 2 processing #
    ####################

    info = process.information(df_wfm_data, job_no)

    (spend,
     task,
     staff,
     job_mhb_spend) = process.job_spend_tables(df_wfm_data, job_no)

    (job_invoicing,
     job_total_invoiced) = invoicing.job_table(df_invoices_data, job_no)

    (job_fee,
     job_variations,
     job_total_fee) = fees.fees(df_fees_data, job_no)

    job_costs = costs.costs(df_costs_per_job, job_no)
    job_costs_pct = job_costs / job_total_fee
    job_mhb_fee = job_total_fee - job_costs
    job_mhb_fee_pct = job_mhb_fee / job_total_fee

    job_invoiced_total_pct = job_total_invoiced / job_total_fee

    job_total_spend = job_costs + job_mhb_spend
    job_total_spend_pct = job_total_spend / job_total_fee

    job_mhb_spend_pct = job_mhb_spend / job_mhb_fee

    df_job_costs_table = costs.job_table(df_costs_data, job_no)

    if 1 > job_invoiced_total_pct > 0:
        job_spend_projected = job_mhb_spend / job_invoiced_total_pct + job_costs
        job_spend_projected_pct = job_spend_projected / job_total_fee
    else:
        job_spend_projected = "-"
        job_spend_projected_pct = "-"

    financial_info = [["Fee", job_fee, ""],
                      ["Variations", job_variations, ""],
                      ["Total Fee", job_total_fee, ""],
                      ["Costs", job_costs, job_costs_pct],
                      ["MHB Fee", job_mhb_fee, job_mhb_fee_pct],
                      ["MHB Spend", job_mhb_spend, job_mhb_spend_pct],
                      ["Total Spend", job_total_spend, job_total_spend_pct],
                      ["Total Invoiced", job_total_invoiced, job_invoiced_total_pct],
                      ["Projected Spend", job_spend_projected, job_spend_projected_pct]]

    financial = pd.DataFrame(financial_info)

    report_figure = process.spend_graph(df_wfm_data, job_invoicing, job_no, job_total_fee, df_job_costs_table,)

    report_info_table = dash_table.DataTable(
        data=info.to_dict('records'),
        columns=[dict(id='0', name=''),
                 dict(id='1', name='value'),
                 ],
        # style_header={'display': 'none'},
    )

    report_finance_table = dash_table.DataTable(
        data=financial.to_dict('records'),
        columns=[dict(id='0', name=''),
                 dict(id='1', name='value', type='numeric', format=money),
                 dict(id='2', name='%', type='numeric', format=percentage)
                 ],
        # style_header={'display': 'none'},
    )

    report_costs_table = dash_table.DataTable(
        data=df_job_costs_table.to_dict('records'),
        columns=[dict(id='Date', name='Date'),
                 dict(id='Description', name='Description', type='numeric', format=money),
                 dict(id='Cost', name='Cost', type='numeric', format=money),
                 ],
        # style_as_list_view=True,
    )

    report_task_table = dash_table.DataTable(
        data=task.to_dict('records'),
        columns=[dict(id='Task', name=''),
                 dict(id='Total', name='Spend', type='numeric', format=money),
                 dict(id='%', name='%', type='numeric', format=percentage)
                 ],
        # style_as_list_view=True,
    )

    report_staff_table = dash_table.DataTable(
        data=staff.to_dict('records'),
        columns=[dict(id='Staff', name=''),
                 dict(id='Total', name='Spend', type='numeric', format=money),
                 dict(id='%', name='%', type='numeric', format=percentage)
                 ],
        # style_as_list_view=True,
    )

    report_invoice_table = dash_table.DataTable(
        data=job_invoicing.to_dict('records'),
        columns=[dict(id='Invoice No', name='Invoice No'),
                 dict(id='Date Inv. Issued', name='Date'),
                 dict(id='Invoice', name='Invoiced Amount', type='numeric', format=money),
                 dict(id='Sum', name='Invoiced Sum', type='numeric', format=money),
                 ],
        # style_as_list_view=True,
    )



    return (
        # Tab 1 return
        table1,
        # Tab 2 return
        report_info_table,
        report_finance_table,
        report_costs_table,
        report_task_table,
        report_staff_table,
        report_invoice_table,
        report_figure
        )


if __name__ == "__main__":
    app.run_server(debug=True)
