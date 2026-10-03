import mlflow

from backend.logger import logger


def start_mlflow_run(experiment_name: str, run_name: str | None = None):
    mlflow.set_experiment(experiment_name)

    run = mlflow.start_run(run_name=run_name)

    logger.info(
        f"MLflow run started: {run.info.run_id}"
    )

    return run


def log_parameter(key: str, value):
    mlflow.log_param(key, value)


def log_metric(key: str, value: float):
    mlflow.log_metric(key, value)


def log_parameters(parameters: dict):
    for key, value in parameters.items():
        mlflow.log_param(key, value)


def log_metrics(metrics: dict):
    for key, value in metrics.items():
        if isinstance(value, (int, float)):
            mlflow.log_metric(key, value)
            
def log_pipeline_info(
    experiment_id: str,
    dataset_name: str,
    rows: int,
    columns: int,
):
    mlflow.log_param("experiment_id", experiment_id)
    mlflow.log_param("dataset_name", dataset_name)
    mlflow.log_param("rows", rows)
    mlflow.log_param("columns", columns)
    
def log_agent_metadata(agent_name: str, metadata: dict):
    for key, value in metadata.items():
        if value is None:
            continue

        if isinstance(value, (str, int, float, bool)):
            mlflow.log_param(
                f"{agent_name}_{key}",
                value,
            )
        else:
            mlflow.log_param(
                f"{agent_name}_{key}",
                str(value),
            )


def end_mlflow_run():
    mlflow.end_run()

    logger.info("MLflow run completed.")
    
