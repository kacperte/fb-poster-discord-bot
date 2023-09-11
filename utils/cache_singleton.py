class CacheSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CacheSingleton, cls).__new__(cls)
            cls._instance.cache = {}
        return cls._instance
