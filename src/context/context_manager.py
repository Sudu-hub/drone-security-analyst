from dataclasses import dataclass
from typing import Optional


@dataclass
class ActiveContext:
    """
    Represents an ongoing activity detected
    across multiple frames.
    """

    object_type: str

    location: str

    activity: str

    first_seen: str

    last_seen: str

    frame_count: int = 1

    color: Optional[str] = None

    make: Optional[str] = None

    model: Optional[str] = None

    # Prevent repeated alerts for the same event
    loitering_alerted: bool = False


class ContextManager:
    """
    Maintains temporal context across
    consecutive video frames.
    """

    def __init__(
        self,
        loitering_threshold_seconds: int = 5
    ):

        self.loitering_threshold_seconds = (
            loitering_threshold_seconds
        )

        # Active objects/events currently being tracked
        self.active_contexts = {}

    # =========================================================
    # PROCESS OBSERVATION
    # =========================================================

    def process_observation(
        self,
        observation: dict
    ) -> list:

        events = []

        timestamp = observation["timestamp"]

        location = observation["location"]

        objects = observation.get(
            "objects",
            []
        )

        for obj in objects:

            context_key = self._build_context_key(
                obj,
                location
            )

            existing_context = (
                self.active_contexts.get(
                    context_key
                )
            )

            # -------------------------------------------------
            # New object
            # -------------------------------------------------

            if existing_context is None:

                context = self._create_context(
                    obj=obj,
                    timestamp=timestamp,
                    location=location
                )

                self.active_contexts[
                    context_key
                ] = context

            # -------------------------------------------------
            # Existing object
            # -------------------------------------------------

            else:

                self._update_context(
                    context=existing_context,
                    obj=obj,
                    timestamp=timestamp
                )

                event = (
                    self._detect_temporal_event(
                        existing_context
                    )
                )

                if event is not None:

                    events.append(event)

        return events

    # =========================================================
    # CREATE CONTEXT
    # =========================================================

    def _create_context(
        self,
        obj: dict,
        timestamp: str,
        location: str
    ) -> ActiveContext:

        return ActiveContext(

            object_type=obj.get(
                "type",
                "unknown"
            ),

            location=location,

            activity=obj.get(
                "activity",
                "unknown"
            ),

            first_seen=timestamp,

            last_seen=timestamp,

            frame_count=1,

            color=obj.get(
                "color"
            ),

            make=obj.get(
                "make"
            ),

            model=obj.get(
                "model"
            )
        )

    # =========================================================
    # UPDATE CONTEXT
    # =========================================================

    def _update_context(
        self,
        context: ActiveContext,
        obj: dict,
        timestamp: str
    ):

        context.last_seen = timestamp

        context.frame_count += 1

        activity = obj.get(
            "activity"
        )

        if activity:

            context.activity = activity

    # =========================================================
    # BUILD CONTEXT KEY
    # =========================================================

    def _build_context_key(
        self,
        obj: dict,
        location: str
    ) -> str:

        return "|".join(
            [
                obj.get(
                    "type",
                    "unknown"
                ),

                obj.get(
                    "color"
                ) or "unknown",

                obj.get(
                    "make"
                ) or "unknown",

                obj.get(
                    "model"
                ) or "unknown",

                location
            ]
        )

    # =========================================================
    # TEMPORAL EVENT DETECTION
    # =========================================================

    def _detect_temporal_event(
        self,
        context: ActiveContext
    ) -> Optional[dict]:

        duration = (
            self._calculate_duration(
                context.first_seen,
                context.last_seen
            )
        )

        # -----------------------------------------------------
        # Person loitering rule
        # -----------------------------------------------------

        if (
            context.object_type == "person"

            and context.activity
            in [
                "standing",
                "walking"
            ]

            and duration >=
            self.loitering_threshold_seconds

            and not context.loitering_alerted
        ):

            # Mark this context as already alerted
            context.loitering_alerted = True

            return {

                "event_type": "loitering",

                "object_type":
                    context.object_type,

                "location":
                    context.location,

                "first_seen":
                    context.first_seen,

                "last_seen":
                    context.last_seen,

                "duration_seconds":
                    duration,

                "frame_count":
                    context.frame_count
            }

        return None

    # =========================================================
    # CALCULATE TIME DIFFERENCE
    # =========================================================

    @staticmethod
    def _calculate_duration(
        start: str,
        end: str
    ) -> int:

        start_seconds = (
            ContextManager
            ._timestamp_to_seconds(start)
        )

        end_seconds = (
            ContextManager
            ._timestamp_to_seconds(end)
        )

        return max(
            0,
            end_seconds - start_seconds
        )

    # =========================================================
    # TIMESTAMP → SECONDS
    # =========================================================

    @staticmethod
    def _timestamp_to_seconds(
        timestamp: str
    ) -> int:

        parts = timestamp.split(":")

        if len(parts) != 2:

            raise ValueError(
                f"Invalid timestamp: {timestamp}"
            )

        minutes = int(
            parts[0]
        )

        seconds = int(
            parts[1]
        )

        return (
            minutes * 60
            + seconds
        )

    # =========================================================
    # CLEANUP EXPIRED CONTEXTS
    # =========================================================

    def cleanup_contexts(
        self,
        current_timestamp: str,
        max_gap_seconds: int = 5
    ):

        expired_contexts = []

        for key, context in list(
            self.active_contexts.items()
        ):

            gap = (
                self._calculate_duration(
                    context.last_seen,
                    current_timestamp
                )
            )

            # If object hasn't appeared for
            # more than max_gap_seconds,
            # close its context.
            if gap > max_gap_seconds:

                expired_contexts.append(
                    context
                )

                del self.active_contexts[
                    key
                ]

        return expired_contexts

    # =========================================================
    # GET ACTIVE CONTEXTS
    # =========================================================

    def get_active_contexts(self):

        return list(
            self.active_contexts.values()
        )

    # =========================================================
    # CLEAR ALL CONTEXT
    # =========================================================

    def clear(self):

        self.active_contexts.clear()