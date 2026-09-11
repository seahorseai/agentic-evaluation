"""A minimal LangChain agent that can calculate basic arithmetic."""

from __future__ import annotations

import ast
import operator
import os
from typing import Any

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langfuse import get_client
from langfuse.langchain import CallbackHandler

load_dotenv()

_BINARY_OPERATORS: dict[type[ast.operator], Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}
_UNARY_OPERATORS: dict[type[ast.unaryop], Any] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _evaluate_expression(node: ast.AST) -> float | int:
    """Evaluate only numeric literals and the arithmetic operators we allow."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        left = _evaluate_expression(node.left)
        right = _evaluate_expression(node.right)
        return _BINARY_OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        return _UNARY_OPERATORS[type(node.op)](_evaluate_expression(node.operand))
    raise ValueError("Use only numbers and +, -, *, /, or **.")


@tool
def calculator(expression: str) -> str:
    """Calculate an arithmetic expression, for example `25 * 48` or `100 / 4`."""
    try:
        expression_tree = ast.parse(expression, mode="eval")
        return str(_evaluate_expression(expression_tree.body))
    except (ArithmeticError, SyntaxError, ValueError) as error:
        return f"Calculation error: {error}"


def build_agent():
    """Create a tool-using agent with a configurable OpenAI model."""
    model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"), temperature=0)
    return create_agent(
        model=model,
        tools=[calculator],
        system_prompt=(
            "You are a concise mathematical assistant. Use the calculator tool for "
            "arithmetic, then state the result clearly."
        ),
    )


def _langfuse_callback() -> CallbackHandler | None:
    """Return an observability callback only when Langfuse is configured.

    Keeping tracing optional makes the public example runnable without
    placeholder credentials while allowing GitHub Actions to send traces when
    repository secrets are configured.
    """
    if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
        return CallbackHandler()
    return None


def run_agent(question: str) -> str:
    """Run the agent, optionally trace it in Langfuse, and return final text."""
    callback = _langfuse_callback()
    config: dict[str, Any] = {
        "metadata": {
            "langfuse_tags": ["github-example", "calculator-agent"],
        }
    }
    if callback:
        config["callbacks"] = [callback]

    try:
        result = build_agent().invoke(
            {"messages": [{"role": "user", "content": question}]},
            config=config,
        )
        return str(result["messages"][-1].content)
    finally:
        # Ensure a short-lived local script or CI job exports its trace before exit.
        if callback:
            get_client().flush()


if __name__ == "__main__":
    question = "What is 25 * 48?"
    print(f"Question: {question}")
    print(f"Answer: {run_agent(question)}")
