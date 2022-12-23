"""
Chant owners
"""

from yoyo import step

__depends__ = {'20210301_01_Rnr8T-chants'}

steps = [
    step(
        "ALTER TABLE chants ADD COLUMN owner_id INTEGER;",
        "ALTER TABLE chants DROP COLUMN owner_id;",
    ),
]
