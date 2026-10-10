
from unittest.mock import MagicMock

from backend.services.agent_execution_service import (
    create_agent_execution,
    get_next_attempt_number,
    complete_agent_execution,
    fail_agent_execution,
)


def test_create_agent_execution():
    db = MagicMock()

    execution = create_agent_execution(
        db=db,
        experiment_id="test-experiment",
        agent_name="FeatureAgent",
        attempt_number=1,
    )

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(execution)

    assert execution.experiment_id == "test-experiment"
    assert execution.agent_name == "FeatureAgent"
    assert execution.status == "running"
    assert execution.attempt_number == 1


def test_get_next_attempt_number_when_no_previous_execution():
    db = MagicMock()
    db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

    attempt_number = get_next_attempt_number(
        db=db,
        experiment_id="test-experiment",
        agent_name="FeatureAgent",
    )

    assert attempt_number == 1


def test_get_next_attempt_number_after_previous_attempt():
    db = MagicMock()
    previous_execution = MagicMock()
    previous_execution.attempt_number = 2

    db.query.return_value.filter.return_value.order_by.return_value.first.return_value = (
        previous_execution
    )

    attempt_number = get_next_attempt_number(
        db=db,
        experiment_id="test-experiment",
        agent_name="FeatureAgent",
    )

    assert attempt_number == 3


def test_complete_agent_execution():
    db = MagicMock()
    execution = MagicMock()
    execution.execution_id = "execution-123"

    db.query.return_value.filter.return_value.first.return_value = execution

    result = complete_agent_execution(
        db=db,
        execution_id="execution-123",
        execution_time=1.25,
    )

    assert result is execution
    assert execution.status == "completed"
    assert execution.execution_time == 1.25
    assert execution.error_message is None
    assert execution.completed_at is not None

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(execution)


def test_fail_agent_execution():
    db = MagicMock()
    execution = MagicMock()
    execution.execution_id = "execution-123"

    db.query.return_value.filter.return_value.first.return_value = execution

    result = fail_agent_execution(
        db=db,
        execution_id="execution-123",
        error_message="Test failure",
        execution_time=0.75,
    )

    assert result is execution
    assert execution.status == "failed"
    assert execution.error_message == "Test failure"
    assert execution.execution_time == 0.75
    assert execution.completed_at is not None

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(execution)
    


from unittest.mock import MagicMock

def test_get_next_attempt_number_after_failed_attempt():
    from backend.services.agent_execution_service import (
        get_next_attempt_number,
    )

    db = MagicMock()

    failed_execution = MagicMock()
    failed_execution.attempt_number = 1

    query = db.query.return_value
    query.filter.return_value = query
    query.order_by.return_value = query
    query.first.return_value = failed_execution

    result = get_next_attempt_number(
        db,
        experiment_id="experiment-123",
        agent_name="FeatureAgent",
    )

    assert result == 2

def test_retry_creates_new_execution_record():
    

    from backend.services.agent_execution_service import (
        create_agent_execution,
    )

    db = MagicMock()

    retry_execution = create_agent_execution(
        db=db,
        experiment_id="experiment-123",
        agent_name="FeatureAgent",
        attempt_number=2,
    )

    assert retry_execution.experiment_id == "experiment-123"
    assert retry_execution.agent_name == "FeatureAgent"
    assert retry_execution.attempt_number == 2
    assert retry_execution.status == "running"
    assert retry_execution.execution_id is not None

    db.add.assert_called_once_with(retry_execution)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(retry_execution)
    

def test_retry_preserves_original_failed_execution():
    from unittest.mock import MagicMock

    from backend.services.agent_execution_service import (
        create_agent_execution,
        fail_agent_execution,
    )

    db = MagicMock()

    # Create the first execution.
    first_execution = create_agent_execution(
        db=db,
        experiment_id="experiment-123",
        agent_name="FeatureAgent",
        attempt_number=1,
    )

    # Simulate the first attempt failing.
    first_execution.status = "failed"
    first_execution.error_message = "Temporary test failure"

    # Create a new execution for the retry.
    second_execution = create_agent_execution(
        db=db,
        experiment_id="experiment-123",
        agent_name="FeatureAgent",
        attempt_number=2,
    )

    assert first_execution.execution_id != second_execution.execution_id
    assert first_execution.attempt_number == 1
    assert first_execution.status == "failed"
    assert first_execution.error_message == "Temporary test failure"

    assert second_execution.attempt_number == 2
    assert second_execution.status == "running"

