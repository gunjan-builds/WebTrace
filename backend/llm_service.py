
from .schemas import TestPlan, TestRequest


def generate_test_plan(request: TestRequest) -> TestPlan:
    """
    Temporary mock planner.
    This does not call a real AI model yet.
    """
    return TestPlan(
        steps=[
            {
                "action": "navigate",
                "target": str(request.url),
                "expected": "The website loads successfully",
            },
            {
                "action": "verify",
                "target": "page content",
                "expected": request.objective,
            },
        ]
    )
