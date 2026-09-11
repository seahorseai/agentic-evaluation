# LangChain agent + Langfuse + DeepEval

A compact example of an agentic workflow that is safe to publish to GitHub:

1. A LangChain agent decides when to use a calculator tool.
2. A Langfuse callback records the agent, tool, and LLM activity as a trace.
3. The agent returns a final answer.
4. DeepEval judges the answer for relevance and correctness.
5. GitHub Actions runs the evaluation whenever code changes.

## Project layout

```text
.
├── agent.py                     # Calculator tool, LangChain agent, Langfuse callback
├── tests/
│   └── test_agent_evaluation.py # DeepEval test cases
├── requirements.txt
├── .env.example
└── .github/workflows/evaluate.yml
```

## Run locally

Create a virtual environment and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

Copy the example environment file and add your key. Never commit the resulting
`.env` file.

```bash
cp .env.example .env
```

Run the agent:

```bash
python agent.py
```

Run the DeepEval suite:

```bash
PYTHONPATH=. deepeval test run tests/test_agent_evaluation.py
```

The evaluation is skipped when `OPENAI_API_KEY` is absent. This lets the GitHub
workflow validate the project setup on public forks without exposing a key.

## Enable Langfuse observability

Langfuse tracing is optional. When both Langfuse keys are present, every
`run_agent()` call sends a trace containing the LangChain agent run, calculator
tool call, LLM generations, latency, token usage, and cost (when reported by
the model provider). The script flushes before it exits, which is important for
short-lived commands and CI jobs.

Create a Langfuse project, then put its values in `.env`:

```bash
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

Run `python agent.py`, open the Langfuse project, and inspect the trace tagged
`github-example` and `calculator-agent`.

## Configure GitHub Actions

In the GitHub repository, open **Settings → Secrets and variables → Actions**
and add these repository secrets:

| Secret | Required for |
| --- | --- |
| `OPENAI_API_KEY` | Agent and DeepEval evaluation |
| `LANGFUSE_PUBLIC_KEY` | Sending CI traces to Langfuse (optional) |
| `LANGFUSE_SECRET_KEY` | Sending CI traces to Langfuse (optional) |

Optionally add a `LANGFUSE_BASE_URL` repository variable for a non-EU Langfuse
cloud region or a self-hosted instance. The workflow labels traces with the
`ci` environment. It does not expose any of these secrets to pull requests
from forks.

## Push this example

```bash
git add .
git commit -m "Add LangChain, Langfuse, and DeepEval example"
git push -u origin main
```

If your default branch has a different name, replace `main` with that branch.

## What DeepEval measures here

| Metric | Question it answers |
| --- | --- |
| Answer relevancy | Does the response directly address the math question? |
| Correctness (GEval) | Does the response contain the expected mathematical result? |

The calculator validates its expression with Python's AST before evaluating it;
it does not use unrestricted `eval` on agent-generated input.
