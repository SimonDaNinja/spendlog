from spendlog.counterParty import CounterPartyDataBase
from spendlog.loggingProvider import LoggingProvider
logging = LoggingProvider().logging
import datetime
from typing import Hashable

class FingerprintMismatchError(Exception):
    pass

class Transaction:

    def __hash__(self):
        if self.fingerPrint is not None:
            return hash(self.fingerPrint)
        return hash((self.liquidityChange,
                     self.capitalChange,
                     self.counterPartyAlias,
                     self.date,
                     tuple(self.tags),
                     self.category))

    def __eq__(self, other):
        if self.fingerPrint is None or other.fingerPrint is None:
            return False
        if self.fingerPrint == other.fingerPrint:
            if self.liquidityChange != other.liquidityChange:
                raise FingerprintMismatchError(f"Fingerprint matches but liquidityChange differs! self: {self.liquidityChange}, other: {other.liquidityChange}")
            if self.capitalChange != other.capitalChange:
                raise FingerprintMismatchError(f"Fingerprint matches but capitalChange differs! self: {self.capitalChange}, other: {other.capitalChange}")
            if self.counterPartyAlias != other.counterPartyAlias:
                raise FingerprintMismatchError(f"Fingerprint matches but counterParty differs! self: {self.counterPartyAlias}, other: {other.counterPartyAlias}")
            if self.date != other.date:
                raise FingerprintMismatchError(f"Fingerprint matches but date differs! self: {self.date}, other: {other.date}")
            if self.tags != other.tags:
                raise FingerprintMismatchError(f"Fingerprint matches but tags differs! self: {self.tags}, other: {other.tags}")
            if self.category != other.category:
                raise FingerprintMismatchError(f"Fingerprint matches but category differs! self: {self.category}, other: {other.category}")
            return True
        return False

    def __str__(self):
        return f"Money spent: {self.liquidityChange}; Capital gain: {self.capitalChange}; Counter Party:{self.counterPartyAlias}; transaction date: {self.date}; tags: {self.tags}; category: {self.category}"

    def __repr__(self):
        return str(self)

    def __init__(self, liquidityChange = None, capitalChange = None, counterPartyAlias = None, tags = None, category = None, date = None, fingerPrint = None):
        if liquidityChange is None:
            self.liquidityChange = 0
        else:
            self.liquidityChange = liquidityChange

        if capitalChange is None:
            self.capitalChange = 0
        else:
            self.capitalChange = capitalChange

        if counterPartyAlias is None:
            counterPartyAlias = ""
        self.counterPartyAlias = counterPartyAlias

        if tags is None:
            self.tags = self.getCounterParty().tags
        else:
            self.tags = tags

        self.category = category
        if category is None:
            self.category = self.getCounterParty().category
        if self.category is None:
            self.category = "uncategorized"

        if date is None:
            self.date = datetime.datetime.now()
        else:
            self.date = date

        self.getCounterParty().transactionModifier(self)
        assert isinstance(fingerPrint, Hashable), "Transaction fingerprint must be hashable!"
        if fingerPrint is None:
            logging.warning("Instantiating transaction without fingerprint! This can be risky!")
        self.fingerPrint = fingerPrint


    def getLiquidityChange(self):
        return self.liquidityChange

    def getCapitalChange(self):
        return self.capitalChange

    def getNetChange(self):
        return self.liquidityChange + self.capitalChange

    def getCounterParty(self):
        return CounterPartyDataBase().getCounterParty(self.counterPartyAlias)

    def getTags(self):
        return self.tags

    def getCategory(self):
        return self.category

    def getDate(self):
        return self.date

    def setLiquidityChange(self, liquidityChange):
        self.liquidityChange = liquidityChange

    def setCapitalChange(self, capitalChange):
        self.capitalChange = capitalChange

    def setCounterPartyAlias(self, counterPartyAlias):
        self.counterPartyAlias = counterPartyAlias

    def setTags(self, tags):
        self.tags = tags

    def setCategory(self, category):
        self.category = category

    def setDate(self, date):
        self.date = date
