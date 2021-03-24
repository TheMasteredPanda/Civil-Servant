import json
import os

#Basic settings handler.
class Settings():
    def __init__(self, settings_path):
        self.path = settings_path
        if os.path.exists(settings_path) is False:
            with open(settings_path, 'w') as settings_file:
                json_raw = json.dumps({"punishments": {"muterole": None, "tempbanrole": None}})
                settings_file.write(json_raw)

        with open(settings_path, 'r') as settings_file:
            self.settings_json = json.loads(settings_file.read())

    def get(self):
        return self.settings_json

    def save(self):
        with open(self.path, 'w') as settings_file:
            settings_file.write(json.dumps(self.settings_json))

    def set(self, new_settings):
        self.settings_json = new_settings
