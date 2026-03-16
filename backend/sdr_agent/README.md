# Backend (SDR Agent)

## Setup

```bash
cd backend
uv sync
```

Configure environment variables (`.env`):

- `GROQ_API_KEY`
- `LANGSMITH_API_KEY`
- `LANGSMITH_TRACING=true`
- `LANGSMITH_PROJECT` (optional)

Evaluation scripts auto-load `.env` from both:
- `backend/.env`
- workspace root (`../.env`)

## What was added

- Status-based routing (`new`, `contacted`, `replied`) for full interaction testing.
- Structured intent extraction (`intent_analysis`) with JSON variables from prompt templates in Python.
- Graceful discard flow with dedicated message node.
- LangSmith dataset + experiment scripts covering six scenarios:
	- first interaction
	- follow-up
	- follow-up for nonsense question
	- follow-up for business explanation
	- discard lead with graceful message
	- schedule meeting

## Create/Sync evaluation dataset

```bash
cd backend
uv run python evaluation/sync_dataset.py
```

Optional:

```bash
uv run python evaluation/sync_dataset.py --dataset-name sdr-agent-full-interaction --no-reset
```

## Run experiment

```bash
cd backend
uv run python evaluation/run_experiment.py
```

Optional:

```bash
uv run python evaluation/run_experiment.py \
	--dataset-name sdr-agent-full-interaction \
	--experiment-prefix sdr-full-interaction \
	--max-concurrency 1
```
