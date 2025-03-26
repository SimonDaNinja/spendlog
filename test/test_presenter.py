from test.test_spendlog import TestSpendlog
from spendlog.parser import InternetbankenParser
from counterPartyDatabaseTemplate import populateCounterPartyDatabase
from spendlog.presenter import BasicPresenter
from unittest import mock
from unittest.mock import patch

class TestPresenter(TestSpendlog):

    @patch('builtins.print')
    def testBasicPresenter(self, mock_print):
        populateCounterPartyDatabase()
        InternetbankenParser().parseFromFilename("transactions_template.txt")
        BasicPresenter(self.strToDateTime("2025-03-25"), self.strToDateTime("2025-03-25")).present()

        calls = [
             mock.call("Summary of economy between 2025-03-25 00:00:00 and 2025-03-25 00:00:00"),
             mock.call("========================================================"),
             mock.call("Tags:"),
             mock.call("========================================================"),
             mock.call("Categories:"),
             mock.call("  alcohol:"),
             mock.call("    liquidity: -100"),
             mock.call("  salary:"),
             mock.call("    liquidity: 25000"),
             mock.call("========================================================"),
             mock.call("Counter Parties:"),
             mock.call("  Systembolaget:"),
             mock.call("    liquidity: -100"),
             mock.call("  Salary:"),
             mock.call("    liquidity: 25000"),
             mock.call("========================================================"),
             mock.call("Total:"),
             mock.call("  liquidity: 24900"),
             mock.call("  capital change: 0"),
             mock.call("  net change: 24900")]
        mock_print.assert_has_calls(calls)
        mock_print.reset_mock()

        calls = [
             mock.call("Summary of economy between 2025-03-25 00:00:00 and 2025-03-25 00:00:00"),
             mock.call("========================================================"),
             mock.call("Tags:"),
             mock.call("========================================================"),
             mock.call("Categories:"),
             mock.call("  alcohol:"),
             mock.call("    liquidity: -100"),
             mock.call("    capital change: 0"),
             mock.call("  salary:"),
             mock.call("    liquidity: 25000"),
             mock.call("    capital change: 0"),
             mock.call("========================================================"),
             mock.call("Counter Parties:"),
             mock.call("  Systembolaget:"),
             mock.call("    liquidity: -100"),
             mock.call("    capital change: 0"),
             mock.call("  Salary:"),
             mock.call("    liquidity: 25000"),
             mock.call("    capital change: 0"),
             mock.call("========================================================"),
             mock.call("Total:"),
             mock.call("  liquidity: 24900"),
             mock.call("  capital change: 0"),
             mock.call("  net change: 24900")]
        BasicPresenter(self.strToDateTime("2025-03-25"), self.strToDateTime("2025-03-25")).present(True)
        mock_print.assert_has_calls(calls)
        mock_print.reset_mock()

        calls = [
             mock.call("Summary of economy between 2025-03-25 00:00:00 and 2025-03-25 00:00:00"),
             mock.call("========================================================"),
             mock.call("All transactions:"),
             mock.call("  Money spent: -100; Capital gain: 0; Counter Party:Systembolaget; transaction date: 2025-03-25 00:00:00; tags: set(); category: alcohol"),
             mock.call("  Money spent: 25000; Capital gain: 0; Counter Party:Salary; transaction date: 2025-03-25 00:00:00; tags: set(); category: salary"),
             mock.call('========================================================'),
             mock.call("Tags:"),
             mock.call("========================================================"),
             mock.call("Categories:"),
             mock.call("  alcohol:"),
             mock.call("    liquidity: -100"),
             mock.call("  salary:"),
             mock.call("    liquidity: 25000"),
             mock.call("========================================================"),
             mock.call("Counter Parties:"),
             mock.call("  Systembolaget:"),
             mock.call("    liquidity: -100"),
             mock.call("  Salary:"),
             mock.call("    liquidity: 25000"),
             mock.call("========================================================"),
             mock.call("Total:"),
             mock.call("  liquidity: 24900"),
             mock.call("  capital change: 0"),
             mock.call("  net change: 24900")]
        BasicPresenter(self.strToDateTime("2025-03-25"), self.strToDateTime("2025-03-25")).present(False, True)
        mock_print.assert_has_calls(calls)
