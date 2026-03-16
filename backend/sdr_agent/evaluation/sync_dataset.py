import argparse
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from langsmith import Client

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from evaluation.env_bootstrap import ensure_langsmith_api_key, load_env
from evaluation.scenarios import DATASET_DESCRIPTION, DATASET_NAME, SCENARIOS

load_env()


def _chunked(items: list[Any], size: int) -> Iterable[list[Any]]:
    for index in range(0, len(items), size):
        yield items[index : index + size]


def _dataset_examples() -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    for scenario in SCENARIOS:
        examples.append(
            {
                "inputs": scenario["inputs"],
                "outputs": scenario["expected"],
                "metadata": {
                    "scenario_id": scenario["id"],
                    "scenario_description": scenario["description"],
                },
                "split": "regression",
            }
        )
    return examples


def ensure_dataset(client: Client, dataset_name: str, description: str):
    if client.has_dataset(dataset_name=dataset_name):
        return client.read_dataset(dataset_name=dataset_name)
    return client.create_dataset(dataset_name=dataset_name, description=description)


def sync_dataset(
    client: Client,
    dataset_name: str = DATASET_NAME,
    description: str = DATASET_DESCRIPTION,
    reset_examples: bool = True,
) -> str:
    dataset = ensure_dataset(client, dataset_name=dataset_name, description=description)

    if reset_examples:
        existing_ids = [str(example.id) for example in client.list_examples(dataset_id=dataset.id)]
        for batch in _chunked(existing_ids, 100):
            client.delete_examples(batch)

    examples = _dataset_examples()
    response = client.create_examples(dataset_id=dataset.id, examples=examples)

    print(
        f"Dataset synced: {dataset.name} | Added examples: {response.count if hasattr(response, 'count') else len(examples)}"
    )
    return dataset.name


def main():
    parser = argparse.ArgumentParser(description="Create/update LangSmith dataset for SDR interaction evaluation")
    parser.add_argument("--dataset-name", default=DATASET_NAME)
    parser.add_argument("--no-reset", action="store_true", help="Do not delete existing examples before upload")
    args = parser.parse_args()

    ensure_langsmith_api_key()
    client = Client()
    sync_dataset(
        client,
        dataset_name=args.dataset_name,
        description=DATASET_DESCRIPTION,
        reset_examples=not args.no_reset,
    )


if __name__ == "__main__":
    main()
