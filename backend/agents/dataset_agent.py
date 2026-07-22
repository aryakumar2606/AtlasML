from backend.models.pipeline_state import PipelineState


class DatasetAgent:

    def run(self, state: PipelineState):

        print("Dataset Agent Started")

        print(state.dataset_path)

        print(state.summary["rows"])

        state.current_agent = "completed"

        state.status = "success"

        return state