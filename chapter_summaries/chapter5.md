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
start_task >> pick_erp_system >> [fetch_sales_old, fetch_sales_new] >> [clean_sales_old, clean_sales_new] >> join_branch 
join_branch >> join_datasets >> train_model >> deploy_model 
```

Conditional tasks: e.g. run only when certain data sets are available or deploy only for most recent execution date. 

* Conditions within tasks have same drawback as earlier branching implementation. Can't see and track within Airflow UI!
* Use new AirflowSkipException 

```
def _latest_only(**context): 
  # define boundaries for execution window
  left_window = context['dag'].following_schedule(context['execution_date'])
  right_window = context['dag'].following_schedule(left_window) 
  now = pendulum.utcnow()
  if not left_window < now <= right_window: 
    raise AirflowSkipException("Not the most recent run!")
    
latest_only = PythonOperator(task_id = 'latest_only', python_callable=_latest_only, dag=dag)
latest_only >> deploy_model 
```

What is a trigger rule? 
* Default: `all_success`. All previous tasks must have succeeded else failure is propagated.
* Other trigger rules: 
  * `all_failed`: triggers when all parent tasks have failed (or failure has propagated)
  * `all_done`: triggers when all parents are done (regardless of success or fail) 
  * `one_failed`: triggers as soon as 1 parent fails
  * `one_success`: triggers as soon as 1 parent succeeds
  * `none_failed`: triggers if no fails (either success or skip)
  * `none_skipped`: triggers if no skips (either success or failure)
  * `dummy`: triggers regardless of any upstream state



## Sharing data between tasks 

* `xcom_push` method: to publish xcom values explicitly within task. 
  * view published xcom values in web interface in admin > xcoms 


```
def _train_model(**context): 
  model_id = str(uuid.uid4())
  context['task_instance'].xcom_push(key='model_id', value=model_id)

train_model = PythonOperator(task_id='train_model', python_callable=_train_model,)

def _deploy_model(**context): 
  model_id = context['task_instance'].xcom_pull(task_ids='train_model', key='model_id'

deploy_model = PythonOperator(task_id='deploy_model', python_callable=_deploy_model)
```
