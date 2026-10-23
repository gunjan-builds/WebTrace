
from typing import Literal
from pydantic import BaseModel, Field, HttpUrl


class TestRequest(BaseModel):
    url: HttpUrl
    objective: str = Field(min_length=5, max_length=500)


class TestStep(BaseModel):
    action: Literal["navigate", "click", "fill", "verify"]
    target: str
    expected: str
    value: str | None = None


class TestPlan(BaseModel):
    steps: list[TestStep] = Field(min_length=1, max_length=10)


class TestCreated(BaseModel):
    run_id: str
    status: Literal["queued", "running", "completed", "error"]
    message: str


class StepResult(BaseModel):
    name: str
    status: Literal["passed", "failed", "inconclusive"]
    message: str


class TestReport(BaseModel):
    run_id: str
    status: Literal["queued", "running", "completed", "error"]
    objective: str
    steps: list[StepResult] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
