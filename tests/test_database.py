from src.database.db import Database
from src.database.repository import FrameRepository


def test_database_initialization(tmp_path):

    db_path = tmp_path / "test.db"

    database = Database(
        str(db_path)
    )

    database.initialize()

    repository = FrameRepository(
        database
    )

    frame = {
        "frame_id": 1,
        "timestamp": "00:00",
        "description": "Blue Ford F150 at gate"
    }

    telemetry = {
        "location": "main_gate",
        "altitude": 30,
        "latitude": 18.5204,
        "longitude": 73.8567
    }

    analysis = {
        "objects": [
            {
                "type": "vehicle",
                "color": "blue",
                "make": "Ford",
                "model": "F150",
                "activity": "entering",
                "confidence": 0.95
            }
        ]
    }

    repository.save_observation(
        frame,
        telemetry,
        analysis
    )

    vehicles = repository.find_by_object_type(
        "vehicle"
    )

    assert len(vehicles) == 1

    assert vehicles[0]["make"] == "Ford"

    assert vehicles[0]["model"] == "F150"