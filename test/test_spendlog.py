import unittest
from spendlog.loggingProvider import LoggingProvider
from spendlog.counterParty import CounterPartyDataBase
from spendlog.ledger import Ledger

logging = LoggingProvider().logging

class TestSpendlog(unittest.TestCase):

    def setUp(self):
        self.resetSingletons()
        logging.getLogger().setLevel(logging.DEBUG)

    def resetSingletons(self):
        Ledger().reset()
        CounterPartyDataBase().reset()