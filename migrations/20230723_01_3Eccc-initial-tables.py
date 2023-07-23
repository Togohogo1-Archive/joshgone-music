"""
Initial-tables
"""

from yoyo import step

__depends__ = {}

steps = [
    step("PRAGMA foreign_keys = ON;"),
    step(
        '''CREATE TABLE server (
            server_id INTEGER PRIMARY KEY
        );''',
        "DROP TABLE server;",
    ),
    step(
        '''CREATE TABLE playlists (
            server_id INTEGER,
            playlist_name TEXT,
            playlist_text TEXT,
            owner_id INTEGER,
            UNIQUE (server_id, playlist_name),
            FOREIGN KEY (server_id) REFERENCES server (server_id)
        );''',
        "DROP TABLE playlists;",
    )
]
