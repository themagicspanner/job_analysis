from process import process, wfm, costs, invoicing, fees
import random

def random_from_list():
    job_list = df_costs_per_job['Job'].tolist()
    return random.choice(job_list)

df_wfm_data = wfm.load_data()
df_costs_data = costs.load_data()
df_fees_data = fees.load_data()
df_invoicing_data = invoicing.load_data()

print(df_invoicing_data)

df_costs_per_job = costs.per_job(df_costs_data)

job_no = random_from_list()

print(f'Job No: {job_no}')

df_cost_job_table = costs.job_table(df_costs_data, job_no)

print(df_cost_job_table)

(job_fee, job_variations, job_total_fee) = fees.fees(df_fees_data, job_no)

print(f'Fee: £{job_fee}, Variations: £{job_variations}, Total Fee: £{job_total_fee}')

(job_invoicing, job_total_invoiced) = invoicing.job_table(df_invoicing_data, job_no)


figure = process.spend_graph(df_wfm_data, job_invoicing, job_no, job_total_fee, df_cost_job_table)

figure.show()