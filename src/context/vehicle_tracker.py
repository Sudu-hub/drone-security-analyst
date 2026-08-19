from collections import defaultdict


class VehicleTracker:
    """
    Tracks vehicles across multiple observations.

    A vehicle is identified using:
        color + make + model

    Example:
        blue + Ford + F150
    """

    def __init__(self):

        self.vehicles = defaultdict(list)

    # =========================================================
    # PROCESS VEHICLE
    # =========================================================

    def process_observation(self, observation: dict):

        events = []

        objects = observation.get(
            "objects",
            []
        )

        for obj in objects:

            if obj.get("type") != "vehicle":
                continue

            color = obj.get("color")
            make = obj.get("make")
            model = obj.get("model")

            # We need enough identity information
            # to recognize the same vehicle.

            if not make or not model:
                continue

            vehicle_key = (
                color,
                make,
                model
            )

            vehicle_record = {
                "timestamp": observation["timestamp"],
                "location": observation["location"],
                "activity": obj.get(
                    "activity",
                    "unknown"
                ),
                "confidence": obj.get(
                    "confidence",
                    0.0
                )
            }

            self.vehicles[
                vehicle_key
            ].append(
                vehicle_record
            )

            # -------------------------------------------------
            # Count ENTER events
            # -------------------------------------------------

            entry_events = [
                item
                for item in self.vehicles[
                    vehicle_key
                ]
                if item["activity"] == "entering"
            ]

            # -------------------------------------------------
            # Repeated vehicle
            # -------------------------------------------------

            if len(entry_events) >= 2:

                events.append({

                    "event_type":
                        "repeated_vehicle",

                    "object_type":
                        "vehicle",

                    "color":
                        color,

                    "make":
                        make,

                    "model":
                        model,

                    "location":
                        observation["location"],

                    "first_seen":
                        entry_events[0]["timestamp"],

                    "last_seen":
                        entry_events[-1]["timestamp"],

                    "entry_count":
                        len(entry_events),

                    "message":
                        (
                            f"{color} {make} {model} "
                            f"entered {len(entry_events)} "
                            f"times."
                        )
                })

        return events