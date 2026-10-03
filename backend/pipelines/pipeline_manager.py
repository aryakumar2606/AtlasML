import time
from pathlib import Path

from sqlalchemy.orm import Session

from backend.logger import logger
from backend.models.pipeline_state import PipelineState

from backend.services.experiment_service import (
    update_experiment_status,
)

from backend.services.agent_execution_service import (
    create_agent_execution,
    complete_agent_execution,
    fail_agent_execution,
    get_next_attempt_number,
)

from backend.agents.dataset_agent import DatasetAgent
from backend.agents.feature_agent import FeatureAgent

from backend.services.mlflow_service import (
    start_mlflow_run,
    log_pipeline_info,
    log_metric,
    log_agent_metadata,
    end_mlflow_run,
)


class PipelineManager:

    def __init__(self):

        self.agents = [
            DatasetAgent(),
            FeatureAgent(),
        ]

    def run_pipeline(
        self,
        state: PipelineState,
        db: Session,
    ) -> PipelineState:

        logger.info(
            "========== PIPELINE STARTED =========="
        )

        pipeline_start = time.time()

        dataset_name = Path(
            state.dataset_path
        ).name

        start_mlflow_run(
            experiment_name="AtlasML",
            run_name=state.experiment_id,
        )

        log_pipeline_info(
            experiment_id=state.experiment_id,
            dataset_name=dataset_name,
            rows=state.summary.get("rows", 0),
            columns=state.summary.get("columns", 0),
        )

        try:

            update_experiment_status(
                db=db,
                experiment_id=state.experiment_id,
                status="running",
                current_agent="DatasetAgent",
            )

            for agent in self.agents:

                agent_name = agent.__class__.__name__

                logger.info(
                    f"Running {agent_name}"
                )

                state.current_agent = agent_name

                attempt_number = get_next_attempt_number(
                    db=db,
                    experiment_id=state.experiment_id,
                    agent_name=agent_name,
                )

                execution = create_agent_execution(
                    db=db,
                    experiment_id=state.experiment_id,
                    agent_name=agent_name,
                    attempt_number=attempt_number,
                )

                agent_start = time.time()

                try:

                    state = agent.run(state)

                    agent_execution_time = round(
                        time.time() - agent_start,
                        2,
                    )

                    complete_agent_execution(
                        db=db,
                        execution_id=execution.execution_id,
                        execution_time=agent_execution_time,
                    )
                    
                    log_metric(
                      f"{agent_name}_execution_time",
                      agent_execution_time,
                    )

                    logger.info(
                        f"{agent_name} completed in "
                        f"{agent_execution_time} seconds"
                    )

                except Exception as agent_error:

                    agent_execution_time = round(
                        time.time() - agent_start,
                        2,
                    )

                    fail_agent_execution(
                        db=db,
                        execution_id=execution.execution_id,
                        error_message=str(agent_error),
                        execution_time=agent_execution_time,
                    )

                    logger.exception(
                        f"{agent_name} failed"
                    )

                    raise

            pipeline_execution_time = round(
                time.time() - pipeline_start,
                2,
            )

            log_metric(
                "pipeline_execution_time",
                pipeline_execution_time,
            )

            logger.info(
                f"Pipeline completed in "
                f"{pipeline_execution_time} seconds"
            )

            update_experiment_status(
                db=db,
                experiment_id=state.experiment_id,
                status="completed",
                current_agent="Completed",
                execution_time=pipeline_execution_time,
                pipeline_result=state.summary,
            )

            end_mlflow_run()

            return state

        except Exception as e:

            logger.exception(
                "Pipeline Failed"
            )

            update_experiment_status(
                db=db,
                experiment_id=state.experiment_id,
                status="failed",
                current_agent=state.current_agent,
                error_message=str(e),
            )

            end_mlflow_run()

            raise