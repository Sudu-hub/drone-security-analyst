from src.context.context_manager import ContextManager


def test_person_loitering():

    manager = ContextManager(
        loitering_threshold_seconds=5
    )

    observation_1 = {
        "timestamp": "00:00",
        "location": "main_gate",
        "objects": [
            {
                "type": "person",
                "color": None,
                "make": None,
                "model": None,
                "activity": "standing",
                "confidence": 0.95
            }
        ]
    }

    observation_2 = {
        "timestamp": "00:03",
        "location": "main_gate",
        "objects": [
            {
                "type": "person",
                "color": None,
                "make": None,
                "model": None,
                "activity": "standing",
                "confidence": 0.96
            }
        ]
    }

    observation_3 = {
        "timestamp": "00:06",
        "location": "main_gate",
        "objects": [
            {
                "type": "person",
                "color": None,
                "make": None,
                "model": None,
                "activity": "standing",
                "confidence": 0.97
            }
        ]
    }

    manager.process_observation(
        observation_1
    )

    manager.process_observation(
        observation_2
    )

    events = manager.process_observation(
        observation_3
    )

    assert len(events) >= 1

    event = events[0]

    assert event["event_type"] == "loitering"

    assert event["location"] == "main_gate"

    assert event["duration_seconds"] == 6