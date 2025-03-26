from spendlog.loggingProvider import LoggingProvider
logging = LoggingProvider().logging

class NameMismatchError(Exception):
    pass

class CounterParty:
    def __init__(self, name, tags = None, category = None, transactionModifier = None):
        self.name = name

        if tags is None:
            self.tags = set()
        else:
            self.tags = tags

        self.category = category

        if transactionModifier is not None:
            self.transactionModifier = transactionModifier
        else:
            self.transactionModifier = lambda x : None

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if self.name == other.name:
            errorString = ""
            if self.tags != other.tags:
                errorString += f"Name matches, but tags differs!\nself: {self.tags},\nother: {other.tags}"
            if self.category != other.category:
                errorString += f"Name matches, but category differs!\nself: {self.category},\nother: {other.category}"
            if self.transactionModifier != other.transactionModifier:
                errorString += f"Name matches, but transactionModifier differs!\nself: {self.transactionModifier},\nother: {other.transactionModifier}"
            if errorString:
                errorString += f"\n(for CounterParty: '{self.name}')"
                raise NameMismatchError(errorString)
            return True
        return False

    def __hash__(self):
        return hash(self.name)

class CounterPartyDataBase:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls.aliasToCounterPartyMap = dict()
            logging.debug(f"Initializing and returning new CounterPartyDataBase")
        else:
            logging.everything(f"CounterPartyDataBase already exists. Returning existing instance")
        return cls._instance

    @classmethod
    def reset(cls):
        cls.aliasToCounterPartyMap = dict()
        cls._instance = None
        logging.debug(f"Reset CounterPartyDataBase")

    def getCounterParty(self, alias):
        if alias not in self.aliasToCounterPartyMap:
            logging.info(f"'{alias}' is not in counter party database. Adding it")
            self.addCounterParty([alias])
        return self.aliasToCounterPartyMap[alias]

    def addCounterParty(self, aliases, *args, **kwargs):
        if not aliases:
            return
        for alias in aliases:
            if alias in self.aliasToCounterPartyMap:
                logging.warning(f"Adding counter party with alias '{alias}', which is already in the counter party database! The old alias will be replaced")
        name = aliases[0]
        counterParty = CounterParty(name, *args, **kwargs)
        for alias in aliases:
            self.aliasToCounterPartyMap[alias] = counterParty

    def getAllCounterParties(self):
        return set(self.aliasToCounterPartyMap.values())

    def getAllCounterPartyNames(self):
        return {party.name for party in set(self.aliasToCounterPartyMap.values())}

    def getAllCounterPartyAliases(self):
        return set(self.aliasToCounterPartyMap.keys())

