class AggregatedDataState:
    """
    Holds intermediate and aggregated data for use across multiple aggregation functions.
    Acts as a shared state container.
    """

    PROPORTIONAL_YIELDS_KEY = "proportional_yields"

    def __init__(self):
        self._state = {}

    def set(self, key, value):
        """Set a value in the state."""
        self._state[key] = value

    def get(self, key, default=None):
        """Get a value from the state."""
        return self._state.get(key, default)

    def has(self, key):
        """Check if a key exists in the state."""
        return key in self._state

    def update(self, **kwargs):
        """Update multiple values in the state."""
        self._state.update(kwargs)

    def remove(self, key):
        """Remove a key from the state."""
        self._state.pop(key, None)

    def clear(self):
        """Clear the entire state."""
        self._state.clear()
