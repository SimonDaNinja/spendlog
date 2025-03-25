from spendlog.ledger import Ledger
from spendlog.loggingProvider import LoggingProvider
logging = LoggingProvider().logging
import datetime

DATE_TIME_FORMAT = "%Y-%m-%d"

LINES_PER_TRANSACTION = 9

ALIAS_INDEX = 0
TRANSACTION_DATE_INDEX = 2
LIQUIDITY_CHANGE_INDEX = 6

class Parser:
    def __init__(self):
        logging.info(f"This function has not been implemented in the parser class '{type(self).__name__}'!")

    def parseFromFilename(self, filename):
        logging.warning(f"This function has not been implemented in the parser class '{type(self).__name__}'!")

    def parse(self, content):
        logging.warning(f"This function has not been implemented in the parser class '{type(self).__name__}'!")

    def readFile(self, filename):
        logging.warning(f"This function has not been implemented in the parser class '{type(self).__name__}'!")

    def parseTransactionLines(self, transactionLines):
        logging.warning(f"This function has not been implemented in the parser class '{type(self).__name__}'!")

# This parser takes transaction data copy pasted in bulk directly from the
# browser in Swedbank's Internetbanken into a file. It is thus extremely dependent
# on being in this exact format. Unless you intend to use this project in this exact
# way, you are recommended to implement your own parser
class InternetbankenParser(Parser):
    def __init__(self):
        pass

    def parseFromFilename(self, filename):
        content = self.readFile(filename)
        self.parse(content)

    def parse(self, content):
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

        transactionDate = datetime.datetime.strptime(rawTransactionDate, DATE_TIME_FORMAT)
        liquidityChange = int(rawLiquidityChange.replace(' ','').split(',')[0])

        fingerPrint = hash('\n'.join(transactionLines))

        Ledger().addTransaction(liquidityChange = liquidityChange,
                                counterPartyAlias = alias,
                                date = transactionDate,
                                fingerPrint = fingerPrint)
