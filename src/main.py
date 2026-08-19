from src.frame_simulator import FrameSimulator
from src.telemetry_simulator import TelemetrySimulator

from src.context.context_manager import ContextManager
from src.context.vehicle_tracker import VehicleTracker

from src.vision.vlm_analyzer import VLMAnalyzer

from src.database.db import Database
from src.database.repository import FrameRepository


def print_separator(char="-", length=60):
    print(char * length)


def print_loitering_event(event):
    print()
    print("🚨 TEMPORAL EVENT DETECTED")
    print("=" * 60)

    print(
        f"Event Type: "
        f"{event.get('event_type', 'unknown')}"
    )

    print(
        f"Object Type: "
        f"{event.get('object_type', 'unknown')}"
    )

    print(
        f"Location: "
        f"{event.get('location', 'unknown')}"
    )

    print(
        f"First Seen: "
        f"{event.get('first_seen', 'unknown')}"
    )

    print(
        f"Last Seen: "
        f"{event.get('last_seen', 'unknown')}"
    )

    print(
        f"Duration: "
        f"{event.get('duration_seconds', 0)} seconds"
    )

    print(
        f"Frames Observed: "
        f"{event.get('frame_count', 0)}"
    )

    print("=" * 60)


def print_loitering_alert(event):
    print()
    print("🚨 SECURITY ALERT")
    print("=" * 60)

    print("Alert Type: PERSON_LOITERING")
    print("Severity: HIGH")

    print(
        f"Location: "
        f"{event.get('location', 'unknown')}"
    )

    print(
        f"Message: "
        f"Person loitering at "
        f"{event.get('location', 'unknown')} "
        f"for "
        f"{event.get('duration_seconds', 0)} seconds."
    )

    print(
        f"First Seen: "
        f"{event.get('first_seen', 'unknown')}"
    )

    print(
        f"Last Seen: "
        f"{event.get('last_seen', 'unknown')}"
    )

    print("=" * 60)


def print_repeated_vehicle_event(event):
    print()
    print("🚗 REPEATED VEHICLE EVENT")
    print("=" * 60)

    vehicle_name = (
        f"{event.get('color', 'unknown')} "
        f"{event.get('make', 'unknown')} "
        f"{event.get('model', 'unknown')}"
    )

    print(
        f"Vehicle: "
        f"{vehicle_name}"
    )

    print(
        f"Location: "
        f"{event.get('location', 'unknown')}"
    )

    print(
        f"First Entry: "
        f"{event.get('first_seen', 'unknown')}"
    )

    print(
        f"Latest Entry: "
        f"{event.get('last_seen', 'unknown')}"
    )

    print(
        f"Entry Count: "
        f"{event.get('entry_count', 0)}"
    )

    print(
        f"Message: "
        f"{event.get('message', '')}"
    )

    print("=" * 60)


def print_repeated_vehicle_alert(event):
    print()
    print("🚨 SECURITY ALERT")
    print("=" * 60)

    print("Alert Type: REPEATED_VEHICLE")
    print("Severity: MEDIUM")

    print(
        f"Location: "
        f"{event.get('location', 'unknown')}"
    )

    vehicle_name = (
        f"{event.get('color', 'unknown')} "
        f"{event.get('make', 'unknown')} "
        f"{event.get('model', 'unknown')}"
    )

    print(
        f"Message: "
        f"{vehicle_name} "
        f"observed entering the property "
        f"{event.get('entry_count', 0)} times."
    )

    print(
        f"First Entry: "
        f"{event.get('first_seen', 'unknown')}"
    )

    print(
        f"Latest Entry: "
        f"{event.get('last_seen', 'unknown')}"
    )

    print("=" * 60)


