# LangChain agent + DeepEval

A compact example of an agentic workflow that is safe to publish to GitHub:

1. A LangChain agent decides when to use a calculator tool.
2. The agent returns a final answer.
3. DeepEval judges the answer for relevance and correctness.
4. GitHub Actions runs the evaluation whenever code changes.

## Project layout

```text
.
├── agent.py                     # Calculator tool and LangChain agent
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
deepeval test run tests/test_agent_evaluation.py
```

The evaluation is skipped when `OPENAI_API_KEY` is absent. This lets the GitHub
workflow validate the project setup on public forks without exposing a key.

## Configure GitHub Actions

In the GitHub repository, open **Settings → Secrets and variables → Actions**
and add a repository secret named `OPENAI_API_KEY`. The workflow supplies that
secret only to the evaluation command.

## Push this example

```bash
git add .
git commit -m "Add LangChain and DeepEval example"
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
