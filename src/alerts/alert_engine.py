from typing import Optional


class AlertEngine:
    """
    Converts detected security events into
    actionable security alerts.
    """

    def __init__(self):

        self.rules = [
            self._loitering_rule,
            self._restricted_vehicle_rule,
            self._repeated_vehicle_rule,
        ]

    # =========================================================
    # MAIN ALERT PROCESSOR
    # =========================================================

    def process_event(
        self,
        event: dict
    ) -> Optional[dict]:

        for rule in self.rules:

            alert = rule(event)

            if alert is not None:

                return alert

        return None

    # =========================================================
    # RULE 1 — PERSON LOITERING
    # =========================================================

    def _loitering_rule(
        self,
        event: dict
    ) -> Optional[dict]:

        if event.get("event_type") != "loitering":

            return None

        return {
            "alert_type": "PERSON_LOITERING",
            "severity": "HIGH",
            "location": event["location"],
            "message": (
                f"Person loitering at "
                f"{event['location']} "
                f"for "
                f"{event['duration_seconds']} seconds."
            ),
            "first_seen": event["first_seen"],
            "last_seen": event["last_seen"],
            "frame_count": event["frame_count"],
        }

    # =========================================================
    # RULE 2 — RESTRICTED VEHICLE
    # =========================================================

    def _restricted_vehicle_rule(
        self,
        event: dict
    ) -> Optional[dict]:

        if event.get("event_type") != "restricted_vehicle":

            return None

        return {
            "alert_type": "RESTRICTED_VEHICLE",
            "severity": "HIGH",
            "location": event["location"],
            "message": (
                f"Vehicle detected in restricted "
                f"area at {event['location']}."
            ),
            "first_seen": event["first_seen"],
            "last_seen": event["last_seen"],
            "frame_count": event["frame_count"],
        }

    # =========================================================
    # RULE 3 — REPEATED VEHICLE
    # =========================================================

    def _repeated_vehicle_rule(
        self,
        event: dict
    ) -> Optional[dict]:

        if event.get("event_type") != "repeated_vehicle":

            return None

        vehicle = (
            f"{event.get('color', '')} "
            f"{event.get('make', '')} "
            f"{event.get('model', '')}"
        ).strip()

        return {
            "alert_type": "REPEATED_VEHICLE",
            "severity": "MEDIUM",
            "location": event["location"],
            "message": (
                f"{vehicle} observed multiple times "
                f"at {event['location']}."
            ),
            "first_seen": event["first_seen"],
            "last_seen": event["last_seen"],
            "frame_count": event["frame_count"],
        }