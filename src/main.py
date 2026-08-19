from src.frame_simulator import FrameSimulator
from src.telemetry_simulator import TelemetrySimulator

def combine_frame_with_telemetry(frame, telemetry):
    return {
        "frame_id": frame["frame_id"],
        "timestamp": frame["timestamp"],
        "description": frame["description"],
        "location": telemetry["location"],
        "latitude": telemetry["latitude"],
        "longitude": telemetry["longitude"],
        "altitude": telemetry["altitude"]
    }


def main():
    frame_simulator = FrameSimulator()
    telemetry_simulator = TelemetrySimulator()

    frames = frame_simulator.get_frames()
    telemetry = telemetry_simulator.get_telemetry()

    print("=" * 60)
    print("DRONE SECURITY ANALYST - SIMULATION")
    print("=" * 60)

    print("\n--- COMBINED DRONE OBSERVATIONS ---")

    telemetry_by_time = {
        item["timestamp"]: item
        for item in telemetry
    }

    for frame in frames:
        matching_telemetry = telemetry_by_time.get(
            frame["timestamp"]
        )

        if matching_telemetry is None:
            print(
                f"Warning: No telemetry found for "
                f"{frame['timestamp']}"
            )
            continue

        observation = combine_frame_with_telemetry(
            frame,
            matching_telemetry
        )

        print(
            f"\nFrame {observation['frame_id']}"
        )

        print(
            f"Time: {observation['timestamp']}"
        )

        print(
            f"Location: {observation['location']}"
        )

        print(
            f"Altitude: {observation['altitude']}m"
        )

        print(
            f"Description: {observation['description']}"
        )


if __name__ == "__main__":
    main()