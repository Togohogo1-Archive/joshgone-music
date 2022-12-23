"""
Initial tables
"""

from yoyo import step

__depends__ = {}

steps = [
    step("PRAGMA foreign_keys = ON;"),
    step(
        '''CREATE TABLE server (
            server_id INTEGER PRIMARY KEY,
            running INTEGER
        );''',
        "DROP TABLE server;",
    ),
    step(
        '''CREATE TABLE removed_emoji (
            server_id INTEGER,
            emoji_id INTEGER,
            UNIQUE (server_id, emoji_id),
            FOREIGN KEY (server_id) REFERENCES server (server_id)
        );''',
        "DROP TABLE removed_emoji;",
    ),
    step(
        '''CREATE TABLE allowed_user (
            server_id INTEGER,
            user_id INTEGER,
            UNIQUE (server_id, user_id),
            FOREIGN KEY (server_id) REFERENCES server (server_id)
        );''',
        "DROP TABLE allowed_user;",
    ),
]
