from test.test_spendlog import TestSpendlog
from spendlog.parser import InternetbankenParser
from spendlog.ledger import Ledger
from spendlog.transaction import Transaction

class TestParser(TestSpendlog):

    def testInternetbankenParser(self):
        parser = InternetbankenParser()
        parser.parseFromFilename("transactions_template.txt")

        fingerprint1 = hash("Systembolaget\n\n" +
                     "2025-03-25\n\n" +
                     "2025-03-25\n\n" +
                     "-100,00\n\n" +
                     "24 900,00")
        fingerprint2 = hash(
                     "ICA SUPERMARKET\n\n" +
                     "2025-03-24\n\n" +
                     "2025-03-24\n\n" +
                     "-300,00\n\n" +
                     "25 000,00")
        fingerprint3 = hash(
                     "SALARY SYSTEM\n\n" +
                     "2025-03-25\n\n" +
                     "2025-03-24\n\n" +
                     "25 000,00\n\n" +
                     "25 300,00")
        fingerprint4 = hash(
                     "Henkes Keba*\n\n" +
                     "2025-03-24\n\n" +
                     "2025-03-24\n\n" +
                     "-300,00\n\n" +
                     "300,00")

        expectedTransactions = {
            Transaction(-100, 0, "Systembolaget", None, "uncategorized", self.strToDateTime("2025-03-25"), fingerprint1),
            Transaction(-300, 0, "ICA SUPERMARKET", None, "uncategorized", self.strToDateTime("2025-03-24"), fingerprint2),
            Transaction(25000, 0, "SALARY SYSTEM", None, "uncategorized", self.strToDateTime("2025-03-25"), fingerprint3),
            Transaction(-300, 0, "Henkes Keba*", None, "uncategorized", self.strToDateTime("2025-03-24"), fingerprint4)
        }
        transactionsOnLedger = Ledger().getTransactions()
        self.assertEqual(expectedTransactions, transactionsOnLedger)