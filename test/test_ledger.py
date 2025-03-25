import unittest
import datetime

from spendlog.ledger import Ledger, TimeRange
from spendlog.counterParty import CounterPartyDataBase
from spendlog.loggingProvider import LoggingProvider
from spendlog.transaction import Transaction, FingerprintMismatchError

logging = LoggingProvider().logging

initList = list()

class TestLedger(unittest.TestCase):
    def setUp(self):
        self.previousFingerprint = 0
        Ledger().reset()
        CounterPartyDataBase().reset()
        logging.getLogger().setLevel(logging.DEBUG)

    def getNewFingerPrint(self):
        self.previousFingerprint += 1
        return self.previousFingerprint

    def strToDateTime(self, string):
        return datetime.datetime.strptime(string, "%Y-%m-%d")

    def testInitializeLedger(self):
        a = Ledger()
        b = a
        c = Ledger()

        # ledger is a singleton, so each instance should be identical
        self.assertIs(a, b)
        self.assertIs(b, c)
        self.assertIs(a, c)
        self.assertIs(Ledger(), Ledger())

    def testAddTransaction(self):
        liquidityChange = 1
        capitalChange = 2
        alias = "alias"
        tags = []
        category = "booze"
        date = self.strToDateTime("2025-01-24")
        fingerprint = hash(None)

        # add transaction and double check that it is added to the ledger
        lenBeforeAdding = len(Ledger().transactionSet)
        Ledger().addTransaction(liquidityChange, capitalChange, alias, tags, category, date, fingerprint)
        lenAfterAdding = len(Ledger().transactionSet)

        self.assertEqual(lenBeforeAdding + 1, lenAfterAdding)

        self.assertTrue(Transaction(liquidityChange, capitalChange, alias, tags, category, date, fingerprint) in Ledger().transactionSet)

        # add the same transaction again and check that it has not been added twice
        lenBeforeAdding = len(Ledger().transactionSet)
        Ledger().addTransaction(liquidityChange, capitalChange, alias, tags, category, date, fingerprint)
        lenAfterAdding = len(Ledger().transactionSet)

        self.assertEqual(lenBeforeAdding, lenAfterAdding)

        self.assertTrue(Transaction(liquidityChange, capitalChange, alias, tags, category, date, fingerprint) in Ledger().transactionSet)

        # add identical transaction, except with new fingerprint, check that it has been added, and has not replaced the old
        newFingerPrint = hash(1)
        lenBeforeAdding = len(Ledger().transactionSet)
        Ledger().addTransaction(liquidityChange, capitalChange, alias, tags, category, date, newFingerPrint)
        lenAfterAdding = len(Ledger().transactionSet)

        self.assertEqual(lenBeforeAdding + 1, lenAfterAdding)

        self.assertTrue(Transaction(liquidityChange, capitalChange, alias, tags, category, date, fingerprint) in Ledger().transactionSet)
        self.assertTrue(Transaction(liquidityChange, capitalChange, alias, tags, category, date, newFingerPrint) in Ledger().transactionSet)

        # add transaction, with same fingerprint but new data (this is an error, but there is error handling and it will not crash the program),
        # check that it has replaced the old
        newAlias = "new alias"

        lenBeforeAdding = len(Ledger().transactionSet)
        with self.assertRaises(FingerprintMismatchError):
            Transaction(liquidityChange, capitalChange, newAlias, tags, category, date, fingerprint) in Ledger().transactionSet

        Ledger().addTransaction(liquidityChange, capitalChange, newAlias, tags, category, date, fingerprint)
        lenAfterAdding = len(Ledger().transactionSet)

        self.assertEqual(lenBeforeAdding, lenAfterAdding)

        self.assertTrue(Transaction(liquidityChange, capitalChange, newAlias, tags, category, date, fingerprint) in Ledger().transactionSet)
        with self.assertRaises(FingerprintMismatchError):
            self.assertTrue(Transaction(liquidityChange, capitalChange, alias, tags, category, date, fingerprint) in Ledger().transactionSet)

    def testResetLedger(self):
        liquidityChange = 1
        capitalChange = 2
        alias = "alias"
        tags = []
        category = "booze"
        date = self.strToDateTime("2025-01-24")
        fingerprint1 = hash(None)
        fingerprint2 = hash(1)

        # add two transactions to the ledger
        lenBeforeAdding = len(Ledger().transactionSet)
        self.assertEqual(lenBeforeAdding, 0)

        Ledger().addTransaction(liquidityChange, capitalChange, alias, tags, category, date, fingerprint1)
        Ledger().addTransaction(liquidityChange, capitalChange, alias, tags, category, date, fingerprint2)

        lenAfterAdding = len(Ledger().transactionSet)
        self.assertEqual(lenAfterAdding, 2)

        # reset the ledger
        Ledger().reset()

        lenAfterResetting = len(Ledger().transactionSet)
        self.assertEqual(lenAfterResetting, 0)

    def testGetAllTransactionsInTimeRange(self):
        kwargs1 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 1", "tag 2"],
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-01-24"),       #NOTE: in the range
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction1 = Transaction(**kwargs1)
        Ledger().addTransaction(**kwargs1)
        kwargs2 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 1", "tag 2"],
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-01-14"),       #NOTE: in the range
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction2 = Transaction(**kwargs2)
        Ledger().addTransaction(**kwargs2)
        kwargs3 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 1", "tag 2"],
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-03-14"),       #NOTE: NOT in the range
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction3 = Transaction(**kwargs3)
        Ledger().addTransaction(**kwargs3)
        kwargs4 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 1", "tag 2"],
            "category"            : "booze",
            "date"                : self.strToDateTime("2024-01-14"),       #NOTE: NOT in the range
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction4 = Transaction(**kwargs4)
        Ledger().addTransaction(**kwargs4)
        timeRange = TimeRange(self.strToDateTime("2025-01-10"),
                              self.strToDateTime("2025-01-25"))
        transactionsInRange = Ledger().getAllTransactionsInTimeRange(timeRange)

        self.assertTrue(transaction1 in transactionsInRange)
        self.assertTrue(transaction2 in transactionsInRange)
        self.assertFalse(transaction3 in transactionsInRange)
        self.assertFalse(transaction4 in transactionsInRange)

    def testGetAllTransactionsWithCategory(self):
        kwargs1 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 1", "tag 2"],
            "category"            : "booze",                            # NOTE: has the category
            "date"                : self.strToDateTime("2025-01-24"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction1 = Transaction(**kwargs1)
        Ledger().addTransaction(**kwargs1)
        kwargs2 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 1", "tag 2"],
            "category"            : "booze",                            # NOTE: has the category
            "date"                : self.strToDateTime("2025-01-24"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction2 = Transaction(**kwargs2)
        Ledger().addTransaction(**kwargs2)
        kwargs3 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 1", "tag 2"],
            "category"            : None,                               # NOTE: does NOT have the category
            "date"                : self.strToDateTime("2025-01-24"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction3 = Transaction(**kwargs3)
        Ledger().addTransaction(**kwargs3)
        kwargs4 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 1", "tag 2"],
            "category"            : "weed",                             # NOTE: does NOT have the category
            "date"                : self.strToDateTime("2025-01-24"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction4 = Transaction(**kwargs4)
        Ledger().addTransaction(**kwargs4)
        transactionsWithCategory = Ledger().getAllTransactionsWithCategory("booze")

        self.assertTrue(transaction1 in transactionsWithCategory)
        self.assertTrue(transaction2 in transactionsWithCategory)
        self.assertFalse(transaction3 in transactionsWithCategory)
        self.assertFalse(transaction4 in transactionsWithCategory)

    def testGetAllTransactionsWithoutCategory(self):
        kwargs1 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 1", "tag 2"],
            "category"            : "booze",                            # NOTE: has the category
            "date"                : self.strToDateTime("2025-01-24"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction1 = Transaction(**kwargs1)
        Ledger().addTransaction(**kwargs1)
        kwargs2 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 1", "tag 2"],
            "category"            : "booze",                            # NOTE: has the category
            "date"                : self.strToDateTime("2025-01-24"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction2 = Transaction(**kwargs2)
        Ledger().addTransaction(**kwargs2)
        kwargs3 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 1", "tag 2"],
            "category"            : None,                               # NOTE: does NOT have the category
            "date"                : self.strToDateTime("2025-01-24"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction3 = Transaction(**kwargs3)
        Ledger().addTransaction(**kwargs3)
        kwargs4 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 1", "tag 2"],
            "category"            : "weed",                             # NOTE: does NOT have the category
            "date"                : self.strToDateTime("2025-01-24"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction4 = Transaction(**kwargs4)
        Ledger().addTransaction(**kwargs4)
        transactionsWithoutCategory = Ledger().getAllTransactionsWithoutCategory("booze")

        self.assertFalse(transaction1 in transactionsWithoutCategory)
        self.assertFalse(transaction2 in transactionsWithoutCategory)
        self.assertTrue(transaction3 in transactionsWithoutCategory)
        self.assertTrue(transaction4 in transactionsWithoutCategory)

    def testGetAllTransactionsInCategories(self):
        kwargs1 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 1", "tag 2"],
            "category"            : "booze",                            # NOTE: has one of the specified categories
            "date"                : self.strToDateTime("2025-01-24"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction1 = Transaction(**kwargs1)
        Ledger().addTransaction(**kwargs1)
        kwargs2 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 1", "tag 2"],
            "category"            : "weed",                             # NOTE: has one of the specified categories
            "date"                : self.strToDateTime("2025-01-24"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction2 = Transaction(**kwargs2)
        Ledger().addTransaction(**kwargs2)
        kwargs3 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 1", "tag 2"],
            "category"            : None,                               # NOTE: does NOT have one of the specified categories
            "date"                : self.strToDateTime("2025-01-24"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction3 = Transaction(**kwargs3)
        Ledger().addTransaction(**kwargs3)
        kwargs4 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 1", "tag 2"],
            "category"            : "cake",                             # NOTE: does NOT have one of the specified categories
            "date"                : self.strToDateTime("2025-01-24"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction4 = Transaction(**kwargs4)
        Ledger().addTransaction(**kwargs4)
        transactionsInCategories = Ledger().getAllTransactionsInCategories(["booze", "weed"])

        self.assertTrue(transaction1 in transactionsInCategories)
        self.assertTrue(transaction2 in transactionsInCategories)
        self.assertFalse(transaction3 in transactionsInCategories)
        self.assertFalse(transaction4 in transactionsInCategories)

    def testGetAllTransactionsWithRequiredTags(self):
        kwargs1 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 1", "tag 2", "tag 3"],        # NOTE: has all specified tags
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-01-24"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction1 = Transaction(**kwargs1)
        Ledger().addTransaction(**kwargs1)
        kwargs2 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 2", "tag 3", "tag 4"],        # NOTE: has all specified tags
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-01-24"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction2 = Transaction(**kwargs2)
        Ledger().addTransaction(**kwargs2)
        kwargs3 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 3", "tag 4", "tag 5"],        # NOTE: only has one specified tag
            "category"            : None,
            "date"                : self.strToDateTime("2025-01-24"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction3 = Transaction(**kwargs3)
        Ledger().addTransaction(**kwargs3)
        kwargs4 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 4", "tag 5", "tag 6"],        # NOTE: has no specified tag
            "category"            : "weed",
            "date"                : self.strToDateTime("2025-01-24"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction4 = Transaction(**kwargs4)
        Ledger().addTransaction(**kwargs4)
        transactionsWithRequiredTags = Ledger().getAllTransactionsWithRequiredTags(["tag 2", "tag 3"])

        self.assertTrue(transaction1 in transactionsWithRequiredTags)
        self.assertTrue(transaction2 in transactionsWithRequiredTags)
        self.assertFalse(transaction3 in transactionsWithRequiredTags)
        self.assertFalse(transaction4 in transactionsWithRequiredTags)

    def testGetAllTransactionsWithoutTags(self):
        kwargs1 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 1", "tag 2"],                 # NOTE: has no specified tags
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-01-24"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction1 = Transaction(**kwargs1)
        Ledger().addTransaction(**kwargs1)
        kwargs2 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 2", "tag 3"],                 # NOTE: has no specified tags
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-01-14"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction2 = Transaction(**kwargs2)
        Ledger().addTransaction(**kwargs2)
        kwargs3 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 3", "tag 4"],                 # NOTE: only has one specified tag
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-03-14"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction3 = Transaction(**kwargs3)
        Ledger().addTransaction(**kwargs3)
        kwargs4 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 4", "tag 5"],                 # NOTE: has all specified tag
            "category"            : "booze",
            "date"                : self.strToDateTime("2024-01-14"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction4 = Transaction(**kwargs4)
        Ledger().addTransaction(**kwargs4)
        transactionsWithoutTags = Ledger().getAllTransactionsWithoutTags(["tag 4", "tag 5"])

        self.assertTrue(transaction1 in transactionsWithoutTags)
        self.assertTrue(transaction2 in transactionsWithoutTags)
        self.assertFalse(transaction3 in transactionsWithoutTags)
        self.assertFalse(transaction4 in transactionsWithoutTags)

    def testGetAllTransactionsWithAllowedTags(self):
        kwargs1 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 2"],                 # NOTE: only has allowed tags (one of them)
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-01-24"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction1 = Transaction(**kwargs1)
        Ledger().addTransaction(**kwargs1)
        kwargs2 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 2", "tag 3"],                 # NOTE: only has allowed tags (both of them)
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-01-14"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction2 = Transaction(**kwargs2)
        Ledger().addTransaction(**kwargs2)
        kwargs3 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 3", "tag 4"],                 # NOTE: has one allowed tag and one disallowed
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-03-14"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction3 = Transaction(**kwargs3)
        Ledger().addTransaction(**kwargs3)
        kwargs4 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 4", "tag 5"],                 # NOTE: only has disallowed tags
            "category"            : "booze",
            "date"                : self.strToDateTime("2024-01-14"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction4 = Transaction(**kwargs4)
        Ledger().addTransaction(**kwargs4)
        transactionsWithAllowedTags = Ledger().getAllTransactionsWithAllowedTags(["tag 2", "tag 3"])

        self.assertTrue(transaction1 in transactionsWithAllowedTags)
        self.assertTrue(transaction2 in transactionsWithAllowedTags)
        self.assertFalse(transaction3 in transactionsWithAllowedTags)
        self.assertFalse(transaction4 in transactionsWithAllowedTags)

    def testGetAllTransactionsWithCounterParty(self):
        kwargs1 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 1","tag 2"],
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-01-24"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction1 = Transaction(**kwargs1)
        Ledger().addTransaction(**kwargs1)
        kwargs2 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 2", "tag 3"],
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-01-14"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction2 = Transaction(**kwargs2)
        Ledger().addTransaction(**kwargs2)
        kwargs3 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias2",
            "tags"                : ["tag 3", "tag 4"],
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-03-14"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction3 = Transaction(**kwargs3)
        Ledger().addTransaction(**kwargs3)
        transactionsWithCounterParty = Ledger().getAllTransactionsWithCounterParty("alias")

        self.assertTrue(transaction1 in transactionsWithCounterParty)
        self.assertTrue(transaction2 in transactionsWithCounterParty)
        self.assertFalse(transaction3 in transactionsWithCounterParty)

    def testGetAllTransactionsWithoutCounterParty(self):
        kwargs1 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 1","tag 2"],
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-01-24"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction1 = Transaction(**kwargs1)
        Ledger().addTransaction(**kwargs1)
        kwargs2 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 2", "tag 3"],
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-01-14"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction2 = Transaction(**kwargs2)
        Ledger().addTransaction(**kwargs2)
        kwargs3 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias2",
            "tags"                : ["tag 3", "tag 4"],
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-03-14"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction3 = Transaction(**kwargs3)
        Ledger().addTransaction(**kwargs3)
        transactionsWithCounterParty = Ledger().getAllTransactionsWithoutCounterParty("alias2")

        self.assertTrue(transaction1 in transactionsWithCounterParty)
        self.assertTrue(transaction2 in transactionsWithCounterParty)
        self.assertFalse(transaction3 in transactionsWithCounterParty)

    def testGetAllTransactionsInCounterParties(self):
        kwargs1 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 1","tag 2"],
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-01-24"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction1 = Transaction(**kwargs1)
        Ledger().addTransaction(**kwargs1)
        kwargs2 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias2",
            "tags"                : ["tag 2", "tag 3"],
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-01-14"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction2 = Transaction(**kwargs2)
        Ledger().addTransaction(**kwargs2)
        kwargs3 = {
            "liquidityChange"     : 1,
            "capitalChange"       : 2,
            "counterPartyAlias"   : "alias3",
            "tags"                : ["tag 3", "tag 4"],
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-03-14"),
            "fingerPrint"         : self.getNewFingerPrint()}
        transaction3 = Transaction(**kwargs3)
        Ledger().addTransaction(**kwargs3)
        transactionsWithCounterParty = Ledger().getAllTransactionsInCounterParties(["alias", "alias2"])

        self.assertTrue(transaction1 in transactionsWithCounterParty)
        self.assertTrue(transaction2 in transactionsWithCounterParty)
        self.assertFalse(transaction3 in transactionsWithCounterParty)

    def testTotalGetters(self):
        liquidityChanges = [123,572,53]
        capitalChanges = [89, 432, 6545]

        kwargs1 = {
            "liquidityChange"     : liquidityChanges[0],
            "capitalChange"       : capitalChanges[0],
            "counterPartyAlias"   : "alias",
            "tags"                : ["tag 1","tag 2"],
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-01-24"),
            "fingerPrint"         : self.getNewFingerPrint()}
        Ledger().addTransaction(**kwargs1)
        kwargs2 = {
            "liquidityChange"     : liquidityChanges[1],
            "capitalChange"       : capitalChanges[1],
            "counterPartyAlias"   : "alias2",
            "tags"                : ["tag 2", "tag 3"],
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-01-14"),
            "fingerPrint"         : self.getNewFingerPrint()}
        Ledger().addTransaction(**kwargs2)
        kwargs3 = {
            "liquidityChange"     : liquidityChanges[2],
            "capitalChange"       : capitalChanges[2],
            "counterPartyAlias"   : "alias3",
            "tags"                : ["tag 3", "tag 4"],
            "category"            : "booze",
            "date"                : self.strToDateTime("2025-03-14"),
            "fingerPrint"         : self.getNewFingerPrint()}
        Ledger().addTransaction(**kwargs3)

        self.assertEqual(Ledger().getTotalLiquidityChange(), sum(liquidityChanges))
        self.assertEqual(Ledger().getTotalCapitalChange(), sum(capitalChanges))
        self.assertEqual(Ledger().getTotalNetChange(), sum(capitalChanges) + sum(liquidityChanges))