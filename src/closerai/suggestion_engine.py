import json
from pathlib import Path
from typing import Optional

class SuggestionEngine:
    def __init__(self, config_path: str = "config/triggers.json"):
        self.config_file = Path(config_path)
        self.triggers: dict[str, str] = {}
        self._last_mtime: float = 0.0
        self._load()  # initial load

    def _load(self):
        """Read the JSON file into memory."""
        if not self.config_file.exists():
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            self.config_file.write_text("{}")
        data = json.loads(self.config_file.read_text())
        # normalize keys to lowercase
        self.triggers = {k.lower(): v for k, v in data.items()}
        self._last_mtime = self.config_file.stat().st_mtime

    def _maybe_reload(self):
        """Reload if the file has been modified since last load."""
        try:
            mtime = self.config_file.stat().st_mtime
        except FileNotFoundError:
            mtime = 0.0
        if mtime > self._last_mtime:
            self._load()

    def get(self, text: str) -> Optional[str]:
        """
        Return the first matching trigger suggestion, reloading
        the config if it’s changed since last time.
        """
        self._maybe_reload()
        txt = text.lower()
        for keyword, suggestion in self.triggers.items():
            if keyword in txt:
                return suggestion
        return None
