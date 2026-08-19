from src.frame_simulator import FrameSimulator
from src.telemetry_simulator import TelemetrySimulator

from src.context.context_manager import ContextManager
from src.context.vehicle_tracker import VehicleTracker

from src.vision.vlm_analyzer import VLMAnalyzer

from src.database.db import Database
from src.database.repository import FrameRepository

from src.agent.security_agent import SecurityAnalystAgent


# =============================================================
# PRINT HELPERS
# =============================================================

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


# =============================================================
# MAIN
# =============================================================

def main():

    # =========================================================
    # INITIALIZE COMPONENTS
    # =========================================================

    print("=" * 60)
    print("DRONE SECURITY ANALYST")
    print("=" * 60)

    print()
    print("Initializing system...")

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

    # Vehicle history reasoning
    vehicle_tracker = VehicleTracker()

    # Security Analyst Agent
    security_agent = SecurityAnalystAgent()

    # Store generated security alerts
    generated_alerts = []

    print("✓ Frame simulator initialized")
    print("✓ Telemetry simulator initialized")
    print("✓ VLM analyzer initialized")
    print("✓ Database initialized")
    print("✓ Context manager initialized")
    print("✓ Vehicle tracker initialized")
    print("✓ Security analyst agent initialized")

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

    print()
    print(
        f"Frames loaded: {len(frames)}"
    )

    print(
        f"Telemetry records loaded: "
        f"{len(telemetry)}"
    )

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

            ai_result = (
                vlm_analyzer.analyze_description(
                    description=frame["description"],
                    timestamp=frame["timestamp"],
                    location=matching_telemetry["location"]
                )
            )

        except Exception as exc:

            print()
            print("❌ VLM analysis failed")

            print(
                f"Error: {exc}"
            )

            continue

        # -----------------------------------------------------
        # VALIDATE VLM OUTPUT
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
        # STORE FRAME IN DATABASE
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

        # =====================================================
        # TEMPORAL CONTEXT ANALYSIS
        # =====================================================

        temporal_events = (
            context_manager.process_observation(
                ai_result
            )
        )

        # =====================================================
        # VEHICLE HISTORY ANALYSIS
        # =====================================================

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
            # STORE SECURITY ALERT
            # -------------------------------------------------

            alert = {
                "alert_type": "PERSON_LOITERING",
                "severity": "HIGH",
                "location": event.get(
                    "location",
                    "unknown"
                ),
                "first_seen": event.get(
                    "first_seen"
                ),
                "last_seen": event.get(
                    "last_seen"
                ),
                "message": (
                    f"Person loitering at "
                    f"{event.get('location', 'unknown')} "
                    f"for "
                    f"{event.get('duration_seconds', 0)} "
                    f"seconds."
                )
            }

            generated_alerts.append(
                alert
            )

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
            # STORE SECURITY ALERT
            # -------------------------------------------------

            alert = {
                "alert_type": "REPEATED_VEHICLE",
                "severity": "MEDIUM",
                "location": event.get(
                    "location",
                    "unknown"
                ),
                "first_seen": event.get(
                    "first_seen"
                ),
                "last_seen": event.get(
                    "last_seen"
                ),
                "message": event.get(
                    "message",
                    ""
                )
            }

            generated_alerts.append(
                alert
            )

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
            f"Total indexed frames: "
            f"{total_frames}"
        )

    except AttributeError:

        print(
            f"Total indexed frames: "
            f"{len(frames)}"
        )

    # =========================================================
    # ACTIVE CONTEXTS
    # =========================================================

    print()
    print("=" * 60)
    print("ACTIVE CONTEXTS")
    print("=" * 60)

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
            "Active context information "
            "not available."
        )

    # =========================================================
    # VEHICLE EVENTS
    # =========================================================

    print()
    print("=" * 60)
    print("VEHICLE EVENTS")
    print("=" * 60)

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
    # VEHICLE HISTORY SUMMARY
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
            f"Entries: {entry_count}"
        )

        print(
            f"Exits: {exit_count}"
        )

        if entry_count >= 2:

            print(
                "⚠️ Repeated vehicle detected"
            )

        else:

            print(
                "✓ No repeated entry detected"
            )

    # =========================================================
    # SECURITY ALERT SUMMARY
    # =========================================================

    print()
    print("=" * 60)
    print("SECURITY ALERT SUMMARY")
    print("=" * 60)

    if not generated_alerts:

        print(
            "✓ No security alerts generated."
        )

    else:

        print(
            f"Total alerts: "
            f"{len(generated_alerts)}"
        )

        for alert in generated_alerts:

            print()
            print(
                f"[{alert['severity']}] "
                f"{alert['alert_type']}"
            )

            print(
                f"Location: "
                f"{alert['location']}"
            )

            print(
                f"Time: "
                f"{alert['first_seen']} - "
                f"{alert['last_seen']}"
            )

            print(
                f"Message: "
                f"{alert['message']}"
            )

    # =========================================================
    # SECURITY ANALYST AGENT
    # =========================================================

    print()
    print("=" * 60)
    print("SECURITY ANALYST AGENT")
    print("=" * 60)

    # ---------------------------------------------------------
    # Build agent context
    # ---------------------------------------------------------

    agent_context = (
        security_agent.build_context(
            vehicle_tracker=vehicle_tracker,
            alerts=generated_alerts
        )
    )

    print()
    print(
        "The video has been analyzed."
    )

    print(
        "You can now ask questions about "
        "the security events."
    )

    print()
    print("Examples:")
    print(
        "  - Was the blue Ford F150 seen more than once?"
    )
    print(
        "  - What vehicles entered the property?"
    )
    print(
        "  - Was there any security alert?"
    )
    print(
        "  - What happened at the main gate?"
    )
    print(
        "  - How many times did the Ford enter?"
    )
    print()
    print(
        "Type 'exit' to finish."
    )
    print()

    # =========================================================
    # INTERACTIVE AGENT LOOP
    # =========================================================

    while True:

        try:

            question = input(
                "Security Analyst > "
            ).strip()

        except (KeyboardInterrupt, EOFError):

            print()
            print(
                "Exiting Security Analyst."
            )

            break

        if question.lower() == "exit":

            print()
            print(
                "Security Analyst session ended."
            )

            break

        if not question:

            continue

        try:

            answer = security_agent.ask(
                question=question,
                context=agent_context
            )

            print()
            print(
                f"Agent > {answer}"
            )

            print()

        except Exception as exc:

            print()
            print(
                f"❌ Agent error: {exc}"
            )

            print()

    # =========================================================
    # END
    # =========================================================

    print()
    print("=" * 60)
    print("END OF ANALYSIS")
    print("=" * 60)


# =============================================================
# ENTRY POINT
# =============================================================

if __name__ == "__main__":
    main()