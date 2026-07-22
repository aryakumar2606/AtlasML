from typing import Any

from pydantic import BaseModel


class PipelineState(BaseModel):

    dataset_path: str

    summary: dict[str, Any]

    current_agent: str

    status: str