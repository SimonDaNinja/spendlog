from counterParty import CounterPartyDataBase
import datetime
from typing import Hashable
from logger import Logger

class Transaction:

    def __hash__(self):
        return hash(self.fingerPrint)

    def __eq__(self, other):
        if self.fingerPrint is None or other.fingerPrint is None:
            return False
        return self.fingerPrint == other.fingerPrint

    def __str__(self):
        return f"Money spent: {self.liquidityChange}; Capital gain: {self.capitalChange}; Counter Party:{self.counterParty}; transaction date: {self.date}; tags: {self.tags}; category: {self.category}"

    def __repr__(self):
        return str(self)

    def __init__(self, liquidityChange = None, capitalChange = None, counterParty = None, tags = None, category = None, date = None, fingerPrint = None):
        parameters = [value for key, value in {**locals()}.items() if key != 'self']

        if liquidityChange is None:
            self.liquidityChange = 0
        else:
            self.liquidityChange = liquidityChange

        if capitalChange is None:
            self.capitalChange = 0
        else:
            self.capitalChange = capitalChange

        if tags is None:
            if counterParty is not None:
                self.tags = counterParty.tags
            else:
                tags = None
        else:
            self.tags = tags

        self.category = category
        if category is None:
            if counterParty is not None:
                self.category = counterParty.category
        if self.category is None:
            self.category = "uncategorized"

        if date is None:
            self.date = datetime.datetime.now()
        else:
            self.date = date

        if counterParty is None:
            self.counterParty = CounterPartyDataBase().getCounterParty("")
        else:
            self.counterParty = counterParty
            self.counterParty.transactionModifier(self)

        if fingerPrint is None:
            Logger().logging.warning("No explicit fingerprint provided. This is unexpected, but will calculate one based on input parameters.")
            self.fingerPrint = hash(tuple(x for x in parameters if isinstance(x, Hashable)))
        else:
            assert isinstance(fingerPrint, Hashable), "Transaction fingerprint must be hashable!"
            self.fingerPrint = fingerPrint


    def getLiquidityChange(self):
        return self.liquidityChange

    def getCapitalChange(self):
        return self.capitalChange

    def getNetChange(self):
        return self.liquidityChange + self.capitalChange

    def getCounterParty(self):
        return self.counterParty

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

    def setCounterParty(self, counterParty):
        self.counterParty = counterParty

    def setTags(self, tags):
        self.tags = tags

    def setCategory(self, category):
        self.category = category

    def setDate(self, date):
        self.date = date


