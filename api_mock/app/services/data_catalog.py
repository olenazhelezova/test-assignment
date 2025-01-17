import json
from pathlib import Path

DATA_FILE_PATH = Path(__file__).parent.parent / "mock_data" / "mock_data.json"

def load_mock_data():
    """
    Load mock data from the JSON file.
    """
    with open(DATA_FILE_PATH, "r") as file:
        return json.load(file)


def get_resource_metadata(type) -> list[dict]:
    """
    Get resource metadata filtered by type.
    """
    data = load_mock_data()
    return list(filter(lambda e: "type" in e and e["type"] == type, data))
