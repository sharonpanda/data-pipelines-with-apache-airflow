# Chapter 5: Defining dependencies between tasks

* How to define task dependencies in a DAG
* How to implement joins using trigger rules
* How to make tasks conditional 
* How trigger rules affect task execution
* How to use XComs to share state between tasks
* Taskflow API (Airflow 2): how it can help simplify Python-heavy DAGS

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

Branching: e.g. when data needs to come from different sources. 