def main():

    # =========================================================
    # INITIALIZE COMPONENTS
    # =========================================================

    frame_simulator = FrameSimulator()

    telemetry_simulator = TelemetrySimulator()

    vlm_analyzer = VLMAnalyzer()

    database = Database()

    database.initialize()

    repository = FrameRepository(
        database
    )

    # Temporal reasoning
    context_manager = ContextManager(
        loitering_threshold_seconds=5
    )

    # Historical vehicle reasoning
    vehicle_tracker = VehicleTracker()

    # =========================================================
    # LOAD SIMULATED DATA
    # =========================================================

    frames = frame_simulator.get_frames()

    telemetry = telemetry_simulator.get_telemetry()

    # Match telemetry using timestamp
    telemetry_by_time = {
        item["timestamp"]: item
        for item in telemetry
    }

    # =========================================================
    # HEADER
    # =========================================================

    print("=" * 60)
    print("DRONE SECURITY ANALYST")
    print("=" * 60)

    print()

    # =========================================================
    # PROCESS EVERY FRAME
    # =========================================================

    for frame in frames:

        print_separator()

        print(
            f"Processing Frame: "
            f"{frame['frame_id']}"
        )

        print(
            f"Timestamp: "
            f"{frame['timestamp']}"
        )

        print(
            f"Description: "
            f"{frame['description']}"
        )

        # -----------------------------------------------------
        # FIND TELEMETRY
        # -----------------------------------------------------

        matching_telemetry = telemetry_by_time.get(
            frame["timestamp"]
        )

        if matching_telemetry is None:

            print(
                f"WARNING: No telemetry found "
                f"for {frame['timestamp']}"
            )

            continue

        print(
            f"Location: "
            f"{matching_telemetry['location']}"
        )

        # -----------------------------------------------------
        # VLM ANALYSIS
        # -----------------------------------------------------

        try:

            ai_result = vlm_analyzer.analyze_description(
                description=frame["description"],
                timestamp=frame["timestamp"],
                location=matching_telemetry["location"]
            )

        except Exception as exc:

            print()
            print(
                "❌ VLM analysis failed"
            )

            print(
                f"Error: {exc}"
            )

            continue

        # -----------------------------------------------------
        # VALIDATE AI OUTPUT
        # -----------------------------------------------------

        if not vlm_analyzer.validate_result(
            ai_result
        ):

            print(
                f"❌ Invalid AI result "
                f"for frame {frame['frame_id']}"
            )

            continue

        print(
            "✓ VLM analysis successful"
        )

        # -----------------------------------------------------
        # STORE FRAME + ANALYSIS
        # -----------------------------------------------------

        try:

            repository.save_observation(
                frame=frame,
                telemetry=matching_telemetry,
                analysis=ai_result
            )

            print(
                "✓ Frame indexed successfully"
            )

        except Exception as exc:

            print(
                f"❌ Database error: {exc}"
            )

            continue

        # -----------------------------------------------------
        # TEMPORAL CONTEXT ANALYSIS
        # -----------------------------------------------------

        temporal_events = (
            context_manager.process_observation(
                ai_result
            )
        )

        # -----------------------------------------------------
        # VEHICLE HISTORY ANALYSIS
        # -----------------------------------------------------

        vehicle_events = (
            vehicle_tracker.process_observation(
                ai_result
            )
        )

        # =====================================================
        # TEMPORAL EVENTS
        # =====================================================

        for event in temporal_events:

            print_loitering_event(
                event
            )

            # -------------------------------------------------
            # SECURITY ALERT
            # -------------------------------------------------

            print_loitering_alert(
                event
            )

        # =====================================================
        # REPEATED VEHICLE EVENTS
        # =====================================================

        for event in vehicle_events:

            print_repeated_vehicle_event(
                event
            )

            # -------------------------------------------------
            # SECURITY ALERT
            # -------------------------------------------------

            print_repeated_vehicle_alert(
                event
            )

    # =========================================================
    # PROCESSING COMPLETE
    # =========================================================

    print()
    print("=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)

    # =========================================================
    # DATABASE SUMMARY
    # =========================================================

    try:

        total_frames = repository.count_frames()

        print(
            f"\nTotal indexed frames: "
            f"{total_frames}"
        )

    except Exception:

        # Fallback if count_frames()
        # doesn't exist in repository yet.
        print(
            f"\nTotal processed frames: "
            f"{len(frames)}"
        )

    # =========================================================
    # ACTIVE CONTEXTS
    # =========================================================

    try:

        active_contexts = (
            context_manager.get_active_contexts()
        )

        print(
            f"Active contexts: "
            f"{len(active_contexts)}"
        )

        for context in active_contexts:

            print()

            print(
                f"- "
                f"{context.get('object_type', 'unknown')} "
                f"at "
                f"{context.get('location', 'unknown')}"
            )

            print(
                f"  First seen: "
                f"{context.get('first_seen', 'unknown')}"
            )

            print(
                f"  Last seen: "
                f"{context.get('last_seen', 'unknown')}"
            )

            print(
                f"  Frames: "
                f"{context.get('frame_count', 0)}"
            )

    except AttributeError:

        print(
            "\nActive context information "
            "not available."
        )

    # =========================================================
    # VEHICLE EVENTS
    # =========================================================

    print()
    print("=" * 60)
    print("VEHICLE EVENTS")
    print("=" * 60)

    try:

        vehicle_events = (
            vehicle_tracker.get_all_events()
        )

        if not vehicle_events:

            print(
                "No vehicle events found."
            )

        else:

            for event in vehicle_events:

                print(
                    f"{event['timestamp']} | "
                    f"{event['location']} | "
                    f"{event['vehicle']} | "
                    f"{event['activity']}"
                )

    except AttributeError:

        # Build the vehicle event list
        # directly from the tracker state.

        found_vehicle = False

        for (
            vehicle_key,
            observations
        ) in vehicle_tracker.vehicles.items():

            color, make, model = vehicle_key

            for observation in observations:

                found_vehicle = True

                vehicle_name = (
                    f"{color} "
                    f"{make} "
                    f"{model}"
                )

                print(
                    f"{observation['timestamp']} | "
                    f"{observation['location']} | "
                    f"{vehicle_name} | "
                    f"{observation['activity']}"
                )

        if not found_vehicle:

            print(
                "No vehicle events found."
            )

    # =========================================================
    # FORD VEHICLE EVENTS
    # =========================================================

    print()
    print("=" * 60)
    print("FORD VEHICLE EVENTS")
    print("=" * 60)

    found_ford = False

    for (
        vehicle_key,
        observations
    ) in vehicle_tracker.vehicles.items():

        color, make, model = vehicle_key

        if not make:
            continue

        if make.lower() != "ford":
            continue

        for observation in observations:

            found_ford = True

            vehicle_name = (
                f"{color} "
                f"{make} "
                f"{model}"
            )

            print(
                f"{observation['timestamp']} | "
                f"{observation['location']} | "
                f"{vehicle_name} | "
                f"{observation['activity']}"
            )

    if not found_ford:

        print(
            "No Ford vehicle events found."
        )

    # =========================================================
    # VEHICLE SUMMARY
    # =========================================================

    print()
    print("=" * 60)
    print("VEHICLE HISTORY SUMMARY")
    print("=" * 60)

    for (
        vehicle_key,
        observations
    ) in vehicle_tracker.vehicles.items():

        color, make, model = vehicle_key

        vehicle_name = (
            f"{color} "
            f"{make} "
            f"{model}"
        )

        entry_count = sum(
            1
            for item in observations
            if item["activity"] == "entering"
        )

        exit_count = sum(
            1
            for item in observations
            if item["activity"] == "exiting"
        )

        print()
        print(
            f"Vehicle: {vehicle_name}"
        )

        print(
            f"Location: "
            f"{observations[-1]['location']}"
        )

        print(
            f"Entries: "
            f"{entry_count}"
        )

        print(
            f"Exits: "
            f"{exit_count}"
        )

        if entry_count >= 2:

            print(
                "⚠️ Repeated vehicle detected"
            )

        else:

            print(
                "✓ No repeated entry detected"
            )

    print()
    print("=" * 60)
    print("END OF ANALYSIS")
    print("=" * 60)


if __name__ == "__main__":
    main()