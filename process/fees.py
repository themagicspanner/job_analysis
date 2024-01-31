import pandas as pd

def load_data():
    df_fees = pd.read_csv("csv_files/Agreed Fees.csv")
    df_fees['Fee Proposal'] = df_fees['Fee Proposal'].astype(float)
    df_fees['Variations'] = df_fees['Variations'].astype(float)
    df_fees.fillna(0, inplace=True)
    df_fees['Total Fee'] = df_fees['Fee Proposal'] + df_fees['Variations']
    df_fees.fillna(0, inplace=True)

    return df_fees

def fees(df, job_no):
    df_filter = df[(df['Job'] == job_no)]

    if df_filter.empty:
        fee = 0
        variations = 0
    else:
        fee = df_filter['Fee Proposal'].iloc[0]
        variations = df_filter['Variations'].iloc[0]

    fee_total = fee + variations

    return fee, variations, fee_total