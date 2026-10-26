"""Type aliases shared by scoring.py and ranking.py.

Not called types.py on purpose: that name would shadow Python's built-in
types module when a file in this folder is run directly.
"""

import uuid

StoryTags = dict[uuid.UUID, list[uuid.UUID]]  # story_id → that story's tag ids
TagScores = dict[uuid.UUID, float]            # tag_id → the user's score
