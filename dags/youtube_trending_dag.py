from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="youtube_trending_pipeline",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule="*/15 * * * *",
    catchup=False,
) as dag:

    fetch = BashOperator(
        task_id="fetch_data",
        bash_command=f"python3 /Users/mie/Desktop/side_projects/YouTubeTrends/scripts/fetch_trending.py",
    )

    load = BashOperator(
        task_id="load_to_db",
        bash_command="python3 /Users/mie/Desktop/side_projects/YouTubeTrends/scripts/load_to_db.py"
    )

    transform = BashOperator(
        task_id="run_dbt",
        bash_command="cd dbt && dbt run"
    )

    fetch >> load >> transform