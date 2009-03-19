"""Error handling stuff."""


class MKRoestiError(Exception):
    """Runtime error triggered by mkroesti."""

    def __init__(self, message):
        self.message = message
