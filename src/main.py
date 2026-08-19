from src.frame_simulator import FrameSimulator
from src.telemetry_simulator import TelemetrySimulator

from src.vision.vlm_analyzer import VLMAnalyzer

from src.database.db import Database
from src.database.repository import FrameRepository


def main():

    # -----------------------------
    # Initialize components
    # -----------------------------

    frame_simulator = FrameSimulator()

    telemetry_simulator = TelemetrySimulator()

    vlm_analyzer = VLMAnalyzer()

    database = Database()

    database.initialize()

    repository = FrameRepository(
        database
    )

    # -----------------------------
    # Load simulated data
    # -----------------------------

    frames = frame_simulator.get_frames()

    telemetry = telemetry_simulator.get_telemetry()

    telemetry_by_time = {
        item["timestamp"]: item
        for item in telemetry
    }

    print("=" * 60)
    print("DRONE SECURITY ANALYST")
    print("=" * 60)

    # -----------------------------
    # Process every frame
    # -----------------------------

    for frame in frames:

        matching_telemetry = telemetry_by_time.get(
            frame["timestamp"]
        )

        if matching_telemetry is None:

            print(
                f"WARNING: No telemetry for "
                f"{frame['timestamp']}"
            )

            continue

        # -----------------------------
        # AI perception
        # -----------------------------

        ai_result = vlm_analyzer.analyze_description(
            description=frame["description"],
            timestamp=frame["timestamp"],
            location=matching_telemetry["location"]
        )

        # -----------------------------
        # Validate AI output
        # -----------------------------

        if not vlm_analyzer.validate_result(
            ai_result
        ):

            print(
                f"Invalid AI result "
                f"for frame {frame['frame_id']}"
            )

            continue

        # -----------------------------
        # Store in database
        # -----------------------------

        repository.save_observation(
            frame=frame,
            telemetry=matching_telemetry,
            analysis=ai_result
        )

        print(
            f"✓ Frame {frame['frame_id']} "
            f"indexed successfully"
        )

    # -----------------------------
    # Query database
    # -----------------------------

    print("\n")
    print("=" * 60)
    print("ALL FRAMES")
    print("=" * 60)

    frames = repository.get_all_frames()

    for frame in frames:

        print(
            frame["frame_id"],
            frame["timestamp"],
            frame["location"]
        )

    # -----------------------------
    # Query vehicles
    # -----------------------------

    print("\n")
    print("=" * 60)
    print("VEHICLE EVENTS")
    print("=" * 60)

    vehicles = repository.find_by_object_type(
        "vehicle"
    )

    for vehicle in vehicles:

        print(
            vehicle
        )

    # -----------------------------
    # Query Ford vehicles
    # -----------------------------

    print("\n")
    print("=" * 60)
    print("FORD EVENTS")
    print("=" * 60)

    ford_events = repository.find_by_make(
        "Ford"
    )

    for event in ford_events:

        print(
            event
        )


if __name__ == "__main__":
    main()