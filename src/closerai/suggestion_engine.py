import json
from collections import defaultdict

class SuggestionEngine:
    def __init__(self, path="config/suggestions.json"):
        with open(path, encoding="utf-8") as f:
            self.map = json.load(f)
        # track which keyword was already suggested, to avoid repeats
        self.suggested = set()
        # track per-keyword cycling index
        self.indexes = defaultdict(int)

    def get(self, transcript: str):
        """Return one suggestion for the first matching keyword in transcript."""
        t = transcript.lower()
        for kw, messages in self.map.items():
            if kw in t and kw not in self.suggested:
                # pick the next message in rotation
                idx = self.indexes[kw] % len(messages)
                suggestion = messages[idx]
                self.indexes[kw] += 1
                self.suggested.add(kw)
                return suggestion
        return None
