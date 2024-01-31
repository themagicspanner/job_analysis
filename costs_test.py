from process import costs
import random

df_costs_data = costs.load_data()
print(f'\n\nRaw Costs Data\n==========================\n')
print(df_costs_data)

df_costs_per_job = costs.per_job(df_costs_data)
print(f'\n\nCost per Job\n==========================\n')
print(df_costs_per_job)

job_list = df_costs_per_job['Job'].tolist()
job_no = random.choice(job_list)

df_job_costs = costs.costs(df_costs_per_job, job_no)
print(f'\n\nTotal Job Costs:\n==========================\n')
print(f'£{df_job_costs}')

df_job_costs_table = costs.job_table(df_costs_data, job_no)
print(f'\n\nJob Cost Table:\n==========================\n')
print(df_job_costs_table)
