from ledger import Ledger
from counterParty import CounterPartyDataBase
import datetime

DATE_TIME_FORMAT = "%Y-%m-%d"

LINES_PER_TRANSACTION = 9

ALIAS_INDEX = 0
TRANSACTION_DATE_INDEX = 2
LIQUIDITY_CHANGE_INDEX = 6

class Parser:
    def __init__(self):
        pass

    def parse(self, filename):
        content = self.readFile(filename)
        lines = content.split('\n')
        nLines = len(lines)
        i = 0
        while i < nLines:
            transactionLines = lines[i:i+LINES_PER_TRANSACTION]
            self.parseTransactionLines(transactionLines)
            i += LINES_PER_TRANSACTION

    def readFile(self, filename):
        with open(filename, 'r', encoding='utf-8') as fp:
            return fp.read()

    def parseTransactionLines(self, transactionLines):
        alias = transactionLines[ALIAS_INDEX]
        rawTransactionDate = transactionLines[TRANSACTION_DATE_INDEX]
        rawLiquidityChange = transactionLines[LIQUIDITY_CHANGE_INDEX]

        counterParty = CounterPartyDataBase().getCounterParty(alias)
        transactionDate = datetime.datetime.strptime(rawTransactionDate, DATE_TIME_FORMAT)
        liquidityChange = int(rawLiquidityChange.replace(' ','').split(',')[0])

        Ledger().addTransaction(liquidityChange = liquidityChange,
                                counterParty = counterParty,
                                date = transactionDate)
        