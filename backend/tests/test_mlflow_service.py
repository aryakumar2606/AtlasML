
from unittest.mock import patch

from backend.services.mlflow_service import end_mlflow_run


@patch("backend.services.mlflow_service.mlflow.end_run")
@patch("backend.services.mlflow_service.logger")
def test_end_mlflow_run_finished(logger, mock_end_run):
    end_mlflow_run()

    mock_end_run.assert_called_once_with(status="FINISHED")
    logger.info.assert_called_once_with("MLflow run completed.")


@patch("backend.services.mlflow_service.mlflow.end_run")
@patch("backend.services.mlflow_service.logger")
def test_end_mlflow_run_failed(logger, mock_end_run):
    end_mlflow_run(status="FAILED")

    mock_end_run.assert_called_once_with(status="FAILED")
    logger.warning.assert_called_once_with(
        "MLflow run ended with FAILED status."
    )
