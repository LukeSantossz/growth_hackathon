import argparse
import asyncio
import sys
from datetime import date
from pathlib import Path
from typing import Any
from uuid import uuid4

from langsmith import Client

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from agent import run_turn
from evaluation.env_bootstrap import ensure_langsmith_api_key, load_env
from evaluation.scenarios import DATASET_NAME
from evaluation.sync_dataset import sync_dataset

load_env()


def run_full_interaction(inputs: dict[str, Any]) -> dict[str, Any]:
    config = {"configurable": {"thread_id": f"eval-{uuid4().hex}"}}
    return asyncio.run(run_turn(inputs, config=config))


def _outputs(run: Any) -> dict[str, Any]:
    outputs = getattr(run, "outputs", None)
    return outputs if isinstance(outputs, dict) else {}


def _expected(example: Any) -> dict[str, Any]:
    outputs = getattr(example, "outputs", None)
    return outputs if isinstance(outputs, dict) else {}


def action_match(run: Any, example: Any) -> dict[str, Any]:
    predicted = str(_outputs(run).get("action", ""))
    expected = str(_expected(example).get("expected_action", ""))
    score = float(predicted == expected)
    return {
        "key": "action_match",
        "score": score,
        "comment": f"predicted={predicted}, expected={expected}",
    }


def status_match(run: Any, example: Any) -> dict[str, Any]:
    predicted = str(_outputs(run).get("contact_status", ""))
    expected = str(_expected(example).get("expected_contact_status", ""))
    score = float(predicted == expected)
    return {
        "key": "status_match",
        "score": score,
        "comment": f"predicted={predicted}, expected={expected}",
    }


def response_present(run: Any, _: Any) -> dict[str, Any]:
    response_text = str(_outputs(run).get("response_text", "")).strip()
    score = float(bool(response_text))
    return {
        "key": "response_present",
        "score": score,
        "comment": "response generated" if score else "empty response",
    }


def structured_flags_match(run: Any, example: Any) -> dict[str, Any]:
    expected_flags = _expected(example).get("expected_flags", {})
    if not isinstance(expected_flags, dict) or not expected_flags:
        return {
            "key": "structured_flags_match",
            "score": 1.0,
            "comment": "no expected flags for this scenario",
        }

    analysis = _outputs(run).get("intent_analysis", {})
    if not isinstance(analysis, dict):
        analysis = {}

    mismatches: list[str] = []
    for flag_name, flag_value in expected_flags.items():
        predicted = bool(analysis.get(flag_name, False))
        if predicted != bool(flag_value):
            mismatches.append(
                f"{flag_name}: predicted={predicted} expected={bool(flag_value)}"
            )

    score = 1.0 if not mismatches else 0.0
    comment = "all flags matched" if not mismatches else "; ".join(mismatches)
    return {
        "key": "structured_flags_match",
        "score": score,
        "comment": comment,
    }


def scenario_success_rate(runs: list[Any], examples: list[Any]) -> dict[str, Any]:
    total = len(runs)
    if total == 0:
        return {"key": "scenario_success_rate", "score": 0.0, "comment": "no runs"}

    passed = 0
    for run, example in zip(runs, examples):
        out = _outputs(run)
        exp = _expected(example)
        action_ok = str(out.get("action", "")) == str(exp.get("expected_action", ""))
        status_ok = str(out.get("contact_status", "")) == str(exp.get("expected_contact_status", ""))
        response_ok = bool(str(out.get("response_text", "")).strip())

        expected_flags = exp.get("expected_flags", {})
        flags_ok = True
        if isinstance(expected_flags, dict) and expected_flags:
            analysis = out.get("intent_analysis", {})
            if not isinstance(analysis, dict):
                analysis = {}
            flags_ok = all(bool(analysis.get(key, False)) == bool(value) for key, value in expected_flags.items())

        if action_ok and status_ok and response_ok and flags_ok:
            passed += 1

    score = passed / total
    return {
        "key": "scenario_success_rate",
        "score": score,
        "comment": f"{passed}/{total} scenarios passed all checks",
    }


def main():
    parser = argparse.ArgumentParser(description="Run LangSmith experiment for the SDR full-interaction agent")
    parser.add_argument("--dataset-name", default=DATASET_NAME)
    parser.add_argument("--experiment-prefix", default="sdr-full-interaction")
    parser.add_argument("--max-concurrency", type=int, default=1)
    parser.add_argument("--skip-dataset-sync", action="store_true")
    args = parser.parse_args()

    ensure_langsmith_api_key()
    client = Client()

    dataset_name = args.dataset_name
    if not args.skip_dataset_sync:
        dataset_name = sync_dataset(client, dataset_name=dataset_name, reset_examples=True)

    results = client.evaluate(
        run_full_interaction,
        data=dataset_name,
        evaluators=[
            action_match,
            status_match,
            response_present,
            structured_flags_match,
        ],
        summary_evaluators=[scenario_success_rate],
        experiment_prefix=args.experiment_prefix,
        description="Avaliação de fluxo completo do agente SDR por status e intenção",
        max_concurrency=args.max_concurrency,
        metadata={
            "dataset": dataset_name,
            "date": date.today().isoformat(),
            "scope": "full_interaction",
        },
    )

    experiment_name = getattr(results, "experiment_name", None)
    if experiment_name:
        print(f"Experiment completed: {experiment_name}")
    else:
        print("Experiment completed")


if __name__ == "__main__":
    main()
