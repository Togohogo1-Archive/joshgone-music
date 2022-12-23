"""
Chants
"""

from yoyo import step

__depends__ = {'20210122_01_iH7wK-initial-tables'}

steps = [
    step("PRAGMA foreign_keys = ON;"),
    step(
        '''CREATE TABLE chants (
            server_id INTEGER,
            chant_name TEXT,
            chant_text TEXT,
            UNIQUE (server_id, chant_name),
            FOREIGN KEY (server_id) REFERENCES server (server_id)
        );''',
        "DROP TABLE chants;",
    ),
]
