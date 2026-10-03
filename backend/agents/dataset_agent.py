import pandas as pd

from backend.agents.base_agent import BaseAgent
from backend.logger import logger
from backend.models.pipeline_state import PipelineState
from backend.services.mlflow_service import log_agent_metadata

from backend.services.dataset_understanding import (
    detect_identifier_columns,
    detect_target_column,
    detect_problem_type,
    detect_datetime_columns,
    detect_text_columns,
    detect_constant_columns,
    detect_high_cardinality_columns,
    generate_dataset_problems,
)


class DatasetAgent(BaseAgent):

    def run(self, state: PipelineState) -> PipelineState:

        logger.info("========== DATASET AGENT ==========")

        dataframe = pd.read_csv(state.dataset_path)
        state.cleaned_dataframe = dataframe.copy()

        identifier_columns = detect_identifier_columns(dataframe)

        target_column = detect_target_column(dataframe)

        problem_type = detect_problem_type(
            dataframe,
            target_column
        )

        datetime_columns = detect_datetime_columns(dataframe)

        text_columns = detect_text_columns(dataframe)

        constant_columns = detect_constant_columns(dataframe)

        high_cardinality_columns = (
            detect_high_cardinality_columns(dataframe)
        )

        # Make sure these exist before generating problems
        state.summary["identifier_columns"] = identifier_columns
        state.summary["target_column"] = target_column
        state.summary["problem_type"] = problem_type
        state.summary["datetime_columns"] = datetime_columns
        state.summary["text_columns"] = text_columns
        state.summary["constant_columns"] = constant_columns
        state.summary["high_cardinality_columns"] = (
            high_cardinality_columns
        )

        dataset_problems = generate_dataset_problems(
            state.summary
        )

        state.summary["dataset_problems"] = dataset_problems

        state.current_agent = "DatasetAgent"

        state.status = "running"

        state.executed_agents.append("DatasetAgent")
        
        log_agent_metadata(
    "DatasetAgent",
    {
        "target_column": target_column,
        "problem_type": problem_type,
        "identifier_columns": identifier_columns,
        "datetime_columns": datetime_columns,
        "text_columns": text_columns,
        "constant_columns": constant_columns,
        "high_cardinality_columns": high_cardinality_columns,
        "dataset_problems": dataset_problems,
    },
)


        logger.info("Dataset Agent Completed")

        return state