import json
from pathlib import Path
import pytest
import jsonschema

CONTRACTS_DIR = Path(__file__).resolve().parent.parent / "docs" / "contracts"

CONTRACT_NAMES = ["forecast", "action", "explanation"]


@pytest.mark.parametrize("contract_name", CONTRACT_NAMES)
def test_contract_example_matches_schema(contract_name: str) -> None:
    schema_path = CONTRACTS_DIR / f"{contract_name}.schema.json"
    example_path = CONTRACTS_DIR / f"{contract_name}.example.json"

    assert schema_path.exists(), f"Schema file not found: {schema_path}"
    assert example_path.exists(), f"Example file not found: {example_path}"

    with open(schema_path, "r", encoding="utf-8") as sf:
        schema = json.load(sf)

    with open(example_path, "r", encoding="utf-8") as ef:
        example = json.load(ef)

    # Validate example conforms strictly to schema
    jsonschema.validate(instance=example, schema=schema)
