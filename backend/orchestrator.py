
from uuid import uuid4

from .schemas import TestRequest, TestReport
from .llm_service import generate_test_plan


def create_test_run(request: TestRequest) -> dict:
    """
    Create a test run and generate its plan.
    Browser execution will be connected later.
    """
    run_id = str(uuid4())

    plan = generate_test_plan(request)

    report = TestReport(
        run_id=run_id,
        status="queued",
        objective=request.objective,
        steps=[],
        issues=[
            "Test plan generated. Browser execution is not connected yet."
        ],
    )

    return {
        "run_id": run_id,
        "status": "queued",
        "plan": plan,
        "report": report,
    }
