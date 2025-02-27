class CounterParty:
    def __init__(self, name, tags = None, category = None):
        self.name = name

        if tags is None:
            self.tags = set()
        else:
            self.tags = tags

        self.category = category

    def __str__(self):
        return self.name

class CounterPartyDataBase:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls.aliasToCounterPartyMap = dict()
        return cls._instance

    def getCounterParty(self, alias):
        if alias not in self.aliasToCounterPartyMap:
            self.addCounterParty([alias])
        return self.aliasToCounterPartyMap[alias]

    def addCounterParty(self, aliases, tags = None, category = None):
        if not aliases:
            return
        name = aliases[0]
        counterParty = CounterParty(name, tags, category)
        for alias in aliases:
            self.aliasToCounterPartyMap[alias] = counterParty
