
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from .schemas import TestPlan, TestRequest


# Load environment variables from the project root
load_dotenv()


def generate_test_plan(request: TestRequest) -> TestPlan:
    """Generate a structured test plan using Gemini AI."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Check your root .env file."
        )

    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are an expert web application QA tester.

    Website URL: {request.url}
    Testing objective: {request.objective}

    Create a practical test plan containing 2 to 10 steps.

    Rules:
    - Use only these actions: navigate, click, fill, verify.
    - Every step must have an action, target, and expected result.
    - The first step must navigate to the supplied website URL.
    - Use clear targets, such as "Login button" or "Email input field".
    - Do not invent login credentials.
    - Do not claim that tests have already been executed.
    - Generate a plan only. Do not execute browser actions.
    """

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TestPlan,
            temperature=0.2,
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty test plan.")

    return TestPlan.model_validate_json(response.text)
