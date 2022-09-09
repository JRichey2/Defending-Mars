import json


class Settings:
    def __init__(self):
        with open("settings.json", "r") as f:
            object.__setattr__(self, "_settings", json.loads(f.read()))

    def __setattr__(self, name, value):
        s = object.__getattribute__(self, "_settings")
        s[name.lower()] = value
        with open("settings.json", "w") as f:
            f.write(json.dumps(self._settings, indent=2))

    def __getattr__(self, name):
        return object.__getattribute__(self, "_settings")[name.lower()]


settings = Settings()
