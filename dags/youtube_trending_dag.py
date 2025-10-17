from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from scripts.load_to_db import load_latest
from datetime import datetime, timedelta
from pathlib import Path

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dags_dir = Path(__file__).resolve().parent
project_root = dags_dir.parents[0]
scripts_dir = dags_dir / "scripts"

with DAG(
    dag_id="youtube_trending_pipeline",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule="*/15 * * * *",
    # schedule="@daily",
    catchup=False,
) as dag:

    fetch = BashOperator(
        task_id="fetch_data",
        bash_command=f"python3 {scripts_dir}/fetch_trending.py",
    )

    load = PythonOperator(
        task_id="load_to_db",
        python_callable=load_latest,
        op_kwargs={"dry_run": False},
    )

    transform = BashOperator(
        task_id="run_dbt",
        bash_command=(
            f"if [ -d {project_root}/dbt ]; then "
            f"cd {project_root}/dbt && dbt run; "
            f"else echo 'dbt project not found at {project_root}/dbt' >&2; exit 1; fi"
        ),
    )

    fetch >> load >> transform