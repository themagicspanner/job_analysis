import io

import numpy as np
import pandas as pd
import msoffcrypto
from datetime import datetime

pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 10000)
pd.options.display.float_format = '{:.2f}'.format

passwd = 'Samsung8'

decrypted_workbook = io.BytesIO()
with open('S:/3. Financial\Invoice Tracker UPDATED.xlsx', 'rb') as file:
    office_file = msoffcrypto.OfficeFile(file)
    office_file.load_key(password=passwd)
    office_file.decrypt(decrypted_workbook)


####################################
# Export the invoicing information #
####################################

df_invoices = pd.read_excel(decrypted_workbook, sheet_name='invoices by no.')
df_invoices_filtered = df_invoices[df_invoices['Invoice No'].notnull()]
df_export = df_invoices_filtered[['Invoice No',
                                  'Client',
                                  'Job Name',
                                  'Job Number',
                                  'Invoice Amount (excl VAT)',
                                  'Date Inv. Issued']]

invoice_dates_str = df_export['Date Inv. Issued']
invoice_dates = []

for date in invoice_dates_str:
    if not type(date) is str:
        invoice_dates.append(date)
    else:
        invoice_dates.append(np.nan)

df_export['Date Inv. Issued'] = invoice_dates

df_export.to_csv('csv_files/Invoices.csv', index=False)


###############################
# Export the fees information #
###############################

df_fees = pd.read_excel(decrypted_workbook, sheet_name='Jobs, Fees & Outstanding balanc')
df_fees_filtered = df_fees[df_fees['Unnamed: 1'].notnull()]

df_fees_export = df_fees_filtered[['Unnamed: 1',
                                   'Fee Proposal',
                                   'Variations']]
df_fees_export.rename(columns={"Unnamed: 1": "Job"}, inplace=True)


# Remove any non-numerical values from the fee proposal column

fee_proposals = df_fees_export['Fee Proposal']
fee_proposals_float = []

for fee in fee_proposals:
    try:
        fee_float = float(fee)
    except ValueError:
        fee_float = 0
    fee_proposals_float.append(fee_float)

df_fees_export['Fee Proposal'] = fee_proposals_float


# Remove any non-numerical values from the variations column

variations = df_fees_export['Variations']
variations_float = []

for variation in variations:
    try:
        variation_float = float(variation)
    except ValueError:
        variation_float = 0
    variations_float.append(variation_float)

df_fees_export['Variations'] = variations_float



df_fees_export = df_fees_export.fillna(0)

df_fees_export.to_csv('csv_files/Agreed Fees.csv', index=False)
