# Chapter 5: Defining dependencies between tasks

## Beginning-of-chapter overview

* How to define task dependencies in a DAG
* How to implement joins using trigger rules
* How to make tasks conditional 
* How trigger rules affect task execution
* How to use XComs to share state between tasks
* Taskflow API (Airflow 2): how it can help simplify Python-heavy DAGS

## Branching, condition-checking, BranchPythonOperator 

It's possible to create a *fan-in structure* for multiple items that feed into a single downstream task. 

```
# Listing 5.3
start = DummyOperator(task_id='start')
start >> [fetch_weather, fetch_sales]
fetch_weather >> clean_weather
fetch_sales >> clean_sales 

# Listing 5.5 
[clean_weather, clean_sales] >> join_datasets >> train_model >> deploy_model 
```

Branching: e.g. when data needs to come from different sources. Branching within the DAG is preferred: easier to see & troubleshoot. 

```
# branching within the cleaning task & fetch task (latter not shown) 

def _clean_sales(**context): 
  if context['execution_date'] < ERP_CHANGE_DATE: _clean_sales_old(**context)
  else: _clean_sales_new
  
# branching within the DAG: preferred
def _pick_erp_system(**context): 
  if context['execution_date'] < ERP_CHANGE_DATE: return "fetch_sales_old"
  else: return "fetch_sales_new"
  
# define new BranchPythonOperator
pick_erp_system = BranchPythonOperator(task_id = 'pick_erp_system', python_callable=_pick_erp_system,)

# change trigger rules
join_branch = DummyOperator(task_id = 'join_erp_branch', trigger_rule = 'none_failed')

# define dependencies 
start_task >> pick_erp_system >> [fetch_sales_old, fetch_sales_new] >> [clean_sales_old, clean_sales_new] >> join_branch >> join_datasets >> train_model >> deploy_model 


```
