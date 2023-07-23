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
        '''CREATE TABLE chants (
            server_id INTEGER,
            chant_name TEXT,
            chant_text TEXT,
            owner_id INTEGER,  /* In order these features were added */
            UNIQUE (server_id, chant_name),
            FOREIGN KEY (server_id) REFERENCES server (server_id)
        );''',
        "DROP TABLE chants;",
    )
]
