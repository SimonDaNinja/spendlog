from presenter import BasicPresenter
from ledger import Ledger
from counterParty import CounterPartyDataBase
import datetime
import specificBudget

from parser import Parser

if __name__ == '__main__':
    specificBudget.populateCounterPartyDatabase()
    parser = Parser()
    parser.parse("raw_input.txt")
    format = "%Y-%m-%d"
    start = datetime.datetime.strptime("2025-01-24", format)
    end = datetime.datetime.strptime("2025-02-24", format)
    BasicPresenter(start, end).present()