"""DeepEval checks for the final answer produced by the LangChain agent."""

from __future__ import annotations

import os

import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from agent import run_agent


pytestmark = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY is required for the agent and DeepEval judge.",
)


@pytest.mark.parametrize(
    ("question", "expected_answer"),
    [
        ("What is 25 * 48?", "1200"),
        ("What is 100 / 4?", "25"),
        ("What is 17 + 35?", "52"),
    ],
)
def test_math_agent(question: str, expected_answer: str) -> None:
    actual_answer = run_agent(question)
    test_case = LLMTestCase(
        input=question,
        actual_output=actual_answer,
        expected_output=expected_answer,
    )

    relevancy = AnswerRelevancyMetric(threshold=0.8)
    correctness = GEval(
        name="Mathematical correctness",
        criteria=(
            "Determine whether the actual output correctly answers the input. "
            "The expected output gives the required mathematical result."
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        threshold=0.8,
    )

    assert_test(test_case, [relevancy, correctness])
