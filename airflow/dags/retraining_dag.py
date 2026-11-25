from datetime import datetime, timezone

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator

ACCURACY_THRESHOLD = 0.75


def collect_data():
    return {"sample_count": 100}


def evaluate_model(ti):
    data = ti.xcom_pull(task_ids="collect_data")
    if not data or data["sample_count"] == 0:
        raise ValueError("Nessun dato disponibile per la valutazione")

    return 0.72


def decide_next_step(ti):
    accuracy = ti.xcom_pull(task_ids="evaluate_model")
    if accuracy is None:
        raise ValueError("Accuracy non disponibile in XCom")

    return "retrain" if accuracy < ACCURACY_THRESHOLD else "skip"


def retrain_model():
    print("Stub: avvio del retraining")


with DAG(
    dag_id="weekly_sentiment_retraining",
    schedule="@weekly",
    start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    tags=["sentiment", "mlops"],
) as dag:
    collect = PythonOperator(
        task_id="collect_data",
        python_callable=collect_data,
    )
    evaluate = PythonOperator(
        task_id="evaluate_model",
        python_callable=evaluate_model,
    )
    decide = BranchPythonOperator(
        task_id="decide",
        python_callable=decide_next_step,
    )
    retrain = PythonOperator(
        task_id="retrain",
        python_callable=retrain_model,
    )
    skip = EmptyOperator(task_id="skip")

    collect >> evaluate >> decide >> [retrain, skip]
