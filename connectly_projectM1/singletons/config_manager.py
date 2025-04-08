class ConfigManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.settings = {
            "DEFAULT_PAGE_SIZE": 20,
            "ENABLE_LOGGING": True,
            "POST_METADATA_REQUIRED": False
        }

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value