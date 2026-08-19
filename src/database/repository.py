from .db import Database


class FrameRepository:
    """
    Handles persistence and querying of
    drone frames and detected objects.
    """

    def __init__(self, database: Database):

        self.database = database

    def save_observation(
        self,
        frame: dict,
        telemetry: dict,
        analysis: dict
    ):

        connection = self.database.get_connection()

        cursor = connection.cursor()

        # -----------------------------
        # Store frame
        # -----------------------------

        cursor.execute(
            """
            INSERT OR REPLACE INTO frames (
                frame_id,
                timestamp,
                location,
                altitude,
                latitude,
                longitude,
                description
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                frame["frame_id"],
                frame["timestamp"],
                telemetry.get("location"),
                telemetry.get("altitude"),
                telemetry.get("latitude"),
                telemetry.get("longitude"),
                frame["description"]
            )
        )

        # -----------------------------
        # Remove previous objects
        # -----------------------------

        cursor.execute(
            """
            DELETE FROM objects
            WHERE frame_id = ?
            """,
            (
                frame["frame_id"],
            )
        )

        # -----------------------------
        # Store detected objects
        # -----------------------------

        for obj in analysis.get("objects", []):

            cursor.execute(
                """
                INSERT INTO objects (
                    frame_id,
                    object_type,
                    color,
                    make,
                    model,
                    activity,
                    confidence
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    frame["frame_id"],
                    obj.get("type"),
                    obj.get("color"),
                    obj.get("make"),
                    obj.get("model"),
                    obj.get("activity"),
                    obj.get("confidence")
                )
            )

        connection.commit()
        connection.close()

    # --------------------------------
    # Query all frames
    # --------------------------------

    def get_all_frames(self):

        connection = self.database.get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM frames
            ORDER BY timestamp
            """
        )

        rows = cursor.fetchall()

        connection.close()

        return [dict(row) for row in rows]

    # --------------------------------
    # Query objects by type
    # --------------------------------

    def find_by_object_type(
        self,
        object_type: str
    ):

        connection = self.database.get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                f.frame_id,
                f.timestamp,
                f.location,
                f.description,
                o.object_type,
                o.color,
                o.make,
                o.model,
                o.activity,
                o.confidence

            FROM frames f

            JOIN objects o
                ON f.frame_id = o.frame_id

            WHERE o.object_type = ?

            ORDER BY f.timestamp
            """,
            (
                object_type,
            )
        )

        rows = cursor.fetchall()

        connection.close()

        return [dict(row) for row in rows]

    # --------------------------------
    # Query by make
    # --------------------------------

    def find_by_make(
        self,
        make: str
    ):

        connection = self.database.get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                f.frame_id,
                f.timestamp,
                f.location,
                o.object_type,
                o.color,
                o.make,
                o.model,
                o.activity,
                o.confidence

            FROM frames f

            JOIN objects o
                ON f.frame_id = o.frame_id

            WHERE LOWER(o.make) = LOWER(?)

            ORDER BY f.timestamp
            """,
            (
                make,
            )
        )

        rows = cursor.fetchall()

        connection.close()

        return [dict(row) for row in rows]

    # --------------------------------
    # Query by time
    # --------------------------------

    def find_by_time(
        self,
        start_time: str,
        end_time: str
    ):

        connection = self.database.get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                f.frame_id,
                f.timestamp,
                f.location,
                o.object_type,
                o.color,
                o.make,
                o.model,
                o.activity,
                o.confidence

            FROM frames f

            LEFT JOIN objects o
                ON f.frame_id = o.frame_id

            WHERE f.timestamp >= ?
              AND f.timestamp <= ?

            ORDER BY f.timestamp
            """,
            (
                start_time,
                end_time
            )
        )

        rows = cursor.fetchall()

        connection.close()

        return [dict(row) for row in rows]