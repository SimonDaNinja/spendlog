from spendlog.transaction import Transaction, FingerprintMismatchError
from spendlog.loggingProvider import LoggingProvider
from spendlog.counterParty import CounterPartyDataBase
logging = LoggingProvider().logging

class TimeRange:
    def __init__(self, start, end):
        self.start = start
        self.end = end

class Ledger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        logging.everything(f"Ledger requested")
        if cls._instance is None:
            logging.debug(f"Initializing and returning new Ledger")
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls.transactionSet = set()
        else:
            logging.everything(f"Ledger already exists. Returning existing instance")
        return cls._instance

    @classmethod
    def reset(cls):
        logging.debug(f"Reset Ledger")
        cls._instance = None
        cls.transactionSet = set()

    def addTransaction(self, *args, **kwargs):
        newTransaction = Transaction(*args, **kwargs)
        try:
            if newTransaction in self.transactionSet:
                logging.warning("Transaction already exists!")
        except FingerprintMismatchError as e:
            logging.error(str(e) + "\nNote: Replacing old transaction with new to recover.")
            for oldTransaction in self.transactionSet:
                if hash(newTransaction) == hash(oldTransaction):
                    self.transactionSet.remove(oldTransaction)
                    break
        self.transactionSet.add(Transaction(*args, **kwargs))

    def getTransactions(self,
                 timeRange = None,
                 requiredCategory = None,
                 forbiddenCategory = None,
                 allowedCategories = None,
                 requiredTags = None,
                 forbiddenTags = None,
                 allowedTags = None,
                 requiredCounterParty = None,
                 forbiddenCounterParty = None,
                 allowedCounterParties = None) -> set[Transaction]:
        transactions = self.transactionSet.copy()
        transactions &= self.getAllTransactionsInTimeRange(timeRange)
        transactions &= self.getAllTransactionsWithCategory(requiredCategory)
        transactions &= self.getAllTransactionsWithoutCategory(forbiddenCategory)
        transactions &= self.getAllTransactionsInCategories(allowedCategories)
        transactions &= self.getAllTransactionsWithRequiredTags(requiredTags)
        transactions &= self.getAllTransactionsWithoutTags(forbiddenTags)
        transactions &= self.getAllTransactionsWithAllowedTags(allowedTags)
        transactions &= self.getAllTransactionsWithCounterParty(requiredCounterParty)
        transactions &= self.getAllTransactionsWithoutCounterParty(forbiddenCounterParty)
        transactions &= self.getAllTransactionsInCounterParties(allowedCounterParties)
        return transactions


    def getAllTransactionsInTimeRange(self, timeRange) -> list[Transaction]:
        if timeRange is None:
            return self.transactionSet.copy()
        return {transaction for transaction in self.transactionSet if timeRange.start <= transaction.getDate() <= timeRange.end}

    def getAllTransactionsWithCategory(self, category) -> list[Transaction]:
        if category is None:
            return self.transactionSet.copy()
        return {transaction for transaction in self.transactionSet if transaction.getCategory() == category}

    def getAllTransactionsWithoutCategory(self, category) -> list[Transaction]:
        if category is None:
            return self.transactionSet.copy()
        return {transaction for transaction in self.transactionSet if transaction.getCategory() != category}

    def getAllTransactionsInCategories(self, categories) -> list[Transaction]:
        if categories is None:
            return self.transactionSet.copy()
        return {transaction for transaction in self.transactionSet if transaction.getCategory() in categories}

    def getAllTransactionsWithRequiredTags(self, tags) -> list[Transaction]:
        if tags is None:
            return self.transactionSet.copy()
        return {transaction for transaction in self.transactionSet if self.isAllRequiredTagsPresentInTags(tags, transaction.tags)}

    def isAllRequiredTagsPresentInTags(self, requiredTags, tags) -> bool:
        for requiredTag in requiredTags:
            if requiredTag not in tags:
                return False
        return True

    def getAllTransactionsWithoutTags(self, tags) -> list[Transaction]:
        if tags is None:
            return self.transactionSet.copy()
        return {transaction for transaction in self.transactionSet if self.isNoForbiddenTagsPresentInTags(tags, transaction.tags)}

    def isNoForbiddenTagsPresentInTags(self, forbidenTags, tags) -> bool:
        for forbiddenTag in forbidenTags:
            if forbiddenTag in tags:
                return False
        return True

    def getAllTransactionsWithAllowedTags(self, tags) -> list[Transaction]:
        if tags is None:
            return self.transactionSet.copy()
        return {transaction for transaction in self.transactionSet if self.isAllTagsAllowed(tags, transaction.tags)}

    def isAllTagsAllowed(self, allowedTags, tags) -> bool:
        for tag in tags:
            if tag not in allowedTags:
                return False
        return True

    def getAllTransactionsWithCounterParty(self, counterPartyAlias) -> list[Transaction]:
        if counterPartyAlias is None:
            return self.transactionSet.copy()
        counterParty = CounterPartyDataBase().getCounterParty(counterPartyAlias)
        return {transaction for transaction in self.transactionSet if CounterPartyDataBase().getCounterParty(transaction.counterPartyAlias) == counterParty}

    def getAllTransactionsWithoutCounterParty(self, counterPartyAlias) -> list[Transaction]:
        if counterPartyAlias is None:
            return self.transactionSet.copy()
        counterParty = CounterPartyDataBase().getCounterParty(counterPartyAlias)
        return {transaction for transaction in self.transactionSet if CounterPartyDataBase().getCounterParty(transaction.counterPartyAlias) != counterParty}

    def getAllTransactionsInCounterParties(self, counterPartyAliases) -> list[Transaction]:
        if counterPartyAliases is None:
            return self.transactionSet.copy()
        counterParties = {CounterPartyDataBase().getCounterParty(counterPartyAlias) for counterPartyAlias in counterPartyAliases}
        return {transaction for transaction in self.transactionSet if CounterPartyDataBase().getCounterParty(transaction.counterPartyAlias) in counterParties}

    def getTotalLiquidityChange(self, *args, **kwargs) -> list[Transaction]:
        return sum([transaction.getLiquidityChange() for transaction in self.getTransactions(*args, **kwargs)])

    def getTotalCapitalChange(self, *args, **kwargs) -> list[Transaction]:
        return sum([transaction.getCapitalChange() for transaction in self.getTransactions(*args, **kwargs)])

    def getTotalNetChange(self, *args, **kwargs) -> list[Transaction]:
        return sum([transaction.getNetChange() for transaction in self.getTransactions(*args, **kwargs)])
