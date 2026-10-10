
from unittest.mock import MagicMock, patch

import pytest

from backend.models.pipeline_state import PipelineState
from backend.pipelines.pipeline_manager import PipelineManager


def test_pipeline_marks_experiment_failed_when_agent_fails():
    manager = PipelineManager()

    state = MagicMock(spec=PipelineState)
    state.experiment_id = "test-experiment-id"
    state.dataset_path = "test.csv"
    state.summary = {"rows": 10, "columns": 2}
    state.current_agent = None

    fake_execution = MagicMock()
    fake_execution.execution_id = "test-execution-id"

    with (
        patch(
            "backend.pipelines.pipeline_manager.start_mlflow_run"
        ),
        patch(
            "backend.pipelines.pipeline_manager.log_pipeline_info"
        ),
        patch(
            "backend.pipelines.pipeline_manager.create_agent_execution",
            return_value=fake_execution,
        ),
        patch(
            "backend.pipelines.pipeline_manager.get_next_attempt_number",
            return_value=1,
        ),
        patch(
            "backend.pipelines.pipeline_manager.complete_agent_execution"
        ),
        patch(
            "backend.pipelines.pipeline_manager.fail_agent_execution"
        ) as fail_execution,
        patch(
            "backend.pipelines.pipeline_manager.update_experiment_status"
        ) as update_status,
        patch(
            "backend.pipelines.pipeline_manager.end_mlflow_run"
        ) as end_mlflow,
        patch.object(
            manager.agents[0],
            "run",
            side_effect=RuntimeError("Test agent failure"),
        ),
    ):
        with pytest.raises(
            RuntimeError,
            match="Test agent failure",
        ):
            manager.run_pipeline(state, MagicMock())

    fail_execution.assert_called_once()

    failed_update = [
        call
        for call in update_status.call_args_list
        if call.kwargs.get("status") == "failed"
    ]

    assert failed_update, "Experiment was not marked as failed"

    assert (
        failed_update[-1].kwargs["error_message"]
        == "Test agent failure"
    )

    end_mlflow.assert_called_once_with(status="FAILED")
