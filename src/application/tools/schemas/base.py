"""base schemas for tools."""

from pydantic import BaseModel, Field


class ToolResponse(BaseModel):
    """base tool response model."""

    status: str = Field(default="success", description="response status")

