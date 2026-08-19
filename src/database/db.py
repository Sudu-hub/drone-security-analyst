import sqlite3
from pathlib import Path


class Database:
    """
    SQLite database manager for the Drone Security Analyst.
    """

    def __init__(self, db_path: str = "data/drone_security.db"):

        self.db_path = Path(db_path)

        # Make sure data directory exists
        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    def get_connection(self):

        connection = sqlite3.connect(
            self.db_path
        )

        # Allows us to access columns by name
        connection.row_factory = sqlite3.Row

        # Enforce foreign keys
        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        return connection

    def initialize(self):

        connection = self.get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS frames (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                frame_id INTEGER NOT NULL UNIQUE,

                timestamp TEXT NOT NULL,

                location TEXT,

                altitude REAL,

                latitude REAL,

                longitude REAL,

                description TEXT,

                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS objects (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                frame_id INTEGER NOT NULL,

                object_type TEXT NOT NULL,

                color TEXT,

                make TEXT,

                model TEXT,

                activity TEXT,

                confidence REAL,

                FOREIGN KEY (frame_id)
                    REFERENCES frames(frame_id)
                    ON DELETE CASCADE
            )
            """
        )

        # Useful indexes
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_frames_timestamp
            ON frames(timestamp)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_frames_location
            ON frames(location)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_objects_type
            ON objects(object_type)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_objects_make
            ON objects(make)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_objects_activity
            ON objects(activity)
            """
        )

        connection.commit()
        connection.close()